

class DuplicateIdError(RuntimeError):
    pass


class IdNotFoundError(RuntimeError):
    pass


class BoardConnectionError(RuntimeError):
    pass


class BoardUpdateError(RuntimeError):
    pass


class PromptChainError(RuntimeError):
    pass


class CardTypeError(RuntimeError):
    pass


class InformationStoreException(RuntimeError):
    """Custom exception for Information Store errors."""
    pass


class ElementTypeError(RuntimeError):
    pass


class PathLinkError(RuntimeError):
    pass


class TestExecutionError(RuntimeError):
    pass


class TestEvaluationError(RuntimeError):
    pass