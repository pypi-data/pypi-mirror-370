import json
import os

from synalinks.cli.constants import PROJECT_CONFIG_FILENAME


def is_inside_synalinks_project():
    """
    Check if the current directory contains a synalinks project config.

    Returns:
        (bool): True if a synalinks project is detected, False otherwise.
    """
    if os.path.exists(os.path.join(os.getcwd(), PROJECT_CONFIG_FILENAME)):
        return True
    return False


def get_synalinks_project_config():
    """
    Retrieve the configuration of the current synalinks project.

    Returns:
        (dict): The project configuration if inside a synalinks project,
            otherwise an empty dictionary.
    """
    if is_inside_synalinks_project():
        with open(
            os.path.join(os.getcwd(), PROJECT_CONFIG_FILENAME, "r", encoding="utf-8")
        ) as f:
            return json.loads(f.read())
    return {}
