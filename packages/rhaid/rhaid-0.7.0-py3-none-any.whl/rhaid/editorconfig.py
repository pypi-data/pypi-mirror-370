import os, configparser
DEFAULTS={"indent_size":"4","end_of_line":"lf","insert_final_newline":"true"}
def load_editorconfig(start_path: str) -> dict:
    p=os.path.join(os.path.abspath(start_path if os.path.isdir(start_path) else os.path.dirname(start_path)),".editorconfig")
    if not os.path.isfile(p): return DEFAULTS.copy()
    parser=configparser.ConfigParser(); parser.read(p)
    sec="*"
    if sec in parser: return {**DEFAULTS, **{k.lower():v for k,v in parser[sec].items()}}
    return {**DEFAULTS, **({k.lower():v for k,v in parser[parser.sections()[0]].items()} if parser.sections() else {})}
