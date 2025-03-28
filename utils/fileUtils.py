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

def decompress_extension(extension_path) -> None:

    """
    This function tries to decompress the extension file.
    """
    try:
        shutil.unpack_archive(extension_path, paths.get_actual_path() + "\\chrome-extension-directory")
        print(f"{greenColour}[+]{endColour}{grayColour} Extension decompressed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Extension not decompressed{endColour}")

def remove_extension() -> None:

    """
    This function tries to remove the extension directory.
    """
    try:
        shutil.rmtree(paths.get_extension_path())
        print(f"{greenColour}[+]{endColour}{grayColour} Extension removed{endColour}")
    except:
        print(f"{redColour}[!]{endColour}{grayColour} Extension not removed{endColour}")