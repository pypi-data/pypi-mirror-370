import json, os, datetime, difflib
def timestamp(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
class RunLogger:
    def __init__(self, base_dir: str):
        self.base_dir=base_dir; os.makedirs(os.path.join(base_dir,"logs"),exist_ok=True)
        self.run_id=timestamp(); self.log_path=os.path.join(base_dir,"logs",f"run_{self.run_id}.jsonl")
        self.diff_dir=os.path.join(base_dir,"logs",f"diffs_{self.run_id}"); os.makedirs(self.diff_dir, exist_ok=True)
    def log(self, rec: dict):
        rec={**rec,"ts":timestamp(),"run_id":self.run_id}
        with open(self.log_path,"a",encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False)+"\n")
    def save_diff(self, path: str, before: str, after: str):
        rel=path.replace(os.sep,"/")
        diff=difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=f"a/{rel}", tofile=f"b/{rel}", n=3)
        text="".join(diff); out=os.path.join(self.diff_dir, rel.replace("/", "__") + ".diff")
        os.makedirs(os.path.dirname(out), exist_ok=True); open(out,"w",encoding="utf-8").write(text); return out
