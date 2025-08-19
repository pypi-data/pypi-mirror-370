from __future__ import annotations
from enum import StrEnum, auto
from random import choice


class ErrorType(StrEnum):
    MISSING_PARAMETER = auto()
    MADE_UP_PARAMETER = auto()
    MISSING_MEMORY = auto()
    MADE_UP_ASSIGNMENT = auto()
    WRONG_ASSIGNMENT = auto()
    MADE_UP_API = auto()
    BAD_REPEAT = auto()
    MISSING_CALL = auto()
    NEW_CALL = auto()
    UNKNOWN = auto()

    @classmethod
    def get_random_error(cls) -> ErrorType:
        available_keys = [
            cls.MISSING_PARAMETER,
            cls.MADE_UP_PARAMETER,
            cls.MADE_UP_ASSIGNMENT,
        ]

        return choice(available_keys)
