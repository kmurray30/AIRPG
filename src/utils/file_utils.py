import os
import sys
from dotenv import load_dotenv

def get_abs_path(relative_path):
    # Get the directory of this file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the root directory of the project by going up two levels from this directory
    project_root = os.path.abspath(os.path.join(script_dir, '../..'))

    # Generate the absolute path of the file by joining the project root and the relative path
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

def init_dotenv():
    # Get the path of the .env file
    if getattr(sys, 'frozen', False):
        # The application is running in a PyInstaller bundle
        env_path = os.path.join(sys._MEIPASS, '.env')
    else:
        # The application is running in a normal Python environment
        env_path = format_path_from_root('.env')
    load_dotenv(dotenv_path=env_path)