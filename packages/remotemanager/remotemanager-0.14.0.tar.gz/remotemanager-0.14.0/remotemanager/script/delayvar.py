from operator import getitem
from typing import Any, Optional

from remotemanager.script.utils import try_value


class ChainingMixin:
    """
    Overrides common actions to allow DelayVar to insert itself and "delay"
    the operation until script generation

    Needs to be a subclass so Subsitution also has access to this ability.
    This is used when doing actions like computer.a = computer.b * computer.c
    """

    __slots__ = []

    def __pow__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__pow__")

    def __mul__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__mul__")

    def __truediv__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__truediv__")

    def __floordiv__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__floordiv__")

    def __add__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__add__")

    def __sub__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__sub__")

    def __mod__(self, other: Any) -> "DelayVar":
        return self._chain_operation(self, other, "__mod__")

    def __eq__(self, other: Any) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, other, "__eq__")

    def __ne__(self, other: Any) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, other, "__ne__")

    def __le__(self, other: Any) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, other, "__le__")

    def __lt__(self, other: Any) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, other, "__lt__")

    def __ge__(self, other: Any) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, other, "__ge__")

    def __gt__(self, other: Any) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, other, "__gt__")

    def __getitem__(self, item) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, item, "__getitem__")

    def __bool__(self) -> "DelayVar":  # type: ignore
        return self._chain_operation(self, None, "__bool__")

    @classmethod
    def _chain_operation(cls, this, other, operation) -> "DelayVar":
        return DelayVar(this, other, operation)


class DelayVar(ChainingMixin):
    """
    Adds chaining ability for DynamicMixin and DynamicValue

    Args:
        a: First parameter
        b: Second parameter (if any)
        op: Operator for the two parameters
        default: Default value
        skip_format: Skip entry formatting
    """

    __slots__ = [
        "_a",
        "_b",
        "_op",
        "default",
        "_value_override",
    ]

    def __init__(
        self,
        a: Any,
        b: Optional[Any] = None,
        op: Optional[str] = None,
        default: Optional[Any] = None,
        skip_format: bool = False,
    ):
        if try_value(a) == "":
            a = None
        if try_value(b) == "":
            b = None
        if op == "":
            op = None

        if (a is None or b is None) and op not in (
            None,
            "__eq__",
            "__ne__",
            "__bool__",
        ):
            if a is None:
                instance = "2nd"
            else:
                instance = "1st"
            raise ValueError(
                f"Operator specified without {instance} value when attempting to create DelayVar({a}, {b}, {op})"
            )
        if b is not None and op is None:
            raise ValueError("Cannot specify 2nd value without operator")

        self._a = self.entry_format(a, skip_format=skip_format)
        self._b = self.entry_format(b, skip_format=skip_format)
        self._op = op

        self.default = self.entry_format(default, skip_format=skip_format)

        self._value_override = None

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self):
        if self._value_override is not None:
            val = self._value_override
        elif self._a is None:
            val = self.default
        else:
            val = self._a
        callstr = [str(val)]

        if self._op is not None:
            callstr.append(f"{self._b}, '{self._op}'")

        return f"DelayVar({', '.join(callstr)})"

    def __hash__(self) -> int:
        return hash(self.value)

    @staticmethod
    def entry_format(value: Any, skip_format: bool) -> Any:
        """
        Attempts to format the value to be numeric. If not possible, leaves it as is.
        """
        from remotemanager.script.substitution import Substitution

        if isinstance(value, Substitution):
            value = value._value

        if value is None:
            return None

        if skip_format:
            return value

        if isinstance(value, bool):
            return value

        try:
            value = float(value)

            if value % 1 == 0:
                return int(value)
            return value

        except (ValueError, TypeError):  # non numeric
            return value

    @property
    def a(self) -> Any:
        return try_value(self._a)

    @property
    def b(self) -> Any:
        return try_value(self._b)

    @property
    def value(self) -> Any:
        if self._value_override is not None:
            return self._value_override

        # while most operations are valid if both a and b are None,
        # equality checks are okay with a=None, b=Any
        if self.a is None and self.b is None:
            return try_value(self.default)

        try:
            if self._op is None:
                return self._a
            # Operations often have special behaviour with int and float, which causes
            # any __op__ to return NotImplmented, so we need to manually handle them.
            # There's probably a nicer way to do this, though...
            elif self._op == "__pow__":
                return self.a**self.b
            elif self._op == "__mul__":
                return self.a * self.b
            elif self._op == "__truediv__":
                return self.a / self.b
            elif self._op == "__floordiv__":
                return self.a // self.b
            elif self._op == "__add__":
                return self.a + self.b
            elif self._op == "__sub__":
                return self.a - self.b
            elif self._op == "__mod__":
                return self.a % self.b
            # boolean operations
            elif self._op == "__eq__":
                return self.a == self.b
            elif self._op == "__ne__":
                return self.a != self.b
            elif self._op == "__lt__":
                return self.a < self.b
            elif self._op == "__le__":
                return self.a <= self.b
            elif self._op == "__gt__":
                return self.a > self.b
            elif self._op == "__ge__":
                return self.a >= self.b
            # miscellaneous operations
            elif self._op == "__getitem__":
                try:
                    return getitem(self.a, self.b)
                except Exception as E:
                    raise ValueError(
                        f"Failed {self.a}[{self.b}]\nTypes: {type(self.a)}[{type(self.b)}]"
                    ) from E

            # mono operations
            elif self._op == "__bool__":
                return bool(self.a)
            # raise
            else:
                raise NotImplementedError(f"Unsupported operation: {self._op}")

        except (TypeError, ValueError):
            if isinstance(self._a, DelayVar):
                return None
            else:
                raise

    @value.setter
    def value(self, value: Any) -> None:
        if self._b is not None:
            print(f"WARNING! Dynamic chain broken when assigning value={value}")
            self._b = None
            self._op = None
        self._a = value
