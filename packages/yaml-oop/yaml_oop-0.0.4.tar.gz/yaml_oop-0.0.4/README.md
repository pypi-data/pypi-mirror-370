# yaml_oop

A Python library that enables features such as inheritance, variables, and instantiation in YAML files.

## Requirements

Python 3.8 or later 
pyyaml 6.0.2

## Features

YAML in-line keywords that enable inheritance and variables from other files. Ultimately, this allows YAML files to be fully modular through in-line modifications of the YAML file.

### Inheritance:
Files can be nested within elements of YAML files and apply composition and inheritance logic to concatenante elements.
Inheritance logic applies to matching keys within the tree node and to multiple (nested) layers of YAML file inheritance.
Multiple inheritance, overriding, and keywords such as sealed, abstract, private is supported.

### Variables:
Variables can be injected into YAML files during inheritance or Python code to modify scalar values.
Variables allow scalars to represent other scalars, lists, dicts, or dynamic inheritance paths.
Variables can also operate on in-line keywords for additional customization.

### Supported Keywords:
Multiple keywords can be assigned a single key or sequence element.

**(base_config)**: Specifies file path(s) to inherit elements from base YAML file(s).
**(variables)**: Specifies scalar values to replace. Can be injected into root YAML file or (base_config) YAML files or declared in-line and apply to child elements.
**(override)**: Overrides values of base YAML files for matching keys.
**(append) (prepend)**: Concatenates sequences with a matching parent key.
**(merge)**: Applies inheritance rules to sequence items of the same indicies.
**(abstract) (sealed) (private)**: To enforce override, prevent override, and hide keys, sequence elements, and variables from inheritance respecitvely.
**(optional)**: Deletes keys or sequence elements if variables do not replace values.
**(carryover)**: Allows variables to be pass through muliple layers of inheritance.

## Installation

```cmd
pip install yaml_oop
```

## Usage

```python
import yaml
from yaml_oop import oopify

output_yaml = oopify(file_path=input_yaml_path, directory=input_yaml_directory, Loader=yaml.SafeLoader, variables=variables)
```

```yaml

```

## Project Structure

```
yaml_oop/
├── yaml_oop/
│   ├── __init__.py
│   └── yaml_object.py
├── tests/
│   └── test_yaml_object.py
├── example.yaml
├── README.md
└── requirements.txt
```

## License

MIT License
