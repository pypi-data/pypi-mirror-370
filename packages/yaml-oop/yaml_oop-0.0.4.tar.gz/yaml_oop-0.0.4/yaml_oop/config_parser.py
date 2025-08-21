import sys
import os
import yaml
from yaml_oop.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError,
    InvalidInstantiationError,
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

import yaml_oop.parser as parser
import yaml_oop.definitions as definitions
import yaml_oop.dictionary_parser as dictionary_parser
import yaml_oop.variable_parser as variable_parser
import yaml_oop.next_parser as next_parser


# To do: what happens when you declare !!int and !!float values??
# To do: test loaders
# TO DO: yaml anchors and special stuff
# TO DO: Space in yaml keys
# Infinite loops in find_base_config_declarations
def process_yaml(yaml_data, directory: str, variables: dict, loader):
    """Process the root YAML config file inplace."""

    if definitions.ABSTRACT_CONFIG_DECLARATION in yaml_data:
        raise NotImplementedError(
            "Cannot process an abstract YAML file. "
            "Abstract objects must be inherited in (base_config) declarations.")
    if definitions.SEALED_CONFIG_DECLARATION in yaml_data:
        yaml_data.pop(definitions.SEALED_CONFIG_DECLARATION)

    config_to_root_key_declarations(yaml_data)

    variable_parser.process_variables(yaml_data, None, None, variables, False)
    # Second process_variables call ensures that injected variables are processed correctly.
    variable_parser.process_variables(yaml_data, None, None, variables, False)

    next_parser.process_next(
        super_data=None,
        super_key_or_index=None,
        yaml_data=yaml_data,
        yaml_properties=definitions.Declarations(False, False, False),
        directory=directory,
        loader=loader)

    # Removes base declarations that are a part of the root config.
    # Removes sub declarations that were not found earlier.
    # Process_dictionary does not compare sub keys that have no equivalent base keys.
    for declaration in definitions.BASE_DECLARATIONS | definitions.SUB_DECLARATIONS:
        dictionary_parser.remove_all_key_declarations(yaml_data, "declaration", declaration)

    if dictionary_parser.contains_conflicting_declaration(yaml_data, set()):
        raise ConflictingDeclarationError(f"'{yaml_data}' cannot declare more than one of: abstract, sealed, private.")

    return yaml_data


