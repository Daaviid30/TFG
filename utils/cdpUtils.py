"""
AUTOR: David Martín Castro
This script contains all the functions needed to work with CDP (Chrome DevTools Protocol).
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

from playwright.async_api import async_playwright
import asyncio
import json
import node_objects.Target as Target
import node_objects.Page as Page
import node_objects.Network as Network
import node_objects.ExecutionContext as ExecutionContext
import node_objects.Script as Script
import node_objects.Extension as Extension
import node_objects.DOMElement as DOMElement
import utils.timeUtils as timeUtils

#---------------------------- GLOBAL VARIABLES --------------------------

global breakpoint_scriptID

#---------------------------- JSON FUNCTIONS ----------------------------

"""
We need to store the infomation of the nodes in a json file in order to have
a report that we can analyze later.
"""
report_json = [] # List of dictionaries that contains all the nodes

async def generate_json_report() -> None:

    await page_associate_id()
    await initiator_associate_page()

    with open("report.json", "w") as report:
        json.dump(report_json, report, indent=4)

#---------------------------- TARGET FUNCTIONS --------------------------

def get_targets(targets) -> None:

    """
    This function is called at the beginning of the program, saving the targets that
    exists before we start capturing them.
    """

    for target in targets["targetInfos"]:

        # Create the target node object
        node = Target.TargetNode(
            target["targetId"],
            target["type"],
            "create",
            target["url"],
            timeUtils.generate_timestamp()
        )
        # Add the node to the report
        report_json.append(node.to_dict())

        # Call the page functions if target is a page
    if node.type == "page":
        store_page_id(node)

def target_created(target) -> None:

    """
    This function is called when a new target is created, and saves the target info.
    """

    target_info = target["targetInfo"]
    # Create the target node object
    node = Target.TargetNode(
        target_info["targetId"],
        target_info["type"],
        "create",
        target_info["url"],
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

    # Call the page functions if target is a page
    if node.type == "page":
        store_page_id(node)

def target_info_changed(target) -> None:

    """
    This function is called when the information of a target is changed,
    and saves the target info.
    """

    target_info = target["targetInfo"]
    node = Target.TargetNode(
        target_info["targetId"],
        target_info["type"],
        "change",
        target_info["url"],
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

    # Call the page functions if target is a page
    if node.type == "page":
        store_page_id(node)

def target_destroyed(target) -> None:

    """
    This function is called when a new target is destroyed, and saves the target info.
    """
    # Create the node in dict version, because destroy event is not a TargetNode
    node = {
        "nodeType": "target",
        "targetID": target["targetId"],
        "event": "destroy",
        "timestamp": timeUtils.generate_timestamp()
    }
    # Add the node to the report
    report_json.append(node)

#---------------------------- PAGE FUNCTIONS -----------------------------

# Dictionary that stores all the page IDs we create
page_IDs = {}

def store_page_id(target) -> None:

    """
    This function stores the page ID of a page.
    """
    if target.url not in page_IDs.keys():
        id = "page" + str(len(page_IDs))
        page_IDs[target.url] = id

def page_navigated(page) -> None:

    """
    This function is called when we navigate to a page, saving the page info.
    """

    frame = page["frame"]
    node = Page.PageNode(
        "pageID",
        frame["id"],
        frame["url"],
        frame["loaderId"],
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

async def page_associate_id() -> None:

    """
    This function is called at the end of the program, associating the page ID to the page node.
    """

    for node in report_json:
        if node["nodeType"] == "page":
            node["pageID"] = page_IDs[node["url"]]

#---------------------------- NETWORK FUNCTIONS --------------------------

def get_initiator(request) -> str:

    """
    This function gets the initiator of a request.
    """

    initiator = request.get("initiator", None) # Tries to get the initiator object
    if initiator:
        initiator_type = initiator["type"]
        if initiator_type == "parser": # Parser initiator is the url of the requester
            return initiator.get("url", None)
        elif initiator_type == "script": # For script, we try to get his ID
            script_id = initiator.get("stack", None).get("callFrames", None)[0].get("scriptId",None)
            if script_id:
                return script_id
        else: # If we do not found any of the previous data, we use the requester url as initiator
            return initiator.get("url", request["documentURL"])
    return request["documentURL"]

async def initiator_associate_page() -> None:

    """
    This function is called at the end of the program, associating the network initiator to the page node.
    """

    for node in report_json:
        if node["nodeType"] == "network" and node["initiator"] in page_IDs.keys():
            node["initiator"] = page_IDs[node["initiator"]]

def request_sent(request) -> None:

    """
    This function is called when a new request is sent, saving the request info.
    """
    node = Network.NetworkNode(
        request["requestId"],
        request["documentURL"],
        request["request"]["url"],
        request.get("frameId", None),
        get_initiator(request),
        timeUtils.generate_timestamp()
    )

    # Add the node to the report
    report_json.append(node.to_dict())

#------------------------- EXTENSION FUNCTIONS ----------------------------

def is_extension(execution_context) -> bool:

    """
    This function checks if the a execution context is from an extension.
    """
    if "chrome-extension" in execution_context.origin:
        return True
    return False

def get_extension_id(origin) -> str:

    """
    This function gets the extension id from the origin.
    origin structure: chrome-extension://extension_id
    """
    return origin.split("//")[1]

def extension_found(execution_context) -> None:

    """
    This function is called when an extension is found, saving the extension info.
    """

    node = Extension.ExtensionNode(
        get_extension_id(execution_context.origin),
        execution_context.name,
        timeUtils.generate_timestamp()
    )

    # Add the node to the report
    report_json.append(node.to_dict())

#----------------------- EXECUTION CONTEXT FUNCTIONS ---------------------

def get_execution_context_type(execution_context) -> str:
    auxData = execution_context.get("auxData", None)
    if auxData:
        return auxData.get("type", None)
    return auxData

def get_execution_context_frameID(execution_context) -> str:
    auxData = execution_context.get("auxData", None)
    if auxData:
        return auxData.get("frameId", None)
    return auxData

def execution_context_created(execution_context) -> None:

    """
    This function is called when a new execution context is created, saving the execution context info.
    """
    context = execution_context["context"]
    node = ExecutionContext.ExecutionContextNode(
        context["id"],
        context["origin"],
        context["name"],
        get_execution_context_type(context),
        get_execution_context_frameID(context),
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

    # Call the extension functions
    if is_extension(node):
        extension_found(node)

#------------------------- DEBUGGER FUNCTIONS ----------------------------

def get_script_type(script) -> str:
    isModule = script.get("isModule", None)
    if isModule:
        return "module"
    return "script"

def get_script_initiator(script) -> str:
    initiator = script.get("stackTrace", None)
    if initiator:
        initiator = initiator.get("callFrames", None)[0]
        if initiator:
            initiator = initiator.get("scriptId", None)
    return initiator

def script_parsed(script) -> None:

    """
    This function is called when a new script is parsed, saving the script info.
    """

    node = Script.ScriptNode(
        script["scriptId"],
        script["url"],
        script["executionContextId"],
        get_script_type(script),
        get_script_initiator(script),
        timeUtils.generate_timestamp()
    )

    # Add the node to the report
    report_json.append(node.to_dict())

#---------------------------- DOM FUNCTIONS -----------------------------

def child_node_inserted(element) -> None:
    """
    This function is called when a new child node is inserted, saving the child node info.
    """
    # Pause the debugger in order to get the initiator
    element = element.get("node", element)
    global breakpoint_scriptID

    node = DOMElement.DOMElementNode(
        element["nodeId"],
        element["nodeType"],
        element["nodeName"],
        breakpoint_scriptID,
        timeUtils.generate_timestamp()
    )

    # Add the node to the report
    report_json.append(node.to_dict())

async def child_node_updated(element, cdp_session) -> None:
    
    """
    This function is called when a child node is updated, saving the child node info.
    """
    node = await cdp_session.send("DOM.describeNode", {"nodeId": element["nodeId"]})
    node = node["node"]

    DOM_node = DOMElement.DOMElementNode(
        node["nodeId"],
        node["nodeType"],
        node["nodeName"],
        breakpoint_scriptID,
        timeUtils.generate_timestamp()
    )

    # Add the node to the report
    report_json.append(DOM_node.to_dict())


#---------------------------- CDP FUNCTIONS ------------------------------

async def enable_events(cdp_session) -> None:

    """
    This function calls all the methods needed to enable the events that we want to
    capture.
    """

    await cdp_session.send("Network.enable")
    await cdp_session.send("Page.enable")
    await cdp_session.send("Debugger.enable")
    await cdp_session.send("Target.setDiscoverTargets", {"discover": True})
    await cdp_session.send("Runtime.enable")
    await cdp_session.send("DOM.enable")

async def set_breakpoints(cdp_session) -> None:

    """
    This function sets the breakpoints needed.
    """
    # Create a breakpoint that allows us to pause the debugger en each DOM event
    document = await cdp_session.send("DOM.getDocument", {"depth": -1})
    document_nodeID = document["root"]["nodeId"]
    await cdp_session.send("DOMDebugger.setDOMBreakpoint", {"nodeId": document_nodeID, "type": "subtree-modified"})

async def on_debugger_paused(event, cdp_session) -> None:

    """
    This function resume the debugger and change the value of breakpoint_scriptID, which is the script that
    have been executed when the debugger is paused.
    """
    global breakpoint_scriptID
    breakpoint_scriptID = event["callFrames"][0]["location"]["scriptId"]
    await cdp_session.send("Debugger.resume")

def target_events(cdp_session) -> None:

    """
    This function calls all the target events we need.
    """

    cdp_session.on("Target.targetCreated", target_created)
    cdp_session.on("Target.targetInfoChanged", target_info_changed)
    cdp_session.on("Target.targetDestroyed", target_destroyed)

def page_events(cdp_session) -> None:

    """
    This function calls all the page events we need.
    """

    cdp_session.on("Page.frameNavigated", page_navigated)

def network_events(cdp_session) -> None:

    """
    This function calls all the network events we need.
    """

    cdp_session.on("Network.requestWillBeSent", request_sent)

def execution_context_events(cdp_session) -> None:

    """
    This function calls all the execution context events we need.
    """

    cdp_session.on("Runtime.executionContextCreated", execution_context_created)

def script_events(cdp_session) -> None:

    """
    This function calls all the script events we need.
    """

    cdp_session.on("Debugger.scriptParsed", script_parsed)

def DOM_events(cdp_session) -> None:

    """
    This function calls all the DOM events we need.
    """

    cdp_session.on("DOM.childNodeInserted", child_node_inserted)
    cdp_session.on("DOM.childNodeCountUpdated", lambda params: child_node_updated(params, cdp_session))

def paused_events(cdp_session) -> None:

    """
    This function calls when the debugger is paused.
    """

    cdp_session.on("Debugger.paused", lambda params: on_debugger_paused(params, cdp_session))