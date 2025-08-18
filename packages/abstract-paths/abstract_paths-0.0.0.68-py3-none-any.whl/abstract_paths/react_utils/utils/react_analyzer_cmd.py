from .react_analyzer_utils import start_analyzer
def react_cmd_start():
    ap = argparse.ArgumentParser(description="Map local imports & exported functions.")
    ap.add_argument("--root", default="src", help="Project source root (default: src)")
    ap.add_argument("--entries", default="index,main", help="Comma list of entry basenames (used when --scope=reachable)")
    ap.add_argument("--scope", choices=["reachable", "all"], default="all", help="reachable|all (default: reachable)")
    ap.add_argument("--out", default="import-graph.json", help="Output JSON file")
    ap.add_argument("--dot", default="graph.dot", help="Optional Graphviz .dot output path")
    args = ap.parse_args()
    src_root = args.root
    scope = args.scope
    out = args.out
    entries = args.entries
    dot = args.dot
    src_root,scope,out,entries,dot
    start_analyzer(
        root=root,
        scope=scope,
        out=out,
        entries=entries,
        dot=dot
    )
if __name__ == "__main__":
    react_cmd_start()
