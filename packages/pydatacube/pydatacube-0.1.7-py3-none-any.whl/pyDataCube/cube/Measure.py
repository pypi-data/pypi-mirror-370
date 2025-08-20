from __future__ import annotations

from numbers import Number
from typing import Dict

from .Predicate import Predicate
from .PredicateOperator import PredicateOperator
from .AggregateFunction import AggregateFunction


class Measure:
    def __init__(self, name: str, function: AggregateFunction, sql_name: str):
        self.name: str = name
        self.sqlname: str = sql_name
        self.aggregate_function: AggregateFunction = function

    def aggregate(self, x: Number, y: Number) -> Number:
        return self.aggregate_function.eval(x, y)

    def set_aggregate_function(self, fn: str) -> None:
        match fn.lower():
            case "sum":
                self.aggregate_function = AggregateFunction("SUM", lambda x, y: x + y)
            case "max":
                self.aggregate_function = AggregateFunction("MAX", lambda x, y: x if x > y else y)
            case "min":
                self.aggregate_function = AggregateFunction("MIN", lambda x, y: x if x < y else y)
            case "avg":
                self.aggregate_function = AggregateFunction("AVG", lambda x, y: x)
            case "count":
                self.aggregate_function = AggregateFunction("COUNT", lambda acc, x: acc + 1)
            case _:
                raise Exception(f"Unknown aggregate function {fn}")

    def __add__(self, other: Measure) -> Dict[str, str | AggregateFunction]:
        return self._create_calculated_measure(other, "+")

    def __sub__(self, other: Measure) -> Dict[str, str | AggregateFunction]:
        return self._create_calculated_measure(other, "-")

    def __mul__(self, other: Measure) -> Dict[str, str | AggregateFunction]:
        return self._create_calculated_measure(other, "*")

    def __div__(self, other: Measure) -> Dict[str, str | AggregateFunction]:
        return self._create_calculated_measure(other, "/")

    def _create_calculated_measure(self, other: Measure, operator: str) -> dict[str, str | AggregateFunction]:
        return {"function": self.aggregate_function, "sqlname": f"{self.sqlname} {operator} {other.sqlname}"}

    def __repr__(self) -> str:
        return f"({self.name}, {self.aggregate_function})"

    # HACKS
    def __gt__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.GT)

    def __lt__(self, other) -> Predicate:
        return self._create_pred(other, PredicateOperator.LT)

    def _create_pred(self, other, comparison_operator: PredicateOperator) -> Predicate:
        left_child = Predicate(None, self, None)
        right_child = Predicate(None, other, None)
        return Predicate(left_child, comparison_operator, right_child)
