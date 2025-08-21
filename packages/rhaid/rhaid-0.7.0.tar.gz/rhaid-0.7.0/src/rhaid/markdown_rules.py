import re
from rhaid.rules import rule, fixer, RuleResult, FixResult
@rule("md:heading_space")
def r_hspace(path, content, ctx):
    if not path.lower().endswith(".md"): return []
    out=[]; 
    for i,ln in enumerate(content.splitlines(),1):
        if re.match(r"^#{1,6}\S", ln): out.append(RuleResult("md:heading_space","Missing space after '#' in heading.","info",path,line=i,col=1))
    return out
@fixer("md:heading_space")
def f_hspace(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    fx=re.sub(r"^(#{1,6})(\S)", r"\1 \2", content, flags=re.MULTILINE); return FixResult(fx!=content, ["Inserted space after '#' in headings."], fx)
@rule("md:unclosed_fence")
def r_fence(path, content, ctx):
    if not path.lower().endswith(".md"): return []
    return [RuleResult("md:unclosed_fence","Unbalanced ``` code fences.","warning", path, line=1,col=1)] if content.count("```")%2!=0 else []
