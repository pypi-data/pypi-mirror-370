from dataclasses import dataclass
from typing import Callable, List, Dict, Tuple, Optional
import re, json, io, yaml

@dataclass
class RuleResult:
    """Represents a single rule result (issue)."""
    id: str
    message: str
    severity: str
    path: str
    line: Optional[int] = None
    col: Optional[int] = None

@dataclass
class FixResult:
    """Represents the result of applying a fixer."""
    applied: bool
    notes: List[str]
    content: str

# Plugin support imports
import importlib.util
import glob
import os
# Registry for rules and fixers
_RULES: Dict[str, Callable[[str, str, dict], List[RuleResult]]] = {}
_FIXERS: Dict[str, Callable[[str, str, List[RuleResult], dict], FixResult]] = {}

def rule(id: str) -> Callable:
    """Decorator to register a rule."""
    def deco(fn):
        _RULES[id] = fn
        return fn
    return deco

def fixer(id: str) -> Callable:
    """Decorator to register a fixer."""
    def deco(fn):
        _FIXERS[id] = fn
        return fn
    return deco

def load_plugins(plugin_dir: str = "plugins"):
    """Dynamically load rule/fixer plugins from a directory."""
    for pyfile in glob.glob(os.path.join(plugin_dir, "*.py")):
        spec = importlib.util.spec_from_file_location("plugin", pyfile)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

def get_rule_priority(rule_id: str, config: dict = None) -> int:
    """Get priority for a rule from config, default 10."""
    if config and "priorities" in config:
        return config["priorities"].get(rule_id, 10)
    return 10

_SUPPRESS_RE = re.compile(r"rhaid:ignore\s+([a-z0-9:_\-]+)", re.IGNORECASE)

def filter_suppressions(content: str, issues: List[RuleResult]) -> List[RuleResult]:
    """Filter out suppressed issues from content."""
    ids = {m.group(1).lower() for m in _SUPPRESS_RE.finditer(content or "")}
    return [it for it in issues if it.id.lower() not in ids] if ids else issues

def run_rules(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Run all registered rules on content."""
    res = []
    for rid, fn in _RULES.items():
        res.extend(fn(path, content, ctx))
    return res

def apply_fixers(path: str, content: str, issues: List[RuleResult], ctx: dict) -> Tuple[str, List[str]]:
    """Apply all relevant fixers to content."""
    updated = content
    notes = []
    by_id: Dict[str, List[RuleResult]] = {}
    for it in issues:
        by_id.setdefault(it.id, []).append(it)
    for rid, fx in _FIXERS.items():
        rel = by_id.get(rid, [])
        if not rel:
            continue
        fr = fx(path, updated, rel, ctx)
        if fr.applied:
            updated = fr.content
            notes.extend(fr.notes)
    return updated, notes

@rule("format:newline")
def r_trailing_newline(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect missing trailing newline at EOF."""
    if content and not content.endswith("\n"):
        return [RuleResult("format:newline", "No trailing newline at EOF.", "warning", path, line=1, col=1)]
    return []

@rule("format:crlf")
def r_crlf(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect CRLF line endings."""
    if "\r\n" in content or "\r" in content:
        return [RuleResult("format:crlf", "CRLF detected; prefer LF.", "info", path, line=1, col=1)]
    return []

@rule("format:tabs")
def r_tabs(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect tab characters in content."""
    out = []
    for i, ln in enumerate(content.splitlines(), 1):
        if "\t" in ln:
            out.append(RuleResult("format:tabs", "Tabs detected; prefer spaces.", "info", path, line=i, col=ln.find("\t") + 1))
        if len(out) >= 10:
            break
    return out

@rule("json:parse")
def r_json(path: str, content: str, ctx: dict) -> List[RuleResult]:
    """Detect invalid JSON files."""
    if not path.lower().endswith(".json"):
        return []
    try:
        json.loads(content)
        return []
    except Exception as e:
        line = getattr(e, 'lineno', None) or getattr(e, 'pos', None)
        col = getattr(e, 'colno', None) or getattr(e, 'col', None)
        return [RuleResult("json:parse", f"Invalid JSON: {e}", "error", path, line=line, col=col)]
