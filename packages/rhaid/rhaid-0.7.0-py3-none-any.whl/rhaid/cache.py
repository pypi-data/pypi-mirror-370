import os, json, hashlib
CACHE_NAME = ".rhaid_cache.json"
def _root(start: str) -> str:
    start = os.path.abspath(start if os.path.isdir(start) else os.path.dirname(start))
    return start
def _path(start: str) -> str:
    return os.path.join(_root(start), CACHE_NAME)
def file_hash(content: str) -> str:
    return hashlib.sha1(content.encode('utf-8','ignore')).hexdigest()
def load_cache(start: str) -> dict:
    p = _path(start)
    if not os.path.isfile(p): return {}
    try: return json.load(open(p,"r",encoding="utf-8"))
    except Exception: return {}
def save_cache(start: str, data: dict):
    p = _path(start)
    try: open(p,"w",encoding="utf-8").write(json.dumps(data, indent=2))
    except Exception: pass
