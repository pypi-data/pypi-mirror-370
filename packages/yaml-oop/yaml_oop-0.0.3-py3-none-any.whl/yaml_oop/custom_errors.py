class InfiniteInheritanceRecursionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class KeySealedError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ConflictingDeclarationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoOverrideError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidVariableError(Exception):
    def __init__(self, message):
        super().__init__(message)


# TO DO
class AmbiguousVariableError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidInstantiationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidDeclarationError(Exception):
    def __init__(self, message):
        super().__init__(message)