def process_base_config_declaration(
    super_data,
    super_key_or_index,
    yaml_data: dict,
    yaml_properties: definitions.Declarations,
    directory: str,
    loader
):
    """Find the base_config declaration in the YAML data and append the base config's content to sub_data inplace."""

    if definitions.BASE_CONFIG_DECLARATION not in yaml_data:
        return

    base_config_data = yaml_data.pop(definitions.BASE_CONFIG_DECLARATION)
    base_configs = []
    if type(base_config_data) is list:  # Multiple inheritance case.
        for base_config in base_config_data:
            base_configs.append(base_config)
    else:  # Single inheritance case.
        base_configs.append(base_config_data)

    for config_info in base_configs:
        base_data, instantiation_variables = {}, {}
        if type(config_info) is str:  # Only file path
            base_data = read_yaml(file_path=os.path.join(directory, config_info), loader=loader)
        elif type(config_info) is dict:  # File path and variables
            if (definitions.BASE_CONFIG_PATH not in config_info.keys() or
                len(config_info.keys()) != 2 or not
                any(definitions.VARIABLE_DECLARATION in key for key in config_info)):
                raise InvalidInstantiationError(
                    f"Instantiation with {definitions.BASE_CONFIG_DECLARATION} must include only "
                    f"{definitions.BASE_CONFIG_PATH} key with string value and "
                    f"{definitions.VARIABLE_DECLARATION} key with a dict value."
                )
            base_config_path = config_info[definitions.BASE_CONFIG_PATH]
            if type(base_config_path) is not str:
                raise InvalidInstantiationError(
                    f"Instantiation with {definitions.BASE_CONFIG_DECLARATION} must include only "
                    f"{definitions.BASE_CONFIG_PATH} key with string value and "
                    f"{definitions.VARIABLE_DECLARATION} key with a dict value."
                )
            base_data = read_yaml(file_path=os.path.join(directory, base_config_path), loader=loader)
            instantiation_variables = variable_parser.inherit_variables(base_data, config_info)

        config_to_root_key_declarations(base_data)
        variable_parser.process_variables(base_data, None, None, instantiation_variables, False)

        # Inherit
        base_properties = definitions.Declarations(False, False, False)
        if type(base_data) is list and type(yaml_data) is dict and yaml_data != {}:
            raise TypeError(f"Base config '{base_data}' is a list, but yaml_data is a dictionary.")
        elif type(base_data) is dict and type(yaml_data) is dict:
            dictionary_parser.process_dictionary(
                super_data=super_data,
                super_key_or_index=super_key_or_index,
                sub_data=yaml_data,
                base_data=base_data,
                sub_properties=yaml_properties,
                base_properties=base_properties,
                directory=directory,
                loader=loader
            )
        elif type(base_data) is list and yaml_data == {}:
            if type(super_data) is dict:
                key = super_key_or_index
                if base_properties.is_abstract and key not in base_data:
                    raise NotImplementedError(f"Base config declares abstract, but key '{key}' is not implemented in '{yaml_data}.")
                super_data[key] = base_data
            elif type(super_data) is list:
                index = int(super_key_or_index)
                super_data[index] = base_data
        else:
            # Should not reach this point
            raise TypeError(f"Type mismatch for {base_data}. Cannot parse type {type(base_data)}.")


def config_to_root_key_declarations(yaml_data):
    """Replaces all yaml_file's config declarations to key declarations inplace."""
    
    if type(yaml_data) is not dict:
        return

    abstract_config, sealed_config, override_config = False, False, False
    if definitions.ABSTRACT_CONFIG_DECLARATION in yaml_data:
        abstract_config = True
        yaml_data.pop(definitions.ABSTRACT_CONFIG_DECLARATION)
    if definitions.SEALED_CONFIG_DECLARATION in yaml_data:
        sealed_config = True
        yaml_data.pop(definitions.SEALED_CONFIG_DECLARATION)
    if definitions.OVERRIDE_CONFIG_DECLARATION in yaml_data:
        override_config = True
        yaml_data.pop(definitions.OVERRIDE_CONFIG_DECLARATION)

    for key in list(yaml_data.keys()):
        if key == definitions.BASE_CONFIG_DECLARATION:
            continue
        if key == definitions.VARIABLE_DECLARATION:
            continue

        if abstract_config:
            key = parser.add_key_declaration(yaml_data, key, definitions.ABSTRACT_DECLARATION)
        if sealed_config:
            key = parser.add_key_declaration(yaml_data, key, definitions.SEALED_DECLARATION)
        if override_config:
            key = parser.add_key_declaration(yaml_data, key, definitions.OVERRIDE_DECLARATION)


def read_yaml(file_path: str, loader):
    """Read a YAML file and return its content."""

    yaml_data = {}
    try:
        with open(file_path, 'r') as file:
            yaml_data = yaml.load(file, Loader=loader)
    except Exception as e:
        raise Exception(f"Error reading YAML file: {e}")
    return yaml_data


def root_contains_config_declaration(base_data, config_declaration: str) -> bool:
    """Returns true if matching config declaration was declared in root of data"""
    if type(base_data) is list:
        for item in base_data:
            if item == config_declaration:
                return True
        return False
    elif type(base_data) is dict:
        if config_declaration in base_data:
            return True
        return False
    else:
        # Should not get to this point
        raise TypeError(f"Type mismatch for {base_data}. Cannot parse type {type(base_data)}.")

    
