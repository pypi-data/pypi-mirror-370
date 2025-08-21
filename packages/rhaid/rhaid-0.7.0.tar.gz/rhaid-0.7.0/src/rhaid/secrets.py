import re
from rhaid.rules import rule, RuleResult
_P={"secret:aws_access_key": r"AKIA[0-9A-Z]{16}","secret:github_pat": r"ghp_[A-Za-z0-9]{36,}","secret:private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"}
@rule("secret:scan")
def r_secret(path, content, ctx):
    out=[]
    for rid,pat in _P.items():
        m=re.search(pat, content)
        if m: out.append(RuleResult(id=rid, message=f"Potential secret detected ({rid}).", severity="error", path=path, line=content[:m.start()].count("\n")+1, col=1))
    return out
