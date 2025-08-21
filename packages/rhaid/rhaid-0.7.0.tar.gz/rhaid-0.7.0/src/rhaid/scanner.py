import os, fnmatch
from typing import List
try:
    from pathspec import PathSpec
except Exception:
    PathSpec = None
def glob_match(p: str, pats: List[str]) -> bool:
    p=p.replace('\\','/'); return any(fnmatch.fnmatch(p, pat) for pat in pats)
def _load_gitignore(root: str):
    if not PathSpec: return None
    gi=os.path.join(root,".gitignore")
    if not os.path.isfile(gi): return None
    with open(gi,"r",encoding="utf-8",errors="ignore") as f:
        return PathSpec.from_lines("gitwildmatch", f.readlines())
def list_files(root: str, include: List[str], exclude: List[str]) -> List[str]:
    root=os.path.abspath(root); gi=_load_gitignore(root); out=[]
    for dp,_,fns in os.walk(root):
        norm=(dp.replace('\\','/') + '/')
        if any(fnmatch.fnmatch(norm, ex if ex.endswith('/**') else ex.rstrip('/')+'/**') for ex in exclude): continue
        for fn in fns:
            full=os.path.join(dp,fn); rel=os.path.relpath(full, root).replace('\\','/')
            if gi and gi.match_file(rel): continue
            if glob_match(rel, include) and not glob_match(rel, exclude): out.append(full)
    return out
