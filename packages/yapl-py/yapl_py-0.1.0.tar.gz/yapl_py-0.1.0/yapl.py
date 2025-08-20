from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import os
try:
    from .renderer import YAPLRenderer, RendererOptions, WhitespaceOptions, Prompt
except ImportError:
    from renderer import YAPLRenderer, RendererOptions, WhitespaceOptions, Prompt

Vars = Dict[str, Any]


@dataclass
class YAPLOptions:
    baseDir: str | List[str]
    cache: Optional[bool] = None
    strictPaths: Optional[bool] = None
    maxDepth: Optional[int] = None
    whitespace: Optional[WhitespaceOptions] = None
    resolvePath: Optional[Callable[[str, str, Callable[[str], str]], str]] = None
    loadFile: Optional[Callable[[str], str]] = None
    ensureExtension: Optional[Callable[[str], str]] = None


class YAPL:
    def __init__(self, opts: YAPLOptions) -> None:
        input_bases = opts.baseDir if isinstance(opts.baseDir, list) else [opts.baseDir]
        self.baseDirs: List[str] = [self._normalize_path(p) for p in input_bases]
        # remove aliases from baseDirs but keep for remotes
        local_bases = [b for b in self.baseDirs if not b.startswith("@")]
        self.baseDir = local_bases[0] if local_bases else (self.baseDirs[0] if self.baseDirs else "")
        self.remoteAliases: Dict[str, str] = {}
        if any(b == "@awesome-yapl" for b in input_bases):
            self.remoteAliases["@awesome-yapl"] = (
                "https://raw.githubusercontent.com/yapl-language/awesome-yapl/main/prompts"
            )
        hasRemote = any(
            b.startswith("http://") or b.startswith("https://") or b == "@awesome-yapl" for b in input_bases
        )

        def ensure_ext_default(p: str) -> str:
            return p if p.endswith(".yapl") else p + ".yapl"

        def default_resolve(templateRef: str, fromDir: str, ensureExt: Callable[[str], str]) -> str:
            # Renderer applies ensureExt before calling us; treat templateRef as final
            ref = templateRef
            # alias -> remote
            for alias, baseUrl in self.remoteAliases.items():
                if ref.startswith(alias + "/"):
                    rest = ref[len(alias) + 1 :]
                    return f"{baseUrl}/{rest}"
            # URL passthrough
            if ref.startswith("http://") or ref.startswith("https://"):
                return ref
            # relative
            if ref.startswith("./") or ref.startswith("../"):
                return os.path.normpath(os.path.join(fromDir, ref))
            # search across baseDirs last one wins
            for i in range(len(local_bases) - 1, -1, -1):
                baseI = local_bases[i]
                if not baseI:
                    continue
                candidate = os.path.normpath(os.path.join(baseI, ref))
                if os.path.exists(candidate):
                    return candidate
            # fallback: resolve from fromDir
            return os.path.normpath(os.path.join(fromDir, ref))

        def default_load(absolutePath: str) -> str:
            if absolutePath.startswith("http://") or absolutePath.startswith("https://"):
                import urllib.request
                with urllib.request.urlopen(absolutePath) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"Failed to fetch {absolutePath}: {resp.status}")
                    return resp.read().decode("utf-8")
            with open(absolutePath, "r", encoding="utf-8") as f:
                return f.read()

        renderer_opts = RendererOptions(
            baseDir=self.baseDir,
            strictPaths=True if opts.strictPaths is None else opts.strictPaths,
            maxDepth=opts.maxDepth if opts.maxDepth is not None else 20,
            whitespace=opts.whitespace if opts.whitespace is not None else WhitespaceOptions(),
            resolvePath=opts.resolvePath if opts.resolvePath is not None else default_resolve,
            loadFile=opts.loadFile if opts.loadFile is not None else default_load,
            ensureExtension=opts.ensureExtension if opts.ensureExtension is not None else ensure_ext_default,
        )
        self.renderer = YAPLRenderer(renderer_opts)

    def setBaseDir(self, dir: str) -> None:
        self.baseDir = self._normalize_path(dir)
        self.renderer.setBaseDir(self.baseDir)

    def dirname(self, filePath: str) -> str:
        return os.path.dirname(filePath).replace("\\", "/")

    def renderString(self, templateSource: str, vars: Optional[Vars] = None, currentDir: Optional[str] = None) -> Prompt:
        return self.renderer.renderString(templateSource, vars or {}, currentDir or self.baseDir)

    def render(self, templatePath: str, vars: Optional[Vars] = None) -> Prompt:
        if self.renderer.loadFile is None:
            raise RuntimeError(
                "File loading is not available. Provide a loadFile function in YAPLOptions or use renderString.")
        absolutePath = (
            self.renderer.resolvePath(templatePath, self.baseDir, self.renderer.ensureExtension)
            if self.renderer.resolvePath is not None
            else templatePath
        )
        templateContent = self.renderer._loadTemplateFile(absolutePath)
        templateDir = self.dirname(absolutePath)
        return self.renderString(templateContent, vars or {}, templateDir)

    def _normalize_path(self, p: str) -> str:
        return p.replace("\\", "/").replace("//", "/")
