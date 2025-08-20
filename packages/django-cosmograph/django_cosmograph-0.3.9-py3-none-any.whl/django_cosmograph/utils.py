import math


def assign_node_sizes(nodes, links, max_size=10, base_size=5):
    degree = {}
    for link in links:
        source = link.get("source")
        target = link.get("target")
        if source:
            degree[source] = degree.get(source, 0) + 1
        if target:
            degree[target] = degree.get(target, 0) + 1

    for node in nodes:
        d = degree.get(node.get("id"), 0)
        size = round(base_size + max_size * math.atan(d / 3), 2)
        node["size"] = size

    return nodes
