from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any, Generic, ParamSpec, get_type_hints

from .variable import Variable

_Param = ParamSpec("_Param")


def _is_list_like_sequence(obj: object) -> bool:
    return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray))


class BlackBoxFuncBase(ABC, Generic[_Param]):
    """Base class for black-box functions."""

    class Variables:
        """A class to hold variables considered in the black-box function."""

        def __init__(self, flattened_variables_dict: dict[str, Variable], mapping: dict[str, str | list[str]]) -> None:
            """Initialize the Variables class.

            Args:
                flattened_variables_dict (dict[str, Variable]): A dictionary mapping variable names to their corresponding variable objects.
                mapping (dict[str, str  |  list[str]]): A dictionary mapping argument names to variable names or lists of variable names.

            Raises:
                ValueError: If the flattened_variables_dict is empty.
                ValueError: If the mapping is empty.
            """  # noqa: E501
            if len(flattened_variables_dict) == 0:
                raise ValueError("Empty flattened_variables_dict is not allowed.")

            if len(mapping) == 0:
                raise ValueError("Empty mapping is not allowed.")

            self._mapping = mapping  # mapping from argument name to variable name(s)
            self._flattened_variables_dict = (
                flattened_variables_dict  # variables of the blackbox function in a flattened form
            )
            self._variables_dict = {  # variables of the blackbox function
                k: [self._flattened_variables_dict[v_in] for v_in in v]
                if isinstance(v, list)
                else self._flattened_variables_dict[v]
                for k, v in self._mapping.items()
            }

        def __getattr__(self, name: str) -> Variable | list[Variable]:
            if name not in self._variables_dict:
                raise AttributeError(f"No variable called '{name}'")
            return self._variables_dict[name]

        def __len__(self) -> int:
            return len(self._variables_dict)

    def __init__(self) -> None:
        """Initialize the Variables class."""
        self._flattened_variables_dict: dict[str, Variable] = {}  # variables of the blackbox function
        self._mapping: dict[str, str | list[str]] = {}  # mapping from argument name to variable name(s)
        self._name: str = ""

        self._variables: BlackBoxFuncBase.Variables | None = None

    @property
    def mapping(self) -> dict[str, str | list[str]]:
        """Returns the mapping from argument names to variable names or lists of variable names."""
        return self._mapping

    @property
    def name(self) -> str:
        """Returns the name of the black-box function."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Sets the name of the black-box function.

        Args:
            value (str): The name of the black-box function.

        Raises:
            TypeError: If the value is not a string.
        """
        if not isinstance(value, str):
            raise TypeError("value type must be str")
        self._name = value

    @property
    def flattened_variables_dict(self) -> dict[str, Variable]:
        """Returns the flattened variables dictionary."""
        return self._flattened_variables_dict

    @property
    def variables(self) -> BlackBoxFuncBase.Variables:
        """Returns the variables of the black-box function."""
        if self._variables is None:
            self._variables = BlackBoxFuncBase.Variables(self._flattened_variables_dict, self._mapping)
        return self._variables

    def evaluate(self, values: dict[str, float]) -> float:
        """Evaluates the black-box function with the given input values.

        Args:
            values (dict[str, float]): A dictionary mapping variable names to their corresponding input values.

        Returns:
            float: The output of the black-box function.
        """
        return self(**{
            k: [values[v_in] for v_in in v] if isinstance(v, list) else values[v] for k, v in self._mapping.items()
        })  # type: ignore

    @abstractmethod
    def __call__(self, *args: _Param.args, **kwargs: _Param.kwargs) -> float:
        pass


def blackbox(func: Callable[_Param, Any]) -> BlackBoxFuncBase[_Param]:
    """Wraps a function into a black-box function class.

    Args:
        func (Callable[_Param, Any]): The function to wrap.

    Raises:
        ValueError: If the same variable is already specified.
        ValueError: If an empty variable list is specified.

    Returns:
        BlackBoxFuncBase[_Param]: The wrapped black-box function.
    """
    parameters = inspect.signature(func).parameters
    annotations = get_type_hints(func, include_extras=True)
    flattened_variables_dict: dict[str, Variable] = {}
    mapping: dict[str, str | list[str]] = {}

    def add_variable(
        key: str,
        value: Variable | list[Variable],
    ) -> None:
        if isinstance(value, Variable):
            if key in flattened_variables_dict:
                raise ValueError(f"Variable `{key}` already exists.")
            value.name = key
            flattened_variables_dict[key] = value
            mapping[key] = key
        elif _is_list_like_sequence(value):
            if len(value) == 0:
                raise ValueError(f"Empty list is not allowed for variable `{key}`.")
            keys: list[str] = []
            for i, v in enumerate(value):
                if not isinstance(v, Variable):
                    raise TypeError(f"value type must be Variable, but got {type(v)} at index {i}.")
                inner_key = f"{key}[{i}]"
                if key in flattened_variables_dict:
                    raise ValueError(f"Variable `{inner_key}` already exists.")
                v.name = inner_key
                flattened_variables_dict[inner_key] = v
                keys.append(inner_key)
            mapping[key] = keys

    for k, v in parameters.items():
        if isinstance(v.default, Variable) or _is_list_like_sequence(v.default):
            add_variable(k, v.default)
            continue
        if v.default is inspect.Parameter.empty:
            annotation = annotations[k]
            if hasattr(annotation, "__metadata__") and len(annotation.__metadata__) == 1:
                meta = annotation.__metadata__[0]
                if isinstance(meta, Variable) or _is_list_like_sequence(meta):
                    add_variable(k, meta)
                    continue

        raise ValueError(
            f"Argument `{k}` of {func.__name__} must be annotated with `Annotated[..., Var]`"
            f" or has a default value as `Var`, where `Var` is an instance of `Variable` of sequence of `Variable`."
        )

    class BlackBoxFunc(BlackBoxFuncBase[_Param]):
        def __init__(self) -> None:
            super().__init__()
            self._flattened_variables_dict = flattened_variables_dict
            self._name = func.__name__
            self._mapping = mapping

        def __call__(self, *args: _Param.args, **kwargs: _Param.kwargs) -> float:
            return func(*args, **kwargs)

    return BlackBoxFunc()
