import networkx as nx
import matplotlib.pyplot as plt

def crear_grafo(nodos):
    navegation_graph = nx.DiGraph()

    for nodo in nodos:
        nodo = nodo.to_dict()
        if "request_ID" in nodo:
            node_id = nodo["request_ID"]
            navegation_graph.add_node(node_id, tipo="request", **nodo)

            if "target_ID" in nodo:
                navegation_graph.add_edge(node_id, nodo["target_ID"], relation="belongs_to")

            if nodo.get("initiator"):
                navegation_graph.add_edge(nodo["initiator"], node_id, relation="initiated_by")

        elif "script_ID" in nodo:
            node_id = nodo["script_ID"]
            navegation_graph.add_node(node_id, tipo="script", **nodo)

            if "target_ID" in nodo:
                navegation_graph.add_edge(node_id, nodo["target_ID"], relation="executed_in")

            if nodo.get("initiator"):
                navegation_graph.add_edge(nodo["initiator"], node_id, relation="initiated_by")

        elif "target_ID" in nodo:
            node_id = nodo["target_ID"]
            navegation_graph.add_node(node_id, tipo="target", **nodo)

    return navegation_graph
