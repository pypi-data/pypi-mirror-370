from rhaid.rules import rule, fixer, RuleResult, FixResult
import re
try:
    import hcl2
except Exception:
    hcl2 = None
_EQ=re.compile(r'^(\s*[a-zA-Z0-9_".\[\]-]+)\s*=\s*(.+)$')
@rule("tf:eq_spacing")
def r_tf_spacing(path, content, ctx):
    if not path.lower().endswith(".tf"): return []
    out=[]
    for i,ln in enumerate(content.splitlines(),1):
        m=_EQ.match(ln)
        if m and " = " not in ln and not ln.strip().startswith(("#","//")):
            out.append(RuleResult("tf:eq_spacing","Normalize 'key = value' spacing.","info",path,line=i,col=(ln.find("=")+1 if "=" in ln else 1)))
            if len(out)>=20: break
    return out
@fixer("tf:eq_spacing")
def f_tf_spacing(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    out=[]
    for ln in content.splitlines(True):
        m=_EQ.match(ln)
        if m and not ln.strip().startswith(("#","//")):
            out.append(f"{m.group(1)} = {m.group(2).rstrip()}\n")
        else:
            out.append(ln)
    fx="".join(out)
    return FixResult(fx!=content, ["Normalized Terraform '=' spacing to 'key = value'."], fx)
@rule("tf:parse")
def r_tf_parse(path, content, ctx):
    if not path.lower().endswith(".tf") or not hcl2: return []
    try:
        hcl2.loads(content)
        return []
    except Exception as e:
        return [RuleResult("tf:parse", f"Invalid HCL (Terraform): {e}", "error", path, line=None, col=None)]
