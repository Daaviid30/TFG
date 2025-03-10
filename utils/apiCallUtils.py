"""
AUTOR: David Martín Castro
This script contains the functions needed to create api call nodes.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import utils.cdpUtils as cdpUtils
import utils.timeUtils as timeUtils

#---------------------------- API CALL FUNCTIONS -------------------------

def get_apiCallScriptIDs(report_json) -> None:
    """
    When an API call is detected, we use a manual method for obtein the scriptID
    """
    # Search for the last script that have the same url of the API call
    for node in report_json:
        if (node["nodeType"] == "apiCall"):
                for node2 in report_json:
                    if (node2["nodeType"] == "script") and (node2["timestamp"] >= node["timestamp"]) and (node2["url"] == node["scriptUrl"]):
                        node["scriptID"] = node2["scriptID"]
                        break

def api_call_detected(api_name, origin):
        """
        This function is called on hooks.js when an API call is detected
        """
        # Create the apiCall node and save it.
        cdpUtils.api_call_saved(api_name, "", origin)