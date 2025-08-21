\
import re
from rhaid.rules import rule, fixer, RuleResult, FixResult

_IMPORT = re.compile(r'^\s*(import\s.+?from\s+[\'"].+?[\'"];?|import\s+[\'"].+?[\'"];?)\s*$', re.MULTILINE)

def _extract_import_block(text: str):
    lines = text.splitlines(True)
    i = 0
    while i < len(lines) and (lines[i].startswith("#!") or lines[i].strip().startswith("//")):
        i += 1
    start = i; saw = False
    while i < len(lines):
        s = lines[i]
        if s.strip()=="" or s.lstrip().startswith("//") or _IMPORT.match(s):
            if _IMPORT.match(s): saw=True
            i += 1
            continue
        break
    end = i
    if not saw: return (-1,-1,[])
    return (start, end, lines[start:end])

def _sort_imports(lines):
    im = [l for l in lines if _IMPORT.match(l)]
    other = {i for i,l in enumerate(lines) if not _IMPORT.match(l)}
    sim = sorted(im, key=lambda s: s.strip().lower())
    out = []
    it = iter(sim)
    for idx in range(len(lines)):
        out.append(lines[idx] if idx in other else next(it))
    return out

@rule("js:imports_order")
def r_js_imports(path, content, ctx):
    if not path.lower().endswith((".js",".jsx",".ts",".tsx")): return []
    s,e,block = _extract_import_block(content)
    if s == -1: return []
    if block != _sort_imports(block):
        return [RuleResult("js:imports_order","Top import block can be normalized (sorted).","info", path, line=s+1, col=1)]
    return []

@fixer("js:imports_order")
def f_js_imports(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    s,e,block = _extract_import_block(content)
    if s == -1: return FixResult(False, [], content)
    sb = _sort_imports(block)
    if sb == block: return FixResult(False, [], content)
    lines = content.splitlines(True)
    new = lines[:s]+sb+lines[e:]
    return FixResult(True, ["Sorted JS/TS top import block."], "".join(new))
