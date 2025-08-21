import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from yaml_oop.custom_errors import (
    KeySealedError, 
    ConflictingDeclarationError, 
    NoOverrideError, 
    InvalidVariableError, 
    InvalidInstantiationError, 
    InvalidDeclarationError
)

import yaml_oop.parser as parser
import yaml_oop.definitions as definitions
import yaml_oop.config_parser as config_parser
import yaml_oop.variable_parser as variable_parser
import yaml_oop.next_parser as next_parser


def process_next(super_data, super_key_or_index, yaml_data, yaml_properties: definitions.Declarations, directory: str, loader):
    """Moves through the yaml data while there is not base_data to inherit."""

    if type(yaml_data) is list:
        i = 0
        while i < len(yaml_data):
            item = yaml_data[i]
            if type(item) is dict and definitions.BASE_CONFIG_DECLARATION in item:
                config_parser.process_base_config_declaration(
                    super_data=yaml_data,
                    super_key_or_index=i,
                    yaml_data=item,
                    yaml_properties=yaml_properties,
                    directory=directory,
                    loader=loader)
                if type(yaml_data[i]) is list:
                    # List insertion
                    yaml_data[i:i + 1] = yaml_data[i]
            else:
                process_next(
                    super_data=yaml_data,
                    super_key_or_index=i,
                    yaml_data=item,
                    yaml_properties=yaml_properties,
                    directory=directory,
                    loader=loader)
                i += 1

    elif type(yaml_data) is dict:
        if definitions.BASE_CONFIG_DECLARATION in yaml_data:
            config_parser.process_base_config_declaration(
                super_data=super_data,
                super_key_or_index=super_key_or_index,
                yaml_data=yaml_data,
                yaml_properties=yaml_properties,
                directory=directory,
                loader=loader)
        for key in list(yaml_data.keys()):
            declarations = parser.find_key_declarations(key)
            if definitions.OVERRIDE_DECLARATION in declarations:
                key = parser.remove_key_declaration(yaml_data, key, definitions.OVERRIDE_DECLARATION)
                if yaml_properties.is_overriding:
                    print(f"Warning: '{key}' unnecessarily declares override while already overriding.")
                # TO DO: Override unecessarily declared
                yaml_properties.is_overriding = True
            if definitions.ABSTRACT_DECLARATION in declarations:
                key = parser.remove_key_declaration(yaml_data, key, definitions.ABSTRACT_DECLARATION)
                if yaml_properties.is_abstract:
                    print(f"Warning: '{key}' unnecessarily declares abstract while already abstract.")
                yaml_properties.is_abstract = True
            if definitions.SEALED_DECLARATION in declarations:
                key = parser.remove_key_declaration(yaml_data, key, definitions.SEALED_DECLARATION)
                if yaml_properties.is_sealed:
                    print(f"Warning: '{key}' unnecessarily declares sealed while already sealed.")
                yaml_properties.is_sealed = True
            if definitions.APPEND_SEQUENCE_DECLARATION in declarations or definitions.PREPEND_SEQUENCE_DECLARATION in declarations:
                raise InvalidDeclarationError(f"Base key: '{key}' cannot declare append or prepend without a base key to inherit from.")
            process_next(
                super_data=yaml_data,
                super_key_or_index=key,
                yaml_data=yaml_data[key],
                yaml_properties=yaml_properties,
                directory=directory,
                loader=loader)
