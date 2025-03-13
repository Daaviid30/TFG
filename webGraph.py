"""
AUTOR: David Martín Castro
This script create the WG (Web Graph) from the report.json created based on the navigation
events captured by CDP (Chrome DevTools Protocol).
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import networkx as nx

#--------------------------- GRAPH CREATION ------------------------------

def create_graph(report: dict):
    # Create a directed graph
    graph = nx.DiGraph()

    # Adding all the nodes to the graph
    for node in report:
        type = node["nodeType"]
        if type == "apiCall":
            graph.add_node(node["apiCall"])
        elif type == "domElement":
            graph.add_node(node["elementID"])
        elif type == "eventListener":
            graph.add_node(node["type"])
        elif type == "executionContext":
            graph.add_node(node["executionContextID"])
        elif type == "extension":
            graph.add_node(node["extensionID"])
        elif type == "network":
            graph.add_node(node["requestID"])
        elif type == "page":
            graph.add_node(node["pageID"])
        elif type == "script":
            graph.add_node(node["scriptID"])
        elif type == "target":
            if node["event"] == "create":
                graph.add_node(node["targetID"])

    # Export the graph to a gexf file (for Gephi visualitation)
    nx.write_gexf(graph, "webGraph.gexf")
