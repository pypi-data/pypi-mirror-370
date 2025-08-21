import math
from datetime import (
    timedelta,
    datetime,
)
from typing import Any

from pendulum import duration

from pmsintegration.platform import string_cleansing, utils


class ExpressionEvaluator:
    @staticmethod
    def whitelisted_builtins():
        builtins: dict = eval('__builtins__.copy()')
        builtins.pop('eval')
        builtins.pop('exec')
        builtins.pop('compile')
        builtins["timedelta"] = timedelta
        builtins["datetime"] = datetime
        builtins["math"] = math
        builtins["duration"] = duration
        builtins["string_cleansing"] = string_cleansing
        builtins["str"] = str
        builtins["int"] = int
        builtins["bool"] = utils.coerce_as_bool

        return builtins

    def __init__(self, ):
        self.globals = {"__builtins__": ExpressionEvaluator.whitelisted_builtins()}

    def evaluate(self, expression, variables: dict):
        return eval(expression, self.globals, variables)


_evaluator = ExpressionEvaluator()


def safe_eval(expression: str, variables: dict | None = None):
    return _evaluator.evaluate(expression, variables or {})


def add_global_context(name: str, value: Any):
    _evaluator.globals[name] = value
