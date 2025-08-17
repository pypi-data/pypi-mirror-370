import json
from pathlib import Path

USAGE_FILE = Path("documentation/raw/readmebro_usage.json")
GRAPH_FILE = Path("documentation/function_graph.md")

def generate_mermaid_graph():
    """Generate a Mermaid network graph from the ReadMeBro usage map."""
    if not USAGE_FILE.exists():
        print("[ReadMeBro] No usage file found.")
        return

    with open(USAGE_FILE, "r", encoding="utf-8") as f:
        usage_map = json.load(f)

    edges = set()
    for name, usages in usage_map.items():
        for u in usages:
            # Link function/class to file where it's used
            file_node = Path(u["file"]).stem
            if file_node != name:  # avoid self-loops
                edges.add(f"    {name} --> {file_node}")

    if not edges:
        print("[ReadMeBro] No relationships found for graph.")
        return

    mermaid_block = "```mermaid\ngraph TD\n" + "\n".join(sorted(edges)) + "\n```"

    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        f.write("## 🔗 Function/Class Usage Graph\n\n")
        f.write(mermaid_block)

    print(f"[ReadMeBro] Mermaid graph saved → {GRAPH_FILE}")
