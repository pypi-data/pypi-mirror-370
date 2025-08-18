from enum import Enum


class InsertionMode(Enum):
    IGNORE = "IGNORE"
    RAISE = "RAISE"
    UPDATE = "UPDATE"


class InsertionModeFactory:
    @staticmethod
    def build(insertion_mode: str) -> str:
        """Build InsertionMode object from string."""
        insertion_mode = insertion_mode.upper()
        if insertion_mode not in InsertionMode.__members__:
            msg = f"Invalid insertion mode: {insertion_mode}. Must be one of {list(InsertionMode.__members__.keys())}."
            raise ValueError(msg)
        return InsertionMode[insertion_mode].value
