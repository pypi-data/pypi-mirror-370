import rhaid.python_ast_rules as pr
from rhaid.rules import RuleResult
def test_unused_import_detection():
    src = "import os, sys\nfrom math import sqrt, ceil\n\nprint('x')\n"
    issues = pr.r_py_unused_import("t.py", src, {})
    ids = [i.id for i in issues]
    assert "py:unused_import" in ids
