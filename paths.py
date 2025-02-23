"""
AUTOR: David Martín Castro
This script is used to find and create the paths we need in the program.
"""

#---------------------------- LIBRARIES IMPORT ---------------------------

import os

#---------------------------- PATH CREATION ------------------------------

def get_actual_path() -> str:

    """
    Returns the current working directory path.

    This function utilizes the os module to obtain the absolute path 
    of the current working directory where the script is executed.
    """

    actual_path = os.getcwd()
    return actual_path

def get_report_path() -> str:

    """
    Returns the path where the report.json file will be stored.
    """
    actual_path = get_actual_path()
    report_path = actual_path + "\\report.json"

    return report_path

def get_user_data_path() -> str:

    """
    Returns the path where the navegation user data will be stored.
    """

    actual_path = get_actual_path()
    user_data_path = actual_path + "\\user_data_dir"

    return user_data_path

def get_extension_path() -> str:

    """
    Return the path where the extension is stored.
    """

    directory_ls = os.listdir(get_actual_path()) # List the files in the current directory

    # Search for the extension 
    for file in directory_ls:
        if "Chrome-Web-Store" in file:
            extension_path = get_actual_path() + "\\" + file
            break

    if not extension_path:
        raise Exception("[!] Extension not found")
    
    return extension_path