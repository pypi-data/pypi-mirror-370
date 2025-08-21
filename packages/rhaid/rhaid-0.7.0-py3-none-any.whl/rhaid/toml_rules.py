from rhaid.rules import rule, fixer, RuleResult, FixResult
def _parse_toml(text: str):
    try:
        import tomllib; return tomllib.loads(text)
    except Exception:
        try:
            import tomli as tomllib; return tomllib.loads(text)
        except Exception as e:
            raise e
@rule("toml:parse")
def r_toml_parse(path, content, ctx):
    if not path.lower().endswith(".toml"): return []
    try: _parse_toml(content); return []
    except Exception as e:
        import re
        msg=str(e); line=col=None
        m=re.search(r"line\s+(\d+)(?:\s+column\s+(\d+))?", msg)
        if m: line=int(m.group(1)); col=int(m.group(2)) if m.group(2) else None
        return [RuleResult("toml:parse", f"Invalid TOML: {e}", "error", path, line=line, col=col)]
@rule("toml:eq_spacing")
def r_toml_spacing(path, content, ctx):
    if not path.lower().endswith(".toml"): return []
    out=[]
    for i,ln in enumerate(content.splitlines(),1):
        if "=" in ln and not ln.strip().startswith(("#",";","[")):
            if " = " not in ln:
                out.append(RuleResult("toml:eq_spacing","Normalize 'key = value' spacing.","info",path,line=i,col=(ln.find("=")+1)))
    return out
@fixer("toml:eq_spacing")
def f_toml_spacing(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    out=[]
    for ln in content.splitlines(True):
        if "=" in ln and not ln.strip().startswith(("#",";","[")):
            parts=ln.split("=",1)
            out.append(parts[0].rstrip()+" = "+parts[1].lstrip())
        else:
            out.append(ln)
    fx="".join(out)
    return FixResult(fx!=content, ["Normalized TOML '=' spacing."], fx)
