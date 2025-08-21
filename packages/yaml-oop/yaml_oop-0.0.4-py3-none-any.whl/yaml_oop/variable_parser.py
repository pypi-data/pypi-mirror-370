import sys
import os
import yaml
import logging
from typing import Tuple
from yaml_oop.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

import yaml_oop.definitions as definitions
import yaml_oop.parser as parser
import yaml_oop.config_parser as config_parser
import yaml_oop.dictionary_parser as dictionary_parser


def process_variables(data, super_data, super_key_or_index, parent_variables: dict, is_base_config: bool):
    if is_base_config is False:  # Do not process variables within base_config declaration as those variables should be processed during instantiation
        parent_variables = add_variables(data, parent_variables.copy())
    replace_with_variables(data, super_data, super_key_or_index, parent_variables, is_base_config)


def inherit_variables(base_data, config_info) -> dict:
    """When inheriting variables from instantiation, search both base and sub data for variable config and variable declarations.
       Then add variables to existing variable dict with inheritance and instantiation rules inplace.
       Pops variable decarations from data inplace.
       Returns variable dictionary."""

    base_variables = add_variables(base_data, {})
    instantiation_variables = add_variables(config_info, base_variables)
    return instantiation_variables


def replace_with_variables(data, super_data, super_key_or_index, variables: dict, is_base_config: bool):
    """Replaces all values in dicts and all items in lists, as well as child nodes with corresponding variable in data inplace.
       Searches for declarations of variables and processes them while replacing.
       Should be called when inheriting all of base_data when child nodes of base_data are unknown."""
    if type(data) is dict:
        for key in list(data.keys()):
            if key == definitions.BASE_CONFIG_DECLARATION:
                is_base_config = True

            if is_base_config and definitions.VARIABLE_DECLARATION in find_variable_declarations(key):
                carryover_variables = {variable_key: value for variable_key, value in data[key].items() if definitions.CARRYOVER_DECLARATION in variable_key}
                for carryover_key in carryover_variables:
                    carryover_key_declarations, parsed_carryover_key = find_variable_key_declarations(carryover_key)
                    if parsed_carryover_key in variables:
                        data[key][carryover_key] = variables[parsed_carryover_key][0]
                        carryover_key = parser.remove_key_declaration(data[key], carryover_key, definitions.CARRYOVER_DECLARATION)
                        if definitions.ABSTRACT_DECLARATION in carryover_key_declarations:
                            parser.remove_key_declaration(data[key], carryover_key, definitions.ABSTRACT_DECLARATION)
            elif definitions.OPTIONAL_DECLARTION in parser.find_key_declarations(key):
                key = parser.remove_key_declaration(data, key, definitions.OPTIONAL_DECLARTION)
                if type(data[key]) is not str:
                    raise InvalidVariableError(f"Optional declaration must be associated with a string value. Key {key} is type: {type(data[key])}")
                if data[key] in variables:
                    replace_value(data, key, variables)
                else:
                    data.pop(key)
                    if data == [] or data == {}:
                        super_data.pop(super_key_or_index)
            elif type(data[key]) is dict or type(data[key]) is list:
                process_variables(data[key], data, key, variables, is_base_config)
            else:
                replace_value(data, key, variables)
    elif type(data) is list:
        i = 0
        while i < len(data):
            if type(data[i]) is str and data[i] == definitions.BASE_CONFIG_DECLARATION:
                is_base_config = True

            if type(data[i]) is str and definitions.OPTIONAL_DECLARTION in parser.find_key_declarations(data[i]):
                data[i] = " ".join(data[i].split()[1:])
                if data[i] in variables:
                    replace_value(data, i, variables)
                    i += 1
                else:
                    data.pop(i)
            elif type(data[i]) is dict or type(data[i]) is list:
                if is_base_config and type(data[i]) is str and definitions.VARIABLE_DECLARATION in find_variable_declarations(data[i]):
                    for j in data[i]:
                        if j == definitions.BASE_CONFIG_PATH:
                            replace_value(data[i], j, variables)
                            i += 1
                else:
                    element = data[i]
                    process_variables(data[i], data, i, variables, is_base_config)
                    if element != {} or element != []: # Data element was not popped
                        i += 1
            else:
                replace_value(data, i, variables)
                i += 1


def add_variables(data, parent_variables: dict) -> dict:
    """Search data for variable config and variable declarations.
       Then add variables to existing variable dict with inheritance rules inplace.
       Pops variable decarations from data inplace.
       Should be called at each node before applying inheritance rules to data keys.
       Returns modified variable dictionary inplace."""
    if type(data) is dict:
        for key in list(data.keys()):
            if type(key) is not str:
                continue
            declarations = find_variable_declarations(key)
            if definitions.VARIABLE_DECLARATION in declarations:
                variable_declaration_to_keys_declarations(declarations, data[key])
                merge_variables(parent_variables, data[key])
                data.pop(key)
    elif type(data) is list:
        i = 0
        while i < len(data):
            if type(data[i]) is dict and len(data[i]) == 1 and \
                any(definitions.VARIABLE_DECLARATION in key for key in data[i]):
                for key in data[i]: # Should be only 1 key
                    declarations = find_variable_declarations(key)
                    variable_declaration_to_keys_declarations(declarations, data[i])
                    merge_variables(parent_variables, data[i][key])
                    data.pop(i)
            else:
                i += 1
    return parent_variables


