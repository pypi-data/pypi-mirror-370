\
import ast, re
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set
from rhaid.rules import rule, fixer, RuleResult, FixResult

# -------- Import-order (existing) --------
def _extract_top_import_block(text: str):
    lines=text.splitlines(True); i=0
    def is_import(s): ss=s.strip(); return ss.startswith("import ") or ss.startswith("from ")
    while i < len(lines) and (lines[i].startswith("#!") or re.match(r"^#.*coding[:=]", lines[i])): i+=1
    start=i; saw=False
    while i < len(lines):
        s=lines[i]
        if s.strip()=="" or s.lstrip().startswith("#") or is_import(s):
            if is_import(s): saw=True
            i+=1; continue
        break
    end=i
    if not saw: return (-1,-1,[])
    return (start,end,lines[start:end])

def _sort_import_lines(lines):
    im=[l for l in lines if l.strip().startswith(("import ","from "))]; other={i for i,l in enumerate(lines) if l not in im}
    sim=sorted(im, key=lambda s: s.strip().lower()); out=[]; it=iter(sim)
    for idx in range(len(lines)): out.append(lines[idx] if idx in other else next(it))
    return out

@rule("py:imports_order")
def r_py_imports_order(path, content, ctx):
    if not path.lower().endswith(".py"): return []
    try: ast.parse(content)
    except Exception as e:
        return [RuleResult("py:syntax", f"Python syntax error: {e}", "error", path, line=getattr(e,'lineno',None), col=getattr(e,'offset',None))]
    s,e,block=_extract_top_import_block(content)
    if s==-1: return []
    if block != _sort_import_lines(block):
        return [RuleResult("py:imports_order","Top import block can be normalized (sorted).","info",path,line=s+1,col=1)]
    return []

@fixer("py:imports_order")
def f_py_imports_order(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    s,e,block=_extract_top_import_block(content)
    if s==-1: return FixResult(False, [], content)
    sb=_sort_import_lines(block)
    if block==sb: return FixResult(False, [], content)
    lines=content.splitlines(True); new=lines[:s]+sb+lines[e:]
    return FixResult(True, ["Sorted top import block."], "".join(new))

# -------- Unused imports (new) --------

@dataclass
class _Import:
    line_idx: int
    raw: str
    kind: str   # 'import' or 'from'
    module: str
    names: List[str]  # imported names or module aliases (top-level only)

def _collect_imports(block_lines: List[str]) -> List[_Import]:
    out=[]
    for idx,ln in enumerate(block_lines):
        s=ln.strip()
        if s.startswith("import "):
            rest=s[len("import "):]
            # handle: import a, b as c
            parts=[p.strip() for p in rest.split(",")]
            names=[]
            for p in parts:
                if " as " in p:
                    names.append(p.split(" as ")[1].strip())
                else:
                    names.append(p.split(".")[0])  # module root
            out.append(_Import(idx, ln, "import", "", names))
        elif s.startswith("from ") and " import " in s and not s.startswith("from ."):
            mod=s[len("from "):].split(" import ")[0].strip()
            items=s.split(" import ",1)[1].strip()
            if items=="*": continue
            parts=[p.strip() for p in items.split(",")]
            names=[]
            for p in parts:
                if " as " in p:
                    names.append(p.split(" as ")[1].strip())
                else:
                    names.append(p)
            out.append(_Import(idx, ln, "from", mod, names))
    return out

def _collect_used_names(tree: ast.AST) -> Set[str]:
    used=set()
    class V(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name):
            used.add(node.id)
        def visit_Attribute(self, node: ast.Attribute):
            # capture root of dotted usage: foo.bar -> 'foo'
            cur=node
            while isinstance(cur, ast.Attribute):
                cur=cur.value
            if isinstance(cur, ast.Name):
                used.add(cur.id)
            self.generic_visit(node)
    V().visit(tree)
    return used

def _remove_from_line(line: str, names_to_remove: Set[str]) -> str:
    s=line.strip()
    if s.startswith("import "):
        rest=s[len("import "):]
        parts=[p.strip() for p in rest.split(",")]
        keep=[]
        for p in parts:
            alias=p.split(" as ")[1].strip() if " as " in p else p.split(".")[0]
            if alias not in names_to_remove:
                keep.append(p)
        if not keep:
            return ""  # delete entire line
        return "import " + ", ".join(keep) + ("\n" if not line.endswith("\n") else "")
    if s.startswith("from ") and " import " in s:
        head, items = s.split(" import ",1)
        parts=[p.strip() for p in items.split(",")]
        keep=[]
        for p in parts:
            alias=p.split(" as ")[1].strip() if " as " in p else p
            if alias not in names_to_remove:
                keep.append(p)
        if not keep:
            return ""  # delete entire line
        return head + " import " + ", ".join(keep) + ("\n" if not line.endswith("\n") else "")
    return line

@rule("py:unused_import")
def r_py_unused_import(path, content, ctx):
    if not path.lower().endswith(".py"): return []
    try:
        tree=ast.parse(content)
    except Exception:
        return []  # syntax errors handled elsewhere
    s,e,block=_extract_top_import_block(content)
    if s==-1: return []
    imports=_collect_imports(block)
    used=_collect_used_names(tree)
    issues=[]
    for it in imports:
        unused=[n for n in it.names if n not in used]
        if unused and len(unused)==len(it.names):
            # whole statement unused
            issues.append(RuleResult("py:unused_import", f"Unused import statement.", "warning", path, line=s+it.line_idx+1, col=1))
        elif unused:
            issues.append(RuleResult("py:unused_import", f"Unused import names: {', '.join(unused)}", "warning", path, line=s+it.line_idx+1, col=1))
    return issues

@fixer("py:unused_import")
def f_py_unused_import(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    s,e,block=_extract_top_import_block(content)
    if s==-1: return FixResult(False, [], content)
    imports=_collect_imports(block)
    # Build map line_idx -> names to remove
    to_remove={}
    for it in issues:
        idx=it.line-1 - s
        # parse names list from message when present
        names=set()
        if "Unused import names:" in it.message:
            tail=it.message.split("Unused import names:",1)[1].strip()
            names={n.strip() for n in tail.split(",") if n.strip()}
        else:
            # remove entire line by marking with special token
            names={"__ALL__"}
        to_remove.setdefault(idx, set()).update(names)
    new_block=list(block)
    notes=[]
    for idx, imp in enumerate(imports):
        rem=to_remove.get(imp.line_idx)
        if not rem: continue
        if "__ALL__" in rem:
            new_block[imp.line_idx]=""
            notes.append("Removed unused import statement.")
        else:
            new_line=_remove_from_line(new_block[imp.line_idx], rem)
            if new_line!=new_block[imp.line_idx]:
                new_block[imp.line_idx]=new_line
                notes.append("Removed unused import names.")
    lines=content.splitlines(True)
    out=lines[:s]+new_block+lines[e:]
    new="".join(out)
    return FixResult(new!=content, notes, new)
