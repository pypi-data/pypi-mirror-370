import sys
import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

import yaml_oop.definitions as definitions
import yaml_oop.config_parser as config_parser
import yaml_oop.variable_parser as variable_parser


def oopify(file_path: str, directory: str, Loader, variables=None):
    """Read a YAML file, process it with inheritance rules, and return the complete YAML data as dict or list."""
    if variables is None:
        variables = {}

    yaml_data = {}
    try:
        with open(file_path, 'r') as file:
            yaml_data = yaml.load(file, Loader=Loader)
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        return None

    variables = variable_parser.add_injected_variables(variables)
    yaml_data = config_parser.process_yaml(yaml_data=yaml_data, directory=directory, variables=variables, loader=Loader)
    return yaml_data


def key_without_declaration(key: str) -> str:
    """Returns the key without any declarations."""
    if key == "" or key is None:
        return ""
    return " ".join([
        item for item in key.split()
        if item not in definitions.BASE_DECLARATIONS
           and item not in definitions.SUB_DECLARATIONS
    ])


def find_key_declarations(key: str) -> set:
    """Returns all declarations within the key."""
    if key == "" or key is None:
        return set()
    else:
        declarations = set()
        for item in key.split(" "):
            if item in definitions.BASE_DECLARATIONS or item in definitions.SUB_DECLARATIONS:
                declarations.add(item)
        return declarations


def remove_key_declaration(data: dict, key: str, declaration: str) -> str:
    """Remove a declaration from a specific the key of the YAML data inplace.
       Returns the new key without the declaration"""

    new_key = key.replace(declaration + " ", "")
    new_data = data[key]
    data.pop(key, None)
    data[new_key] = new_data
    return new_key


def add_key_declaration(data: dict, key: str, declaration: str): 
    """Adds a declaration to a key in the YAML data."""
    new_key = declaration + " " + key
    new_data = data[key]
    data.pop(key)
    data[new_key] = new_data
    return new_key
