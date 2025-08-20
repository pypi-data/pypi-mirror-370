from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import re

Vars = Dict[str, Any]


def get_path(obj: Vars, dotted: str) -> Any:
    cur: Any = obj
    for key in dotted.split("."):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def normalize_list(list_literal: str) -> List[str]:
    # Extract values inside double quotes
    return re.findall(r'"([^"]+)"', list_literal)


def parse_with_object(literal: str, parent_vars: Vars) -> Vars:
    # Similar to TS parseWithObject: parses a JSON-like object allowing bare identifiers to reference vars
    inner = literal.strip()
    if inner.startswith("{") and inner.endswith("}"):
        inner = inner[1:-1]
    if not inner.strip():
        return {}

    # Split on commas not inside quotes
    parts: List[str] = []
    cur = ""
    in_str: Optional[str] = None
    esc = False
    for ch in inner:
        if in_str:
            if esc:
                cur += ch
                esc = False
                continue
            if ch == "\\":
                cur += ch
                esc = True
                continue
            if ch == in_str:
                in_str = None
                cur += ch
                continue
            cur += ch
            continue
        if ch in ('"', "'"):
            in_str = ch
            cur += ch
            continue
        if ch == ",":
            parts.append(cur.strip())
            cur = ""
            continue
        cur += ch
    if cur.strip():
        parts.append(cur.strip())

    tokens: List[tuple[str, str]] = []
    for p in parts:
        m = re.match(r"^\s*(\"?)([A-Za-z0-9_.-]+)\1\s*:\s*(.+)\s*$", p)
        if not m:
            continue
        key = m.group(2)
        raw = m.group(3)
        tokens.append((key, raw))

    out: Vars = {}
    for k, v in tokens:
        trimmed = v.strip()
        if (trimmed.startswith('"') and trimmed.endswith('"')) or (
            trimmed.startswith("'") and trimmed.endswith("'")
        ):
            out[k] = trimmed[1:-1]
            continue
        if re.match(r"^-?\d+(\.\d+)?$", trimmed):
            out[k] = float(trimmed) if "." in trimmed else int(trimmed)
            continue
        if trimmed == "true":
            out[k] = True
            continue
        if trimmed == "false":
            out[k] = False
            continue
        if trimmed == "null":
            out[k] = None
            continue
        out[k] = get_path(parent_vars, trimmed)
    return out


def parse_value(expr: str, vars: Vars) -> Any:
    trimmed = expr.strip()
    if (trimmed.startswith('"') and trimmed.endswith('"')) or (
        trimmed.startswith("'") and trimmed.endswith("'")
    ):
        return trimmed[1:-1]
    if re.match(r"^-?\d+(\.\d+)?$", trimmed):
        return float(trimmed) if "." in trimmed else int(trimmed)
    if trimmed == "true":
        return True
    if trimmed == "false":
        return False
    if trimmed == "null":
        return None
    return get_path(vars, trimmed)


def evaluate_condition(condition: str, vars: Vars) -> bool:
    trimmed = condition.strip()
    # and/or
    m = re.match(r"^(.+?)\s+and\s+(.+)$", trimmed)
    if m:
        return evaluate_condition(m.group(1).strip(), vars) and evaluate_condition(
            m.group(2).strip(), vars
        )
    m = re.match(r"^(.+?)\s+or\s+(.+)$", trimmed)
    if m:
        return evaluate_condition(m.group(1).strip(), vars) or evaluate_condition(
            m.group(2).strip(), vars
        )

    m = re.match(r"^(.+?)\s+is\s+(not\s+)?defined$", trimmed)
    if m:
        value = get_path(vars, m.group(1).strip())
        is_def = value is not None
        return (not is_def) if m.group(2) else is_def

    m = re.match(r"^(.+?)\s+is\s+(not\s+)?empty$", trimmed)
    if m:
        value = get_path(vars, m.group(1).strip())
        is_empty = (
            value is None
            or value == ""
            or (isinstance(value, list) and len(value) == 0)
            or (isinstance(value, dict) and len(value) == 0)
        )
        return (not is_empty) if m.group(2) else is_empty

    m = re.match(r"^(.+?)\s*(>=|<=|==|!=|>|<)\s*(.+)$", trimmed)
    if m:
        left = parse_value(m.group(1).strip(), vars)
        op = m.group(2)
        right = parse_value(m.group(3).strip(), vars)
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == ">=":
            return float(left) >= float(right)
        if op == "<=":
            return float(left) <= float(right)
        if op == ">":
            return float(left) > float(right)
        if op == "<":
            return float(left) < float(right)
        return False

    if trimmed == "true":
        return True
    if trimmed == "false":
        return False

    if re.match(r"^[a-zA-Z0-9_.]+$", trimmed):
        value = get_path(vars, trimmed)
        return bool(value)
    return False


def dedent_text(text: str) -> str:
    # Remove leading and trailing single blank lines and dedent by min indent
    s = re.sub(r"^\n", "", text)
    s = re.sub(r"\n\s*$", "", s)
    lines = s.split("\n")
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return text
    def get_leading_ws_len(line: str) -> int:
        m = re.match(r"^[ \t]*", line)
        return len(m.group(0)) if m else 0
    min_indent = min(get_leading_ws_len(ln) for ln in non_empty)
    return "\n".join(ln[min_indent:] for ln in lines)


def apply_tag_trimming(source: str) -> str:
    result = source
    result = re.sub(r"[ \t]*\{\{-", "{{", result)
    result = re.sub(r"-\}\}[ \t]*\r?\n?", "}}", result)
    result = re.sub(r"[ \t]*\{%-", "{%", result)
    result = re.sub(r"-%\}[ \t]*\r?\n?", "%}", result)
    result = re.sub(r"[ \t]*\{#-", "{#", result)
    result = re.sub(r"-#\}[ \t]*\r?\n?", "#}", result)
    return result


def apply_global_whitespace_control(source: str, trim_blocks: bool, lstrip_blocks: bool) -> str:
    result = source
    if lstrip_blocks:
        result = re.sub(r"^[ \t]+(?=\{%)", "", result, flags=re.MULTILINE)
    if trim_blocks:
        result = re.sub(r"%\}[ \t]*\r?\n", "%}", result)
    return result
