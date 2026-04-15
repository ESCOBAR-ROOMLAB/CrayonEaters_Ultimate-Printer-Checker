# This module will help us retrieve the absolute path for the files that we operate in the program
import os

# This module will let the program itself determine if is being run as a bundle or as a script. It also allows
# us to terminate the program safely under certain conditions
import sys

#########################################################################################################################################

# HELPER FUNCTION: GET THE RIGHT PATH FOR FILES
# ---------------------------------------------
# def alternate_get_absolute_path(file_name):

#     """Returns the absolute path for the file argumented"""

#     if getattr(sys, 'frozen', False):
#         # If the application is run as a bundle (e.g., by PyInstaller)
#         BASE_PATH = os.path.dirname(sys.executable)
#     else:
#         # If running as a normal .py script
#         BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    
#     file_absolute_path = os.path.join(BASE_PATH, file_name)
#     return file_absolute_path


def get_absolute_path(relative_path):
    """
    Get the absolute path to a resource, works for both development and
    for a PyInstaller bundled application.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This is the base path to where your assets are bundled.
        base_path = sys._MEIPASS
    except Exception:
        # If _MEIPASS is not defined, we are in development mode.
        # The base path is just the directory of the main script.
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)