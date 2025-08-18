# tests/teststuff.py
import pandas as pd
import igraph as ig

def load_edge_csv_to_igraph(
    path, src="source", dst="target", w="weight", directed=False, aggregate="sum"
):
    """
    Reads an edge-list CSV (with headers) into an igraph Graph.
    - Handles non-contiguous or string node IDs by remapping to 0..n-1
    - Stores original IDs in vertex attribute 'name'
    - Aggregates parallel edges (sum/mean/min/max/first)
    """
    df = pd.read_csv(path)

    # optional: drop self-loops
    df = df[df[src] != df[dst]].copy()

    # Ensure weight column exists; if not, create unit weights
    if w not in df.columns:
        df[w] = 1.0

    # Build a stable mapping from node ID -> 0..n-1
    nodes = pd.Index(pd.concat([df[src], df[dst]]).unique(), name="name")
    id_map = {nid: i for i, nid in enumerate(nodes)}

    # Remap edges to contiguous ints
    df["_u"] = df[src].map(id_map)
    df["_v"] = df[dst].map(id_map)

    # Aggregate parallel edges if any
    if aggregate:
        agg = {w: aggregate}
        df = df.groupby(["_u", "_v"], as_index=False).agg(agg)

    # Create graph
    g = ig.Graph(n=len(nodes), edges=list(zip(df["_u"], df["_v"])), directed=directed)
    g.vs["name"] = nodes.tolist()
    g.es["weight"] = df[w].astype(float).tolist()
    return g

if __name__ == "__main__":
    g = load_edge_csv_to_igraph("tests/Usoskin_graph.csv")
    print(g.summary())

    # Leiden (modularity objective, use edge weights)
    part = g.community_leiden(objective_function="modularity",
                              resolution_parameter=1.0
                              )
    print(f"Communities: {len(part)}")
    print("Membership:", part.membership[:50], "...")
    print("Modularity:", part.modularity)
