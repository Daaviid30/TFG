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
import utils.timeUtils as timeUtils

#---------------------------- JSON FUNCTIONS ----------------------------

"""
We need to store the infomation of the nodes in a json file in order to have
a report that we can analyze later.
"""
report_json = [] # List of dictionaries that contains all the nodes

async def generate_json_report() -> None:

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
            timeUtils.generate_timestamp()
        )
        # Add the node to the report
        report_json.append(node.to_dict())

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
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

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
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

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

def page_navigated(page) -> None:

    """
    This function is called when we navigate to a page, saving the page info.
    """

    frame = page["frame"]
    node = Page.PageNode(
        frame["id"],
        frame["url"],
        frame["loaderId"],
        timeUtils.generate_timestamp()
    )
    # Add the node to the report
    report_json.append(node.to_dict())

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