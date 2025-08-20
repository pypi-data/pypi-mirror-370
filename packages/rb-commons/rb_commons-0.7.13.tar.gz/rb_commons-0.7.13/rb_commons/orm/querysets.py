from typing import Any

from functools import wraps
from typing import Callable, TypeVar, Any

class QJSON:
    def __init__(self, field: str, key: str, operator: str, value: Any):
        self.field = field
        self.key = key
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"QJSON(field={self.field}, key={self.key}, op={self.operator}, value={self.value})"

class Q:
    """Boolean logic container that can be combined with `&`, `|`, and `~`."""

    def __init__(self, **lookups: Any) -> None:
        self.lookups: Dict[str, Any] = lookups
        self.children: List[Q] = []
        self._operator: str = "AND"
        self.negated: bool = False

    def _combine(self, other: "Q", operator: str) -> "Q":
        combined = Q()
        combined.children = [self, other]
        combined._operator = operator
        return combined

    def __or__(self, other: "Q") -> "Q":
        return self._combine(other, "OR")

    def __and__(self, other: "Q") -> "Q":
        return self._combine(other, "AND")

    def __invert__(self) -> "Q":
        clone = Q()
        clone.lookups = self.lookups.copy()
        clone.children = list(self.children)
        clone._operator = self._operator
        clone.negated = not self.negated
        return clone

    def __repr__(self) -> str:
        if self.lookups:
            base = f"Q({self.lookups})"
        else:
            base = "Q()"
        if self.children:
            base += f" {self._operator} {self.children}"
        if self.negated:
            base = f"NOT({base})"
        return base


