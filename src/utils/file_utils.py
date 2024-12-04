import os
import sys

def get_project_root_abs_path():
    # Get the directory of this file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the root directory of the project by going up two levels from this directory
    project_root = os.path.abspath(os.path.join(script_dir, '../..'))

    return project_root

def get_abs_path(relative_path):
    # Get the root directory of the project
    project_root = get_project_root_abs_path()

    # Get the absolute path of the file by joining the project root and the relative path
    file_path = os.path.join(project_root, relative_path)

    return file_path

# This function is used to get the absolute path of a file at runtime
# The given path should be relative to the root of the project
# Handles both normal Python environment and PyInstaller bundle
def format_path_from_root(relative_path):
    if getattr(sys, 'frozen', False):
        # The application is running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # The application is running in a normal Python environment
        return get_abs_path(relative_path)