def add_injected_variables(injected_variables: dict) -> dict:
    """Converts injected variables into modified variable dict format.
       Variable dict format:
       Key = key without declaration (key is the substring to be replaced in YAML)
       Value = (replacement substring, declarations set)"""
    return_variables = {}
    for variable in injected_variables:
        declarations, parsed_key = find_variable_key_declarations(variable)
        return_variables[parsed_key] = (injected_variables[variable], declarations)
    return return_variables


def merge_variables(parent_variables: dict, child_variables) -> dict:
    """Add child variables to parent variables inplace.
       Variable dict format:
       Key = key without declaration (key is the substring to be replaced in YAML)
       Value = (replacement substring, declarations set)"""
    if not child_variables:
        return parent_variables
    
    if type(child_variables) != dict:
        raise InvalidVariableError(f"Variable must be a dict. Invalid value: '{child_variables}'")
    
    for child_key in child_variables:
        child_declarations, child_parsed_key = find_variable_key_declarations(child_key)
        new_variable = (child_variables[child_key], child_declarations)

        if not child_declarations:
            if child_parsed_key in parent_variables:
                raise NoOverrideError(f"Cannot override variable: '{child_parsed_key}' when child variable does not declare override.")
            else:
                parent_variables[child_parsed_key] = new_variable
        if definitions.ABSTRACT_DECLARATION in child_declarations:
            if child_parsed_key in parent_variables and definitions.OVERRIDE_DECLARATION not in child_declarations:
                raise NoOverrideError(f"Cannot override variable: '{child_parsed_key}' when parent variable does not declare override.")
            else:
                parent_variables[child_parsed_key] = new_variable
        if definitions.SEALED_DECLARATION in child_declarations:
            if child_parsed_key in parent_variables and definitions.OVERRIDE_DECLARATION not in child_declarations:
                raise NoOverrideError(f"Cannot override variable: '{child_parsed_key}' when child variable is sealed.")
            else:
                parent_variables[child_parsed_key] = new_variable
        if definitions.OVERRIDE_DECLARATION in child_declarations:
            if child_parsed_key not in parent_variables:
                print(f"Warning. Override was declared for variable: '{child_parsed_key}', but no parent variable exists to override.")
            elif definitions.SEALED_DECLARATION in parent_variables[child_parsed_key][1]:
                raise KeySealedError(f"Cannot override variable: '{child_parsed_key}' when parent variable is sealed.")
            parent_variables[child_parsed_key] = new_variable
    return parent_variables


def replace_value(data, key_or_index, variables: dict):
    """For non-string value in data, replaces any matching data_value with variable value inplace.
       For string value in data, replaces any matching substring of data_value with variable value inplace.
       Returns replaced value."""
    if type(data[key_or_index]) is str:
        for variable_key, variable_value in variables.items():
            if type(data[key_or_index]) is not str:
                break # value was replaced with a non-string; multiple replacements not possible
            elif variable_key in data[key_or_index]:
                if definitions.ABSTRACT_DECLARATION in variable_value[1]:
                    raise NotImplementedError(f"Abstract variable {variable_key} cannot be used before being overriden.") 
                if type(variable_value[0]) is str: # TO DO: Multiple string replacements possible. But what if string replacements are ambiguous?
                    data[key_or_index] = data[key_or_index].replace(variable_key, variable_value[0])
                else:
                    data[key_or_index] = variable_value[0]
                    break # value was replaced with a non-string; multiple replacements not possible
    else:
        if data[key_or_index] in variables.items():
            data[key_or_index] = variables[data[key_or_index]][0]
    

def find_variable_declarations(key: str) -> set:
    """Returns all declarations within the potential variable declaration."""
    if key == "" or key is None:
        return set()
    else:
        declarations = set()
        for item in key.split(" "):
            if item in definitions.VARIABLE_DECLARATIONS or item == definitions.VARIABLE_DECLARATION:
                declarations.add(item)
        return declarations


def find_variable_key_declarations(key: str) -> tuple[set, str]:
    """Returns all declarations and key with no declarations within a variable key."""
    if key == "" or key is None:
        return set(), key
    else:
        declarations = set()
        for item in key.split(" "):
            if item in definitions.VARIABLE_DECLARATIONS:
                declarations.add(item)
        return declarations, key.split(" ")[-1]


def variable_declaration_to_keys_declarations(declarations: set, variables: dict):
    """Replaces all variable's declarations to key declarations inplace."""
    
    if not variables:
        return

    if type(variables) is not dict:
        raise InvalidVariableError(f"Variables must be a dict.")

    is_abstract, is_sealed, is_override, is_optional = False, False, False, False
    if definitions.ABSTRACT_DECLARATION in declarations:
        is_abstract = True
    if definitions.SEALED_DECLARATION in declarations:
        is_sealed = True
    if definitions.OVERRIDE_DECLARATION in declarations:
        is_override = True
    if definitions.OPTIONAL_DECLARTION in declarations:
        is_optional = True

    for key in list(variables.keys()):
        if is_abstract:
            key = parser.add_key_declaration(variables, key, definitions.ABSTRACT_DECLARATION)
        if is_sealed:
            key = parser.add_key_declaration(variables, key, definitions.SEALED_DECLARATION)
        if is_override:
            key = parser.add_key_declaration(variables, key, definitions.OVERRIDE_DECLARATION)
        if is_optional:
            key = parser.add_key_declaration(variables, key, definitions.OPTIONAL_DECLARTION)
        