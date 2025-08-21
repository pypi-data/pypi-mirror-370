\
import re
from rhaid.rules import rule, fixer, RuleResult, FixResult
def _is_mdx(path): return path.lower().endswith(".mdx")
@rule("mdx:heading_space")
def r_hspace(path, content, ctx):
    if not _is_mdx(path): return []
    out=[]; 
    for i,ln in enumerate(content.splitlines(),1):
        if re.match(r"^#{1,6}\S", ln): out.append(RuleResult("mdx:heading_space","Missing space after '#' in heading.","info",path,line=i,col=1))
    return out
@fixer("mdx:heading_space")
def f_hspace(path, content, issues, ctx):
    if not issues: return FixResult(False, [], content)
    fx=re.sub(r"^(#{1,6})(\S)", r"\1 \2", content, flags=re.MULTILINE); return FixResult(fx!=content, ["Inserted space after '#' in MDX headings."], fx)
@rule("mdx:unclosed_fence")
def r_fence(path, content, ctx):
    if not _is_mdx(path): return []
    return [RuleResult("mdx:unclosed_fence","Unbalanced ``` code fences.","warning", path, line=1,col=1)] if content.count("```")%2!=0 else []
