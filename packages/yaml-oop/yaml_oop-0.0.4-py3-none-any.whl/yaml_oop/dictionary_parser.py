import sys
import os
from yaml_oop.custom_errors import (
    KeySealedError,
    ConflictingDeclarationError,
    NoOverrideError,
    InvalidVariableError,
    InvalidInstantiationError,
    InvalidDeclarationError,
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

import yaml_oop.parser as parser
import yaml_oop.definitions as definitions
import yaml_oop.config_parser as config_parser
import yaml_oop.variable_parser as variable_parser
import yaml_oop.next_parser as next_parser


def process_dictionary(
    super_data,
    super_key_or_index,
    sub_data: dict,
    base_data: dict,
    sub_properties: definitions.Declarations,
    base_properties: definitions.Declarations,
    directory: str,
    loader
):

    if definitions.BASE_CONFIG_DECLARATION in base_data:
        config_parser.process_base_config_declaration(super_data=super_data,
                                                      super_key_or_index=super_key_or_index,
                                                      yaml_data=base_data,
                                                      yaml_properties=base_properties,
                                                      directory=directory,
                                                      loader=loader)

    # Map matches the base_data keys to the sub keys with their declarations.
    # sub_key_map Key = parsed key (no declaration)
    # sub_key_map Value = [Full key, declaration]
    sub_key_map = map_parsed_sub_keys(sub_data)

    # List containing:
    # [base_key (without declarations), full_key (with_declaratios), list of declarations]
    base_key_list = list_parsed_base_keys(base_data)

    # Iterate through parsed base keys and perform inheritance logic
    for parsed_base_key, full_base_key, base_declarations in base_key_list:

        # Initialize base declaration logic
        base_key_is_abstract, base_key_is_sealed, base_key_is_private = False, False, False
        for base_declaration in base_declarations:
            if base_declaration in definitions.SUB_DECLARATIONS:
                full_base_key = parser.remove_key_declaration(base_data, full_base_key, base_declaration)
            match base_declaration:
                case definitions.ABSTRACT_DECLARATION:  # Must inherit
                    if contains_conflicting_declaration(base_data[full_base_key], {definitions.ABSTRACT_DECLARATION}):
                        raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: abstract, sealed, private.")
                    full_base_key = parser.remove_key_declaration(base_data, full_base_key, definitions.ABSTRACT_DECLARATION)
                    base_key_is_abstract = True
                case definitions.SEALED_DECLARATION:  # Cannot override
                    if contains_conflicting_declaration(base_data[full_base_key], {definitions.SEALED_DECLARATION}):
                        raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: abstract, sealed, private.")
                    base_key_is_sealed = True
                case definitions.PRIVATE_DECLARATION:  # Cannot inherit
                    if contains_conflicting_declaration(base_data[full_base_key], {definitions.PRIVATE_DECLARATION}):
                        raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: abstract, sealed, private.")
                    base_key_is_private = True
        if base_key_is_private:
            continue  # Do no inherit private keys

        # Sub inherits key from base if able
        if parsed_base_key not in sub_key_map:
            if base_properties.is_abstract or base_key_is_abstract:
                raise NotImplementedError(f"Base YAML declares abstract, but base key: '{parsed_base_key}' is not implemented in sub YAML: '{sub_data}'.")
            if contains_conflicting_declaration(base_data[full_base_key], set()):
                raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: abstract, sealed, private.")
            if sub_properties.is_overriding:
                # If override was declared for a key.
                # New keys are not inherited.
                continue
            remove_all_key_declarations(base_data[full_base_key], "key", definitions.PRIVATE_DECLARATION)
            sub_data[full_base_key] = base_data[full_base_key]
            continue
        sub_key, sub_declarations = sub_key_map.pop(parsed_base_key)

        # Catch case where type mismatch between base and sub occurs
        if sub_key in sub_data and is_type_mismatch(sub_data[sub_key], base_data[full_base_key]):
            raise TypeError(f"Type mismatch for base YAML key: '{full_base_key}': {type(base_data[full_base_key])}, and sub YAML key: '{sub_key}': {type(sub_data[sub_key])}.")

        # parsed_base_key is in sub_data
        # Execute sub declaration logic
        sub_key_is_overriding, sub_is_append_prepend_merge = False, False
        if not sub_declarations:
            if base_properties.is_sealed or base_key_is_sealed:
                raise KeySealedError(f"Cannot override base key: '{full_base_key}' when base key is sealed.")
        for sub_declaration in sub_declarations:
            # TO DO: Maybe conflicting declarations check can occur here without its own DFS
            match sub_declaration:
                case definitions.OVERRIDE_DECLARATION:
                    if base_key_is_sealed or sub_properties.is_sealed:
                        raise KeySealedError(f"Cannot override base key: '{full_base_key}' when base key is sealed.")
                    if sub_properties.is_overriding:
                        print(f"Warning: '{sub_key}' unnecessarily declares override while already overriding.")
                    if sub_key not in base_data:
                        print(f"Warning. Override was declared for variable: '{sub_key}', but no base variable exists to override. Ignoring override declaration.")
                    sub_key_is_overriding = True
                    sub_key = parser.remove_key_declaration(sub_data, sub_key, definitions.OVERRIDE_DECLARATION)
                case definitions.APPEND_SEQUENCE_DECLARATION:
                    if definitions.OVERRIDE_DECLARATION in sub_declarations or definitions.MERGE_SEQUENCE_DECLARATION in sub_declarations or definitions.PREPEND_SEQUENCE_DECLARATION in sub_declarations:
                        raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: override, append, prepend, merge.")
                    sub_is_append_prepend_merge = True
                    process_append_prepend(sub_data, sub_key, base_data, full_base_key, "append", directory, loader)
                    parser.remove_key_declaration(sub_data, sub_key, definitions.APPEND_SEQUENCE_DECLARATION)
                    break
                case definitions.PREPEND_SEQUENCE_DECLARATION:
                    if definitions.OVERRIDE_DECLARATION in sub_declarations or definitions.MERGE_SEQUENCE_DECLARATION in sub_declarations or definitions.APPEND_SEQUENCE_DECLARATION in sub_declarations:
                        raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: override, append, prepend, merge.")
                    sub_is_append_prepend_merge = True
                    process_append_prepend(sub_data, sub_key, base_data, full_base_key, "prepend", directory, loader)
                    parser.remove_key_declaration(sub_data, sub_key, definitions.PREPEND_SEQUENCE_DECLARATION)
                    break
                case definitions.MERGE_SEQUENCE_DECLARATION:
                    if definitions.OVERRIDE_DECLARATION in sub_declarations or definitions.PREPEND_SEQUENCE_DECLARATION in sub_declarations or definitions.APPEND_SEQUENCE_DECLARATION in sub_declarations:
                        raise ConflictingDeclarationError(f"Base key: '{parsed_base_key}' cannot declare more than one of: override, append, prepend, merge.")
                    sub_is_append_prepend_merge = True
                    process_merge(sub_data, sub_key, base_data, full_base_key, directory, loader)
                    parser.remove_key_declaration(sub_data, sub_key, definitions.MERGE_SEQUENCE_DECLARATION)
                    break

        if sub_is_append_prepend_merge:
            continue

        if type(base_data[full_base_key]) is dict:
            process_dictionary(super_data=super_data,
                               super_key_or_index=super_key_or_index,
                               sub_data=sub_data[sub_key], 
                               base_data=base_data[full_base_key], 
                               sub_properties=definitions.Declarations(sub_properties.is_overriding or sub_key_is_overriding, sub_properties.is_abstract, sub_properties.is_sealed),
                               base_properties=definitions.Declarations(base_properties.is_overriding, base_properties.is_abstract or base_key_is_abstract, base_properties.is_sealed or base_key_is_sealed),
                               directory=directory, 
                               loader=loader)
        elif type(base_data[full_base_key]) is list:
            # Append and prepend declarations should not reach this point
            if sub_key_is_overriding is False and sub_properties.is_overriding is False:
                raise NoOverrideError(f"No override declared for '{sub_key}' list despite having matching key in base_config.")
            # Maintain sub_data's values.

    # Process remaining sub_data keys that did not match base_data keys
    for sub_key, sub_declarations in sub_key_map.values():
        if definitions.OVERRIDE_DECLARATION in sub_declarations:
            sub_key = parser.remove_key_declaration(sub_data, sub_key, definitions.OVERRIDE_DECLARATION)
            if sub_properties.is_overriding:
                print(f"Warning: '{sub_key}' unnecessarily declares override while already overriding.")
            sub_properties.is_overriding = True
        if definitions.ABSTRACT_DECLARATION in sub_declarations:
            sub_key = parser.remove_key_declaration(sub_data, sub_key, definitions.ABSTRACT_DECLARATION)
            if sub_properties.is_abstract:
                print(f"Warning: '{sub_key}' unnecessarily declares abstract while already abstract.")
            sub_properties.is_abstract = True
        if definitions.SEALED_DECLARATION in sub_declarations:
            sub_key = parser.remove_key_declaration(sub_data, sub_key, definitions.SEALED_DECLARATION)
            if sub_properties.is_sealed:
                print(f"Warning: '{sub_data}' unnecessarily declares sealed while already sealed.")
            sub_properties.is_sealed = True
        if definitions.APPEND_SEQUENCE_DECLARATION in sub_declarations or definitions.PREPEND_SEQUENCE_DECLARATION in sub_declarations:
            raise InvalidDeclarationError(f"Base key: '{sub_key}' cannot declare append or prepend without a base key to inherit from.")
        next_parser.process_next(
            super_data=sub_data,
            super_key_or_index=sub_key,
            yaml_data=sub_data[sub_key],
            yaml_properties=sub_properties,
            directory=directory,
            loader=loader)


def process_append_prepend(sub_data: dict, sub_key: str, base_data: dict, base_key: str, mode: str, directory: str, loader):
    """Append sub_data's values to base_data's values inplace"""
    if definitions.SEALED_DECLARATION in parser.find_key_declarations(base_key):
        raise KeySealedError(f"Cannot append/prepend base key: '{base_key}' when base key is sealed.")
    if type(sub_data[sub_key]) is not list and sub_data[sub_key] is not None:
        raise TypeError(f"Expected a list for sub_data for append operation, got {type(sub_data[sub_key])}.")
    if type(base_data[base_key]) is not list and base_data[base_key] is not None:
        raise TypeError(f"Expected a list for base_data for append operation, got {type(base_data[base_key])}.")

    # TO DO: Test nested append prepend merge
    remove_all_key_declarations(base_data[base_key], "declaration", definitions.SEALED_DECLARATION)
    remove_all_key_declarations(base_data[base_key], "declaration", definitions.OVERRIDE_DECLARATION)
    remove_all_key_declarations(base_data[base_key], "key", definitions.PRIVATE_DECLARATION)
    # TO DO: How are variables processed in append prepend merge?
    config_parser.process_yaml(yaml_data=base_data[base_key],
                               variables={},
                               directory=directory,
                               loader=loader)

    if mode == "append":
        sub_data[sub_key] = base_data[base_key] + sub_data[sub_key]
    elif mode == "prepend":
        sub_data[sub_key] = sub_data[sub_key] + base_data[base_key]
    else:
        # Should not reach this point
        raise Exception("Incorrect mode arg in process_append_prepend function call. Please open a Github issue with your given input.")


def process_merge(sub_data: dict, sub_key: str, base_data: dict, base_key: str, directory: str, loader):
    """Merge base_data's list values into sub_data's list values inplace.
       Merging involving applying inheritance rules to each item of matching index in sub and base lists."""
    if definitions.SEALED_DECLARATION in parser.find_key_declarations(base_key):
        raise KeySealedError(f"Cannot append/prepend base key: '{base_key}' when base key is sealed.")
    if type(sub_data[sub_key]) is not list and sub_data[sub_key] != {}:
        raise TypeError(f"Expected a list for sub_data for append operation, got {type(sub_data[sub_key])}.")
    if type(base_data[base_key]) is not list and base_data[base_key] != {}:
        raise TypeError(f"Expected a list for base_data for append operation, got {type(base_data[base_key])}.")

    total_length = max(len(sub_data[sub_key]), len(base_data[base_key]))
    for i in range(total_length):
        if i >= len(sub_data[sub_key]):
            sub_data[sub_key].append(base_data[base_key][i])
        elif i >= len(base_data[base_key]):
            pass
        elif sub_data[sub_key][i] is None:
            sub_data[sub_key][i] = base_data[base_key][i]
        elif base_data[base_key][i] is None:
            pass
        else: 
            # Sub and base both have values, so apply inheritance rules
            # Apply inheritance rules only if both sub and base are dicts
            if (type(sub_data[sub_key][i]) is not dict and base_data[base_key][i] is not None) or \
               (type(base_data[base_key][i]) is not dict and sub_data[sub_key][i] is not None):
                raise TypeError(f"Cannot merge list items at index {i} for base key: '{base_key}' and sub key: '{sub_key}' because one or both items are not dictionaries.")
            process_dictionary(super_data=sub_data[sub_key],
                               super_key_or_index=i,
                               sub_data=sub_data[sub_key][i],
                               base_data=base_data[base_key][i],
                               sub_properties=definitions.Declarations(False, False, False),
                               base_properties=definitions.Declarations(False, False, False),
                               directory=directory,
                               loader=loader)


def remove_all_key_declarations(data, mode: str, declaration: str):
    """Removes all keys and subkeys that declares declaration inplace.
       Mode == "declaration" to remove declaration.
       Mode == "key" to remove entire key."""
    if type(data) is dict:
        for key in list(data.keys()):
            if declaration in parser.find_key_declarations(key):
                if mode == "key":
                    data.pop(key)
                elif mode == "declaration":
                    parser.remove_key_declaration(data, key, declaration)
            else:
                remove_all_key_declarations(data[key], mode, declaration)
    if type(data) is list:
        for item in data:
            remove_all_key_declarations(item, mode, declaration)
    return data


def map_parsed_sub_keys(sub_data: dict) -> dict:
    """Map parsed sub keys to their declaration and full key.
       Key = parsed key (no declaration)
       Value = full key, list of declarations."""
    key_map = {}
    for full_key in sub_data:
        declarations = parser.find_key_declarations(full_key)  
        parsed_key = parser.key_without_declaration(full_key)
        key_map[parsed_key] = (full_key, declarations)
    return key_map


def list_parsed_base_keys(base_data: dict) -> list:
    """List parsed base keys to their declaration and full key.
       Value = parsed key, full key, list of declarations."""
    key_list = []
    for full_key in base_data:
        declarations = parser.find_key_declarations(full_key)    
        parsed_key = parser.key_without_declaration(full_key)
        key_list.append((parsed_key, full_key, declarations))
    return key_list


def is_type_mismatch(sub_data, base_data) -> bool:
    """Returns true if types of base and sub prevent inheritance."""
    if sub_data is None or base_data is None:
        return False
    # Empty dicts or lists are essentially None
    elif not sub_data or not base_data:
        return False
    elif type(base_data) is not type(sub_data):
        return True
    # sub and base are both non-empty dicts or non-empty lists 
    return False


# TO DO: Inefficient. Should not iterate through all child keys.
def contains_conflicting_declaration(data, found_declarations: set) -> bool:
    """Returns true if members of base data contain one or more of declarations arg.
       A conflict is defined as more than one declaration type of abstract, sealed, and private."""
    if type(data) is dict:
        for key in data:
            declarations = parser.find_key_declarations(key)
            found_declarations_copy = found_declarations.copy()
            for declaration in declarations:
                if declaration in definitions.BASE_DECLARATIONS:
                    found_declarations_copy.add(declaration)

            if len(found_declarations_copy) > 1:
                return True
            elif contains_conflicting_declaration(data[key], found_declarations_copy):
                return True
    elif type(data) is list:
        for item in data:
            if contains_conflicting_declaration(item, found_declarations.copy()):
                return True
    return False
