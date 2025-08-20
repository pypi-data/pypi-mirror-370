from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple
import re
import json

try:
    from .regexes import (
        BLOCK_REGEX,
        COMMENT_REGEX,
        EXTENDS_REGEX,
        INCLUDE_REGEX,
        MIXIN_REGEX,
        SUPER_REGEX,
        VAR_REGEX,
    )
except ImportError:
    from regexes import (
        BLOCK_REGEX,
        COMMENT_REGEX,
        EXTENDS_REGEX,
        INCLUDE_REGEX,
        MIXIN_REGEX,
        SUPER_REGEX,
        VAR_REGEX,
    )

try:
    from .utils import (
        Vars,
        apply_global_whitespace_control,
        apply_tag_trimming,
        dedent_text,
        evaluate_condition,
        get_path,
        normalize_list,
        parse_with_object,
    )
except ImportError:
    from utils import (
        Vars,
        apply_global_whitespace_control,
        apply_tag_trimming,
        dedent_text,
        evaluate_condition,
        get_path,
        normalize_list,
        parse_with_object,
    )


@dataclass
class WhitespaceOptions:
    trimBlocks: bool = True
    lstripBlocks: bool = True
    dedentBlocks: bool = True


@dataclass
class Prompt:
    content: str
    usedFiles: List[str]


ResolvePath = Callable[[str, str, Callable[[str], str]], str]
LoadFile = Callable[[str], str]
EnsureExtension = Callable[[str], str]


@dataclass
class RendererOptions:
    baseDir: str = ""
    strictPaths: bool = True
    maxDepth: int = 20
    whitespace: Optional[WhitespaceOptions] = None
    resolvePath: Optional[ResolvePath] = None
    loadFile: Optional[Callable[[str], str]] = None
    ensureExtension: Optional[EnsureExtension] = None


@dataclass
class _RenderContext:
    vars: Vars
    currentDir: str
    usedFiles: set[str]
    depth: int


@dataclass
class _RenderOptionsInternal:
    noExtends: bool = False


