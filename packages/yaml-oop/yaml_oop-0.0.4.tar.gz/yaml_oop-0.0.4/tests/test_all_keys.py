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


def test_simple_inheritance():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'simple_inheritance', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'simple_inheritance', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_multiple():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'multiple', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'multiple', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_list():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'list', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'list', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_simple_list():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'simple_list', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'simple_list', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_nested():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'nested', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'nested', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_abstract():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_abstract', 'sub_config.yaml')
    with pytest.raises(NotImplementedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is NotImplementedError


def test_partial_abstract_and_sealed():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'partial_abstract_and_sealed', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'partial_abstract_and_sealed', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_partial_abstract():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_partial_abstract', 'sub_config.yaml')
    with pytest.raises(NotImplementedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is NotImplementedError


def test_failed_sealed():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_sealed', 'sub_config.yaml')
    with pytest.raises(KeySealedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is KeySealedError


def test_failed_nested_sealed():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_nested_sealed', 'sub_config.yaml')
    with pytest.raises(KeySealedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is KeySealedError


def test_failed_abstract_sealed():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_abstract_sealed', 'sub_config.yaml')
    with pytest.raises(ConflictingDeclarationError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is ConflictingDeclarationError


def test_failed_list_to_dict():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_list_to_dict', 'sub_config.yaml')
    with pytest.raises(TypeError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is TypeError


def test_failed_dict_to_list():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_dict_to_list', 'sub_config.yaml')
    with pytest.raises(TypeError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is TypeError


def test_override():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'override', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'override', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_no_override():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_no_override', 'sub_config.yaml')
    with pytest.raises(NoOverrideError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is NoOverrideError


def test_private():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'private', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'private', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_abstract_private():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_abstract_private', 'sub_config.yaml')
    with pytest.raises(ConflictingDeclarationError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is ConflictingDeclarationError


def test_sub_is_list():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'sub_is_list', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'sub_is_list', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_invalid_append():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'failed_invalid_append', 'sub_config.yaml')
    with pytest.raises(InvalidDeclarationError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is InvalidDeclarationError


def test_scalar():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'scalar', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'scalar', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_no_inheritance():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'no_inheritance', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'no_inheritance', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_combination():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'combination', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'combination', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_merge():
    input_path = os.path.join(TESTS_DIR, 'test_keys', 'merge', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_keys', 'merge', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)
