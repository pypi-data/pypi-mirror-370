import os, json, hashlib
BASELINE_NAME="rhaid_baseline.json"
def _root_dir(start:str)->str: import os; return os.path.abspath(start if os.path.isdir(start) else os.path.dirname(start))
def _fp(path:str)->str: import os; return os.path.join(_root_dir(path), BASELINE_NAME)
def issue_fingerprint(path:str, rid:str, msg:str)->str:
    h=hashlib.sha1(); h.update((path+"\n"+rid+"\n"+msg.strip()).encode("utf-8","ignore")); return h.hexdigest()
def write_baseline(start_path:str, flat:list)->str:
    root=_root_dir(start_path); outp=os.path.join(root, BASELINE_NAME)
    data={"fingerprints": sorted({issue_fingerprint(i["path"], i["id"], i["message"]) for i in flat})}
    open(outp,"w",encoding="utf-8").write(json.dumps(data, indent=2, ensure_ascii=False)); return outp
def load_baseline(start_path:str)->set:
    p=_fp(start_path)
    if not os.path.isfile(p): return set()
    try: return set(json.load(open(p,"r",encoding="utf-8")).get("fingerprints", []))
    except Exception: return set()
def filter_new_against_baseline(start_path:str, flat:list)->list:
    base=load_baseline(start_path); 
    if not base: return flat
    keep=[]; 
    for i in flat:
        fp=issue_fingerprint(i["path"], i["id"], i["message"])
        if fp not in base: keep.append(i)
    return keep