class YAPLRenderer:
    def __init__(self, opts: Optional[RendererOptions] = None) -> None:
        if opts is None:
            opts = RendererOptions()
        self.baseDir = opts.baseDir
        self.strictPaths = opts.strictPaths
        self.maxDepth = opts.maxDepth
        self.whitespace = opts.whitespace if opts.whitespace is not None else WhitespaceOptions()
        self._resolvePath = opts.resolvePath
        self._loadFile = opts.loadFile
        self._ensureExtension = (
            opts.ensureExtension
            if opts.ensureExtension is not None
            else (lambda p: p if p.endswith(".yapl") else f"{p}.yapl")
        )

    @property
    def loadFile(self):
        return self._loadFile

    @property
    def resolvePath(self):
        return self._resolvePath

    @property
    def ensureExtension(self):
        return self._ensureExtension

    def setBaseDir(self, dir: str) -> None:
        self.baseDir = dir

    def renderString(self, templateSource: str, vars: Optional[Vars] = None, currentDir: Optional[str] = None) -> Prompt:
        if vars is None:
            vars = {}
        usedFiles: set[str] = set()
        rendered = self._processTemplate(
            templateSource,
            _RenderContext(vars=vars, currentDir=currentDir or self.baseDir, usedFiles=usedFiles, depth=0),
        )
        return Prompt(content=rendered, usedFiles=list(usedFiles))

    # Core processing
    def _processTemplate(self, templateSource: str, context: _RenderContext, options: Optional[_RenderOptionsInternal] = None) -> str:
        if options is None:
            options = _RenderOptionsInternal()
        if context.depth > self.maxDepth:
            raise RuntimeError("Max template depth exceeded (possible recursion).")
        processed = apply_tag_trimming(templateSource)
        processed = apply_global_whitespace_control(
            processed, self.whitespace.trimBlocks, self.whitespace.lstripBlocks
        )
        processed = re.sub(COMMENT_REGEX, "", processed)

        # extends
        if not options.noExtends:
            m = re.search(EXTENDS_REGEX, processed)
            if m:
                return self._processTemplateInheritance(processed, context, m.group(1))

        cleaned = processed
        for rx in (EXTENDS_REGEX, MIXIN_REGEX):
            cleaned = re.sub(rx, "", cleaned)
        processed_includes = self._processDirectives(
            cleaned, context, INCLUDE_REGEX, self._processIncludeDirective
        )
        processed_blocks = self._processStandaloneBlocks(processed_includes, context)
        processed_ifs = self._processIfElseStatements(processed_blocks, context)
        processed_fors = self._processForLoops(processed_ifs, context)
        cleaned_super = re.sub(SUPER_REGEX, "", processed_fors)
        return self._processVariableInterpolation(cleaned_super, context.vars)

    def _processTemplateInheritance(self, childTemplate: str, context: _RenderContext, parentTemplatePath: str) -> str:
        parentAbs = self._resolveTemplatePath(parentTemplatePath, context.currentDir)
        parentContent = self._loadTemplateFile(parentAbs)
        context.usedFiles.add(parentAbs)
        parentBlocks = self._extractBlockDefinitions(parentContent)
        mixinBlocks = self._collectBlocksFromMixins(childTemplate, context)
        childBlocks = self._extractBlockDefinitions(childTemplate)
        mixinEnhancedBlocks = self._mergeBlocksWithSuper(mixinBlocks, parentBlocks)
        finalBlocks = self._mergeBlocksWithSuper(childBlocks, mixinEnhancedBlocks)
        return self._applyBlockOverridesToParent(
            parentContent,
            finalBlocks,
            _RenderContext(vars=context.vars, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1),
            context.currentDir,
        )

    # Directive utilities
    def _processDirectives(self, content: str, context: _RenderContext, regex: Pattern[str], processor: Callable[[re.Match, _RenderContext], str]) -> str:
        # We need to iteratively apply because replacements can change positions.
        def repl(m: re.Match) -> str:
            return processor(m, context)
        return re.sub(regex, repl, content)

    def _processIncludeDirective(self, m: re.Match, context: _RenderContext) -> str:
        templatePath = m.group(1)
        withClause = m.group(2)
        abs_path = self._resolveTemplatePath(templatePath, context.currentDir)
        includeContent = self._loadTemplateFile(abs_path)
        context.usedFiles.add(abs_path)
        localVars = parse_with_object(withClause, context.vars) if withClause else {}
        mergedVars = {**context.vars, **localVars}
        return self._processTemplate(includeContent, _RenderContext(vars=mergedVars, currentDir=self._dirname(abs_path), usedFiles=context.usedFiles, depth=context.depth + 1))

    # Blocks
    def _processStandaloneBlocks(self, content: str, context: _RenderContext) -> str:
        def repl(m: re.Match) -> str:
            blockContent = m.group(2)
            processedContent = (
                dedent_text(blockContent) if self.whitespace.dedentBlocks else blockContent
            )
            return self._processTemplate(processedContent, _RenderContext(vars=context.vars, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
        return re.sub(BLOCK_REGEX, repl, content)

    def _extractBlockDefinitions(self, content: str) -> Dict[str, str]:
        blocks: Dict[str, str] = {}
        for m in re.finditer(BLOCK_REGEX, content):
            name = m.group(1)
            blockContent = m.group(2)
            processedContent = dedent_text(blockContent) if self.whitespace.dedentBlocks else blockContent
            blocks[name] = processedContent
        return blocks

    def _collectBlocksFromMixins(self, templateContent: str, context: _RenderContext) -> Dict[str, str]:
        collected: Dict[str, str] = {}
        mixins = list(re.finditer(MIXIN_REGEX, templateContent))
        if not mixins:
            return collected
        for mixinMatch in mixins:
            paths = normalize_list(mixinMatch.group(1))
            for p in paths:
                abs_path = self._resolveTemplatePath(p, context.currentDir)
                mixinContent = self._loadTemplateFile(abs_path)
                context.usedFiles.add(abs_path)
                blocks = self._extractBlockDefinitions(mixinContent)
                collected.update(blocks)
        return collected

    def _mergeBlocksWithSuper(self, incoming: Dict[str, str], base: Dict[str, str]) -> Dict[str, str]:
        merged = dict(base)
        for name, content in incoming.items():
            baseContent = base.get(name, "")
            merged[name] = re.sub(SUPER_REGEX, baseContent, content)
        return merged

    # If / Else processing
    def _processIfElseStatements(self, content: str, context: _RenderContext) -> str:
        # Iteratively find innermost if blocks and replace
        max_iterations = 50
        iteration = 0
        while iteration < max_iterations:
            new_content = self._processSingleIf(content, context)
            if new_content == content:
                break
            content = new_content
            iteration += 1
        return content

    def _processSingleIf(self, content: str, context: _RenderContext) -> str:
        m = re.search(r"\{%-?\s*if\s+([^%]+?)\s*-?%\}", content)
        if not m:
            return content
        if_start = m.start()
        initial_condition = m.group(1)
        endif_index, blocks = self._findMatchingEndif(content, if_start)
        if endif_index == -1:
            return content
        replacement = ""
        condition_met = False
        if evaluate_condition(initial_condition, context.vars):
            processed = dedent_text(blocks["if"]) if self.whitespace.dedentBlocks else blocks["if"]
            replacement = self._processTemplate(processed, _RenderContext(vars=context.vars, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
            condition_met = True
        if not condition_met:
            for cond, block_content in blocks.get("elif", []):
                if evaluate_condition(cond, context.vars):
                    processed = dedent_text(block_content) if self.whitespace.dedentBlocks else block_content
                    replacement = self._processTemplate(processed, _RenderContext(vars=context.vars, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
                    condition_met = True
                    break
        if not condition_met and blocks.get("else") is not None:
            processed = dedent_text(blocks["else"]) if self.whitespace.dedentBlocks else blocks["else"]
            replacement = self._processTemplate(processed, _RenderContext(vars=context.vars, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
        endif_end = content.find("%}", endif_index) + 2
        full_if_stmt = content[if_start:endif_end]
        return content.replace(full_if_stmt, replacement)

    def _findMatchingEndif(self, content: str, if_start: int):
        depth = 0
        blocks: List[Dict[str, Any]] = []
        pos = content.find("%}", if_start) + 2
        if_tag_end = pos
        # scan
        while pos < len(content):
            m = re.search(r"\{%-?\s*(if|elseif|else|endif)", content[pos:])
            if not m:
                break
            tag_start = pos + m.start()
            tag_type = m.group(1)
            if tag_type == "if":
                depth += 1
                pos = content.find("%}", tag_start) + 2
            elif tag_type == "elseif" and depth == 0:
                mm = re.search(r"\{%-?\s*elseif\s+([^%]+?)\s*-?%\}", content[tag_start:])
                if mm:
                    condition = mm.group(1)
                    elseif_end = content.find("%}", tag_start) + 2
                    blocks.append({"type": "elseif", "condition": condition, "start": tag_start, "end": elseif_end})
                    pos = elseif_end
                else:
                    pos = content.find("%}", tag_start) + 2
            elif tag_type == "else" and depth == 0:
                else_end = content.find("%}", tag_start) + 2
                blocks.append({"type": "else", "start": tag_start, "end": else_end})
                pos = else_end
            elif tag_type == "endif":
                if depth == 0:
                    endif_idx = tag_start
                    # build blocks
                    current_pos = if_tag_end
                    elif_blocks: List[Tuple[str, str]] = []
                    if_content = ""
                    else_content: Optional[str] = None
                    if not blocks:
                        if_content = content[if_tag_end:endif_idx]
                    else:
                        if_content = content[if_tag_end:blocks[0]["start"]]
                        for i, b in enumerate(blocks):
                            next_start = blocks[i + 1]["start"] if i + 1 < len(blocks) else endif_idx
                            block_content = content[b["end"]:next_start]
                            if b["type"] == "elseif" and "condition" in b:
                                elif_blocks.append((b["condition"], block_content))
                            elif b["type"] == "else":
                                else_content = block_content
                    return endif_idx, {"if": if_content, "elif": elif_blocks, "else": else_content}
                depth -= 1
                pos = content.find("%}", tag_start) + 2
            else:
                pos = content.find("%}", tag_start) + 2
        return -1, {"if": "", "elif": [], "else": None}

    # For loops
    def _processForLoops(self, content: str, context: _RenderContext) -> str:
        max_iterations = 50
        iteration = 0
        while iteration < max_iterations:
            new_content = self._processSingleFor(content, context)
            if new_content == content:
                break
            content = new_content
            iteration += 1
        return content

    def _evaluateIterableExpression(self, expr: str, vars: Vars) -> List[Any]:
        if re.match(r"^[a-zA-Z0-9_.]+$", expr):
            value = get_path(vars, expr)
            if value is None:
                return []
            if not isinstance(value, list):
                raise RuntimeError(f"For loop iterable must be an array, got: {type(value).__name__}")
            return value
        if expr.startswith("[") and expr.endswith("]"):
            try:
                parsed = json.loads(expr)
                if not isinstance(parsed, list):
                    raise RuntimeError(f"For loop iterable must be an array, got: {type(parsed).__name__}")
                return parsed
            except Exception as e:
                # Fallback manual split similar to TS
                items: List[Any] = []
                inner = expr[1:-1]
                if not inner.strip():
                    return []
                for item in inner.split(","):
                    t = item.strip()
                    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                        items.append(t[1:-1])
                    else:
                        try:
                            num = float(t) if "." in t else int(t)
                            items.append(num)
                        except Exception:
                            items.append(t)
                return items
        value = get_path(vars, expr)
        if value is None:
            return []
        if not isinstance(value, list):
            raise RuntimeError(f"For loop iterable must be an array, got: {type(value).__name__}")
        return value

    def _processSingleFor(self, content: str, context: _RenderContext) -> str:
        m = re.search(r"\{%-?\s*for\s+([a-zA-Z0-9_]+)\s+in\s+([^%]+?)\s*-?%\}", content)
        if not m:
            return content
        for_start = m.start()
        iterator_var = m.group(1)
        iterable_expr = m.group(2).strip()
        endfor_index, for_content = self._findMatchingEndfor(content, for_start)
        if endfor_index == -1:
            return content
        replacement = ""
        iterable_value = self._evaluateIterableExpression(iterable_expr, context.vars)
        for item in iterable_value:
            loop_ctx = _RenderContext(vars={**context.vars, iterator_var: item}, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1)
            processed = dedent_text(for_content) if self.whitespace.dedentBlocks else for_content
            rendered = self._processTemplate(processed, loop_ctx, _RenderOptionsInternal(noExtends=True))
            replacement += rendered
        endfor_end = content.find("%}", endfor_index) + 2
        full_for_stmt = content[for_start:endfor_end]
        return content.replace(full_for_stmt, replacement)

    def _findMatchingEndfor(self, content: str, for_start: int):
        depth = 0
        pos = content.find("%}", for_start) + 2
        while pos < len(content):
            m = re.search(r"\{%-?\s*(for|endfor)", content[pos:])
            if not m:
                break
            tag_start = pos + m.start()
            tag_type = m.group(1)
            if tag_type == "for":
                depth += 1
                pos = content.find("%}", tag_start) + 2
            elif tag_type == "endfor":
                if depth == 0:
                    for_tag_end = content.find("%}", for_start) + 2
                    for_content = content[for_tag_end:tag_start]
                    return tag_start, for_content
                depth -= 1
                pos = content.find("%}", tag_start) + 2
        return -1, ""

    # Variables
    def _processVariableInterpolation(self, templateContent: str, vars: Vars) -> str:
        def repl(m: re.Match) -> str:
            variablePath = m.group(1)
            defaultValue = m.group(2) if m.group(2) is not None else m.group(3)
            value = get_path(vars, variablePath)
            if value is None:
                return defaultValue or ""
            return str(value)
        return re.sub(VAR_REGEX, repl, templateContent)

    def _applyBlockOverridesToParent(self, parentContent: str, blockOverrides: Dict[str, str], context: _RenderContext, childDir: str) -> str:
        processed = parentContent
        processed_names: set[str] = set()
        for m in re.finditer(BLOCK_REGEX, parentContent):
            full = m.group(0)
            name = m.group(1)
            parentBlockContent = m.group(2)
            processed_names.add(name)
            rendered_parent = self._processTemplate(parentBlockContent, _RenderContext(vars=context.vars, currentDir=context.currentDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
            if name in blockOverrides:
                override_with_super = re.sub(SUPER_REGEX, rendered_parent, blockOverrides[name])
                blockReplacement = self._processTemplate(override_with_super, _RenderContext(vars=context.vars, currentDir=childDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
            else:
                blockReplacement = rendered_parent
            processed = processed.replace(full, blockReplacement)
        processed = self._processTemplate(processed, context, _RenderOptionsInternal(noExtends=True))
        child_only: List[str] = []
        for name, content in blockOverrides.items():
            if name not in processed_names:
                rendered = self._processTemplate(content, _RenderContext(vars=context.vars, currentDir=childDir, usedFiles=context.usedFiles, depth=context.depth + 1), _RenderOptionsInternal(noExtends=True))
                child_only.append(rendered)
        if child_only:
            processed += "\n" + "\n".join(child_only)
        return processed

    # Loader/Resolver
    def _resolveTemplatePath(self, templateRef: str, fromDir: str) -> str:
        if not self._resolvePath:
            raise RuntimeError("No resolvePath provided. File-based operations are not available in this environment.")
        ensured = self._ensureExtension(templateRef)
        return self._resolvePath(ensured, fromDir, self._ensureExtension)

    def _loadTemplateFile(self, absolutePath: str) -> str:
        if not self._loadFile:
            raise RuntimeError("No loadFile provided. File-based operations are not available in this environment.")
        return self._loadFile(absolutePath)

    def _dirname(self, p: str) -> str:
        p2 = p.replace("\\", "/")
        idx = p2.rfind("/")
        return p2[:idx] if idx >= 0 else ""
