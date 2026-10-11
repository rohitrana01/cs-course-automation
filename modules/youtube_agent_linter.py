import os
import sys
import importlib.util

SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")

def _load_tool(name: str, rel_path: str):
    full_path = os.path.join(SKILLS_DIR, rel_path)
    if not os.path.exists(full_path):
        return None
    spec = importlib.util.spec_from_file_location(name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_hookscore_mod = _load_tool("hookscore", os.path.join("yt-script", "hookscore.py"))
_title_mod     = _load_tool("title", os.path.join("yt-package", "title.py"))

def evaluate_hook(hook_text: str) -> dict:
    """
    Evaluates hook against 21 viral formulas and 5 core properties:
    SPECIFICITY, ADDRESS, STAKES, CURIOSITY, BREVITY.
    """
    if not _hookscore_mod:
        return {"verdict": 0, "band": "UNAVAILABLE", "name": "Unknown", "parts": {}}
    parts, verdict, name, hits = _hookscore_mod.score(hook_text)
    band = _hookscore_mod.band(verdict)
    return {
        "text": hook_text,
        "verdict": verdict,
        "band": band,
        "formula": name,
        "hits": hits,
        "parts": parts
    }

def lint_packaging(title: str, thumb_text: str = None) -> dict:
    """
    Lints title and thumbnail text pairing for truncation, duplication, and vagueness.
    """
    if not _title_mod:
        return {"title": title, "score": 100, "issues": [], "good": []}
    return _title_mod.check(title, thumb_text)

if __name__ == "__main__":
    h = evaluate_hook("Stop using Python lists when you need speed!")
    print(f"Hook Verdict: {h['verdict']}/100 [{h['band']}] - Formula: {h['formula']}")
    
    p = lint_packaging("Why Senior Developers ALWAYS Use Tuples", "TUPLE SPEED")
    print(f"Packaging Score: {p['score']}/100 - Issues: {len(p['issues'])}, Good: {len(p['good'])}")
