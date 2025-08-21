import pytest
import os
import sys
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
sys.path.append(BASE_DIR)

from tests.test import assert_result_config
from yaml_oop.parser import oopify
from yaml_oop.custom_errors import KeySealedError, ConflictingDeclarationError, NoOverrideError, InvalidDeclarationError


def test_variable():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'variable', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'variable', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_multiple_variable():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'multiple_variables', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'multiple_variables', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'instantiation', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_multiple_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'multiple_instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'multiple_instantiation', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_abstract_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'abstract_variables', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'abstract_variables', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_abstract_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'failed_abstract_variables', 'sub_config.yaml')
    with pytest.raises(NotImplementedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is NotImplementedError


def test_failed_sealed_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'failed_sealed_variables', 'sub_config.yaml')
    with pytest.raises(KeySealedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is KeySealedError


def test_nested_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'nested_instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'nested_instantiation', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_inject_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'inject_variables', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'inject_variables', 'result_config.yaml')
    variable_injection = {
        'var1': "injected_value",
        'var2': {
            'subkey1': "sub_value1",
            'subkey2': "sub_value2"
        },
        'var3': [1, 2, 3, 4, 5],
        'var4': {
            'subkey3': "sub_value3"
        }
    }
    assert_result_config(input_path, expected_path, TESTS_DIR, variable_injection)


def test_inject_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables', 'inject_instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables', 'inject_instantiation', 'result_config.yaml')
    variable_injection = {
        '<var3>': 'injected_value3',
        '<base_config1>': 'test_variables/inject_instantiation/base_config1.yaml',
        '<base_config2>': 'test_variables/inject_instantiation/base_config2.yaml',
        '<base_config3>': [{
            '(path)': 'test_variables/inject_instantiation/base_config3.yaml',
            '(variables)': {
                '<var1>': 'injected_value1',
                '(carryover) <var3>': ''
            }
        }]
    }
    assert_result_config(input_path, expected_path, TESTS_DIR, variable_injection)