"""
Test the find_config function
"""

import os
import sys
import pytest
from src.shell import find_config


def test_find_config():
    """
    Test the find_config function
    """
    # Test with the config file only exists in the first default path
    if not os.path.exists("./config.json"):
        with open("./config.json", "w") as f:
            f.write("{}")
    assert find_config() == "./config.json"

    # Test with the config file only exists in the second default path
    if os.path.exists("./config.json"):
        os.remove("./config.json")
    if not os.path.exists("../config.json"):
        with open("../config.json", "w") as f:
            f.write("{}")
    assert find_config() == "../config.json"

    # Test with the config file exists in both paths
    if not os.path.exists("./config.json"):
        with open("./config.json", "w") as f:
            f.write("{}")
    if not os.path.exists("../config.json"):
        with open("../config.json", "w") as f:
            f.write("{}")
    assert find_config() == "./config.json"

    # Test with the config file does not exist in both paths
    if os.path.exists("./config.json"):
        os.remove("./config.json")
    if os.path.exists("../config.json"):
        os.remove("../config.json")
    assert find_config() is None
