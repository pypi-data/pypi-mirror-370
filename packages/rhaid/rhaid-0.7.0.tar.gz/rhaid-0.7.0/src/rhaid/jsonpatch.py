import json
def _is_json(s):
    try:
        json.loads(s); return True
    except Exception:
        return False
def json_patch(before: str, after: str):
    if not (_is_json(before) and _is_json(after)): return []
    try:
        b=json.loads(before); a=json.loads(after)
        ops=[]
        for k in b:
            if k not in a: ops.append({"op":"remove","path":f"/{k}"})
            elif a[k]!=b[k]: ops.append({"op":"replace","path":f"/{k}","value":a[k]})
        for k in a:
            if k not in b: ops.append({"op":"add","path":f"/{k}","value":a[k]})
        return ops
    except Exception:
        return []
