import pytest
import os
import sys
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
sys.path.append(BASE_DIR)

import yaml_oop.config_parser as config_parser
from yaml_oop.parser import oopify


def assert_result_config(input_path, expected_path, directory, variables=None):
    if variables is None:
        variables = {}
    input_data = oopify(file_path=input_path, directory=directory, Loader=yaml.FullLoader, variables=variables)
    expected_data = config_parser.read_yaml(file_path=expected_path, loader=yaml.FullLoader)
    if input_data == {} or None:
        pytest.fail("Could not load input and result YAML files")
    assert input_data == expected_data, f"Expected {expected_data}, but got {input_data}"
