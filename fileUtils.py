"""
AUTOR: David Martín Castro
This script contains the functions that are used to create, delete or modify files.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import os
import shutil
import json
from colours import *
import paths

#---------------------------- FILE FUNCTIONS -----------------------------

def remove_report() -> None:

    """
    This function tries to remove previous versions of report.json file.
    """

    try:
        os.remove(paths.get_report_path())
        print(f"{greenColour}[+]{endColour}{grayColour} Report file removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Previous report file not exist{endColour}")


def remove_user_data() -> None:

    """
    This function tries to remove previous versions of user data directory.
    """

    try:
        shutil.rmtree(paths.get_user_data_path())
        print(f"{greenColour}[+]{endColour}{grayColour} User data directory removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Previous user data directory not exist{endColour}")