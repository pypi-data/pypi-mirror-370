import os
from typing import Any, Dict
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from yapl_py.yapl import YAPL, YAPLOptions
from yapl_py.renderer import WhitespaceOptions

BASE = os.path.dirname(__file__)


def make_engine():
    def ensure_ext(p: str) -> str:
        return p if p.endswith(".yapl") else p + ".yapl"

    def resolve_path(templateRef: str, fromDir: str, ensureExt):
        ref = ensureExt(templateRef)
        if ref.startswith("./") or ref.startswith("../"):
            return os.path.normpath(os.path.join(fromDir, ref))
        if os.path.isabs(ref):
            return ref
        return os.path.normpath(os.path.join(fromDir, ref))

    def load_file(abs_path: str) -> str:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()

    opts = YAPLOptions(
        baseDir=BASE,
        strictPaths=True,
        whitespace=WhitespaceOptions(trimBlocks=True, lstripBlocks=True, dedentBlocks=True),
    )
    return YAPL(opts)


def test_conditional_agent_render():
    eng = make_engine()
    vars: Dict[str, Any] = {
        "user_type": "expert",
        "domain": "TypeScript",
        "include_examples": True,
        "capability_1": "Explain complex topics clearly",
        "capability_2": "Provide code samples",
    }
    prompt = eng.render(
        os.path.join("prompts", "examples", "conditional-agent.md.yapl"),
        vars,
    )
    out = prompt.content
    assert "You are a helpful AI." in out
    assert "Adopt a friendly, upbeat tone." in out
    assert "You are an advanced AI assistant" in out
    assert "Respond in markdown." in out
    assert "Provide detailed technical explanations" in out
    assert "Your Capabilities" in out
    assert "Provide code samples" in out
