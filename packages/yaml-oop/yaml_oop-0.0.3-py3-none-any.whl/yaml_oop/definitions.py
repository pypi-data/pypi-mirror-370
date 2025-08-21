# Definitions should not contain any spaces

BASE_CONFIG_DECLARATION = "(base_config)"       
BASE_CONFIG_PATH = "(path)"

VARIABLE_DECLARATION = "(variables)"
OPTIONAL_DECLARTION = "(optional)"
CARRYOVER_DECLARATION = "(carryover)"
GLOBAL_DECLARATION = "(global)"

ABSTRACT_CONFIG_DECLARATION = "(abstract_config)"
SEALED_CONFIG_DECLARATION = "(sealed_config)"
OVERRIDE_CONFIG_DECLARATION = "(override_config)"

ABSTRACT_DECLARATION = "(abstract)"
SEALED_DECLARATION = "(sealed)"
PRIVATE_DECLARATION = "(private)"
OVERRIDE_DECLARATION = "(override)"
APPEND_SEQUENCE_DECLARATION = "(append)"
PREPEND_SEQUENCE_DECLARATION = "(prepend)"
MERGE_SEQUENCE_DECLARATION = "(merge)"

# Declarations available to keys in base classes
BASE_DECLARATIONS = {
    ABSTRACT_DECLARATION,
    SEALED_DECLARATION,
    PRIVATE_DECLARATION,
    OPTIONAL_DECLARTION
}

# Declarations available to keys in sub class
SUB_DECLARATIONS = {
    OVERRIDE_DECLARATION,
    APPEND_SEQUENCE_DECLARATION,
    PREPEND_SEQUENCE_DECLARATION,
    MERGE_SEQUENCE_DECLARATION,
    OPTIONAL_DECLARTION
}

# Declarations available to variables
VARIABLE_DECLARATIONS = {
    ABSTRACT_DECLARATION,  # Abstract variables cannot be used until overriden.
    SEALED_DECLARATION,  # Sealed variables cannot be overriden.
    OVERRIDE_DECLARATION,
    CARRYOVER_DECLARATION,  # Declared during instantiation. Inherits variables from base config during instantiation.
    GLOBAL_DECLARATION,  # TO DO Declared anywhere. Inherits variables from base config through all levels of instantiation.
}

# Declarations for entire file
CONFIG_DECLARATIONS = {
    ABSTRACT_CONFIG_DECLARATION,
    SEALED_CONFIG_DECLARATION,
    OVERRIDE_CONFIG_DECLARATION
}


class Declarations:
    """Contains properties for YAML processing that need to be passed during DFS."""

    def __init__(self, is_overriding: bool, is_abstract: bool, is_sealed: bool):
        self.is_overriding = is_overriding
        self.is_abstract = is_abstract
        self.is_sealed = is_sealed
