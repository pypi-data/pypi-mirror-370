import math
from typing import Any, List, Optional, Union
import warnings

from remotemanager.script.utils import format_time, try_value
from remotemanager.script.delayvar import ChainingMixin, DelayVar
from remotemanager.utils import ensure_list


EMPTY_TREATMENT_STYLES = [
    "line",  # default, removes the whole line
    "local",  # locally removes the value, ignoring the line
    "ignore",  # do nothing, performing no replacement
]
INVALID_EMPTY_TREATMENT = "empty_treatment must be one of the available styles: {style}"


class Substitution(ChainingMixin):
    """
    Creates a substitution for a #placeholder# within a Script object.

    ..note::
        The user is not expected to create these themselves, as they are intended for
        use by the Script object.

    The following args are valid kwargs when specifying a placeholder.

    e.g:
    `#foo:default=10:min=1:max=50:optional=False:hidden=True#`

    Would create a non-optional hidden variable named "foo" with a minimum of 1,
    and a maximum of 50, that defaults to a value of 10

    Args:
        target (str):
            The target string to be replaced
        name (str):
            The assigment on the Script
        value (Optional, Any):
            Force a value. It is advisable to use `default` instead
        default (Optional, Any):
            The default value
        min (Optional, Union[int, float]):
            The minimum value for the variable
        max (Optional, Union[int, float]):
            The maximum value for the variable
        optional (bool):
            Whether the variable is optional or not
        requires (Optional, Union[str, List[str]]):
            The required variables for the substitution
        hidden (bool):
            Whether the variable is hidden within a jobscript
        format (Optional[str]):
            The format of the variable, e.g. "float" or "time", defaults to "int"
        empty_treatment (Optional[str]):
            The treatment of an empty substitution, defaults to "line"
            Available options are:
            - line => A missing value removes the whole line
            - local => A missing value removes the variable locally
            - ignore => A missing value does nothing
        static (bool):
            Does not chain with other values if True
            This causes the content to always be exactly what is set
            I.e. even if you link with default={a}, the script will always generate {a}
        mode (str): Internal arg, used for JUBE compatibility

    """

    __slots__ = [
        "target",
        "name",
        "_optional",
        "hidden",
        "requires",
        "format",
        "static",
        "empty_treatment",
        "_value",
        "_linked",
        "_min",
        "_max",
        "mode",
    ]

    def __init__(
        self,
        target: str,
        name: str,
        value: Optional[Any] = None,
        default: Optional[Any] = None,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        optional: bool = True,
        requires: Optional[Union[str, List[str]]] = None,
        hidden: bool = False,
        format: Optional[str] = None,
        empty_treatment: Optional[str] = "line",
        static: bool = False,
        mode: Optional[str] = None,
    ):
        self.target = target
        self.name = name

        self._optional = self._parse_bool_like(optional)
        self.hidden = self._parse_bool_like(hidden)

        self.requires = ensure_list(requires, semantic=True)
        self.format = format

        self.static = static

        if empty_treatment not in EMPTY_TREATMENT_STYLES:
            raise ValueError(INVALID_EMPTY_TREATMENT.format(style=empty_treatment))
        self.empty_treatment = empty_treatment

        self._value = DelayVar(a=value, default=default)
        self._linked = False

        self._min = DelayVar(None)
        if min is not None:
            self.min = min

        self._max = DelayVar(None)
        if max is not None:
            self.max = max

        self.mode = mode

    def __hash__(self) -> int:
        return hash(self.target)

    def __str__(self):
        return str(self.value)

    def __repr__(self) -> str:
        return f"Substitution({self.target}, {self.name}) -> {self._value}"

    @staticmethod
    def _parse_bool_like(inp: Union[str, int, bool]) -> bool:
        if str(inp) in ["False", "false", "0"]:
            return False
        elif str(inp) in ["True", "true", "1"]:
            return True
        else:
            raise ValueError(f"Invalid value bool conversion: {inp}")

    @classmethod
    def from_string(
        cls, string: str, warn_invalid: bool = True, **kwargs
    ) -> "Substitution":
        """
        Create a substitution object from template string

        Args:
            string (str): Input string to generate from
            warn_invalid (bool): Invalid args name, target will be deleted. Warn if True
            kwargs: Any keyword args to override the string with
        """
        content = string.strip("#")  # actual internal "content"
        sym = content.split(":")[0]  # name, drop args for function extract
        name = sym.lower()  # always lowercase the name
        string_args = cls.get_target_kwargs(string)
        # can't override the name or target
        invalid_args = ["target", "name"]
        for arg in invalid_args:
            if arg in kwargs:
                if warn_invalid:
                    warnings.warn(f"Invalid kwarg {arg}={kwargs[arg]} deleted")
                del kwargs[arg]
        # add any kwargs
        string_args.update(kwargs)

        return cls(target=string, name=name, **string_args)

    @property
    def target_kwargs(self) -> dict:
        """Attempts to extract the kwargs from the target string"""
        return self.get_target_kwargs(self.target)

    @staticmethod
    def get_target_kwargs(string: str) -> dict:
        """Attempts to generate kwargs from input string"""

        if ":" not in string:
            return {}

        _, argline = string.strip("#").split(":", maxsplit=1)

        args = {}
        key_cache = []
        val_cache = []
        key_mode = True
        escape = False
        inset_cache = []

        def append(c: str):
            if key_mode:
                key_cache.append(c)
            else:
                val_cache.append(c)

        for char in argline:
            # handle escaped characters
            if char == "\\" and not escape:
                escape = True
                append(char)
                continue
            # we're in escape mode, append the char, set the flag false and continue
            if escape:
                escape = False
                append(char)
                continue

            # swap from arg to val, once
            if char == "=" and key_mode:
                key_mode = False
                continue

            # quotation
            if char == '"':
                if len(inset_cache) == 0:
                    inset_cache.append(char)
                elif inset_cache[-1] == '"':
                    inset_cache.pop(-1)
            if char == "'":
                if len(inset_cache) == 0:
                    inset_cache.append(char)
                elif inset_cache[-1] == "'":
                    inset_cache.pop(-1)

            # evaluation
            if char == "{":
                inset_cache.append("{")
            if char == "}":
                if inset_cache[-1] == "{":
                    inset_cache.pop(-1)

            # end of this arg, reset
            if char == ":" and len(inset_cache) == 0:
                if key_mode:
                    raise ValueError(
                        f"Spurious ':' character in arg {''.join(key_cache)}"
                    )

                args["".join(key_cache)] = "".join(val_cache)
                key_mode = True
                key_cache = []
                val_cache = []
                continue

            # otherwise, store this char and continue
            append(char)

        if len(key_cache) != 0 and len(val_cache) != 0:
            args["".join(key_cache)] = "".join(val_cache)

        return args

    @property
    def min(self) -> Union[int, float]:
        return try_value(self._min)

    @min.setter
    def min(self, value: Union[int, float, DelayVar]):
        if isinstance(value, DelayVar):
            self._min = value
        else:
            self._min = DelayVar(a=value)

    @property
    def max(self) -> Union[int, float]:
        return try_value(self._max)

    @max.setter
    def max(self, value: Union[int, float, DelayVar]):
        if isinstance(value, DelayVar):
            self._max = value
        else:
            self._max = DelayVar(a=value)

    @property
    def optional(self) -> bool:
        return self._value.default is not None or self._optional

    @optional.setter
    def optional(self, optional: bool) -> None:
        self._optional = optional

    @property
    def temporary_value(self) -> Any:
        return self._value._value_override

    @temporary_value.setter
    def temporary_value(self, value: Any):
        self._value._value_override = value

    def _format_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, bool):
            return value

        if try_value(self.format) == "time":
            return format_time(value)
        if try_value(self.format) == "float":
            return float(value)

        try:
            value / 1  # type: ignore
            isnumeric = True
        except (TypeError, ValueError):
            isnumeric = False

        if isnumeric:
            # round division up, prevents behaviour like requesting 0 nodes
            value = int(math.ceil(try_value(value)))

            if self.min is not None and value < self.min:
                raise ValueError(
                    f"Value for {self.name} ({value}) is less than minimum ({self.min})"
                )
            if self.max is not None and value > self.max:
                raise ValueError(
                    f"Value for {self.name} ({value}) is more than maximum ({self.max})"
                )

        return value

    @property
    def value(self) -> Any:
        return self._format_value(try_value(self._value))

    @value.setter
    def value(self, value: Any):
        if isinstance(value, DelayVar):
            # if the value is a DelayVar, we need to update the link
            self._value = value
        elif isinstance(value, Substitution):
            # if the value is a Sub, we should extract the DelayVar and link update
            self._value = value._value
        else:
            # if the value is an ordinary object, update the link _internals_
            self._value.value = value

    @property
    def default(self) -> Any:
        return self._format_value(try_value(self._value.default))

    @default.setter
    def default(self, value: Any):
        if isinstance(value, DelayVar):
            self._value.default = value
        else:
            self._value.default = DelayVar(value)
