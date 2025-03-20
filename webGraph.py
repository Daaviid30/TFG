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
            graph.add_node(node["apiCall"], viz={"color": {"r": 255, "g": 0, "b": 46}})
        elif type == "domElement":
            graph.add_node(node["elementID"], viz={"color": {"r": 255, "g": 197, "b": 0}})
        elif type == "eventListener":
            graph.add_node(node["type"], viz={"color": {"r": 205, "g": 255, "b": 0}})
        elif type == "executionContext":
            graph.add_node(node["executionContextID"], viz={"color": {"r": 0, "g": 255, "b": 0}})
        elif type == "extension":
            graph.add_node(node["extensionID"], viz={"color": {"r": 0, "g": 0, "b": 255}})
        elif type == "network":
            graph.add_node(node["requestID"], viz={"color": {"r": 0, "g": 255, "b": 189}})
        elif type == "page":
            graph.add_node(node["pageID"], viz={"color": {"r": 0, "g": 209, "b": 255}})
        elif type == "script":
            graph.add_node(node["scriptID"], viz={"color": {"r": 255, "g": 0, "b": 143}})
        elif type == "target":
            if node["event"] == "create":
                graph.add_node(node["targetID"], viz={"color": {"r": 144, "g": 144, "b": 144}})

    # Adding all the edges to the graph
    for node in report:
        type = node["nodeType"]
        if type == "page":
            try:
                # Add edge from target (frameID) to page
                graph.add_edge(node["frameID"], node["pageID"])
            except:
                pass
        elif type == "executionContext":
            try:
                # Add edge from page to executionContext
                graph.add_edge(node["pageID"], node["executionContextID"])
            except:
                pass
        elif type == "extension":
            try:
                # Add edge from executionContext to extension
                graph.add_edge(node["executionContextID"], node["extensionID"])
            except:
                pass
        elif type == "script":
            try:
                # Add edge from executionContext to script
                graph.add_edge(node["executionContextID"], node["scriptID"])
                if node["initiator"]:
                    graph.add_edge(node["initiator"], node["scriptID"])
            except:
                pass
        elif type == "domElement":
            try:
                graph.add_edge(node["initiator"], node["elementID"])
            except:
                pass
        elif type == "apiCall":
            try:
                graph.add_edge(node["scriptID"], node["apiCall"])
            except:
                pass
        elif type == "eventListener":
            try:
                graph.add_edge(node["scriptID"], node["type"])
            except:
                pass
        elif type == "network":
            try:
                if "page" in node["initiator"]:
                    graph.add_edge(node["senderUrl"], node["requestID"])
                
                if "page" in node["targetUrl"]:
                    graph.add_edge(node["requestID"], node["targetUrl"])
                else: 
                    for node2 in report:
                        if (node2["nodeType"] == "script") and (node["targetUrl"] == node2["url"]) \
                        and (node["timestamp"] < node2["timestamp"]):
                            graph.add_edge(node["requestID"], node2["scriptID"])
                            break
                
                
            except Exception as e:
                print(e)
                pass
            

    # Export the graph to a gexf file (for Gephi visualitation)
    nx.write_gexf(graph, "webGraph.gexf")
