from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
from dataclasses import asdict


class NoDataError(Exception):
    pass


class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    NO_DATA = "no-data"
    ERROR = "error"


class Op(Enum):
    CONTAINS = "contains"
    EQUALS = "equals"
    TRUE = "true"
    FALSE = "false"
    GREATER = "greater"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS = "less"
    LESS_OR_EQUAL = "less_or_equal"
    MATCH = "match"
    FAIL = "fail"
    ERROR = "error"
    EXISTS = "exists"


@dataclass
class AssertionResult:
    op: Op
    args: list[Any]
    result: CheckStatus
    failure_message: Optional[str] = None

    def toJson(self):
        result = asdict(self)

        result['op'] = self.op.value
        result['result'] = self.result.value

        if result['failure_message'] is None:
            del result['failure_message']

        return result
