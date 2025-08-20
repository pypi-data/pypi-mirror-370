from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from enum import Enum
from itertools import accumulate
from math import isclose
from typing import Literal, NamedTuple

import amplify

if sys.version_info >= (3, 11):
    from typing import assert_never
else:
    from typing_extensions import assert_never

# global variable generator
_generator = amplify.VariableGenerator()


class EncodingMethod(Enum):
    """Encoding methods for variables.

    Attributes:
        Amplify (int): Use Amplify SDK's default encoding.
        OneHot (int): One-hot encoding.
        DomainWall (int): Domain wall encoding.
    """

    Amplify = 0
    OneHot = 1
    DomainWall = 2


class DiscretizationMethod(Enum):
    """Discretization methods for variables.

    Attributes:
        Uniform (int): Uniform discretization.
        LogUniform (int): Logarithmic uniform discretization.
    """

    Uniform = 0
    LogUniform = 1
    # TODO: Add more discretization methods


class _EncodingMethodBase(ABC):
    @abstractmethod
    def encode(self, var_name: str = "") -> tuple[list[amplify.Poly], amplify.Poly, amplify.Constraint] | None:
        raise NotImplementedError

    @abstractmethod
    def encode_value(self, value: float) -> list[int] | None:  # FIXME: Bad method name
        raise NotImplementedError


class _AmplifyEncoding(_EncodingMethodBase):
    def encode(self, var_name: str = "") -> None:  # noqa: ARG002, PLR6301
        return None

    def encode_value(self, value: float) -> None:  # noqa: ARG002, PLR6301
        return None


class Variable:
    """A base class representing a decision variable for the optimization problem."""

    def __init__(
        self,
        var_type: amplify.VariableType,
        bounds: tuple[float, float] | None = None,
        encoding: _EncodingMethodBase | None = None,
    ) -> None:
        """Initialize a decision variable.

        Args:
            var_type (amplify.VariableType): The type of the variable.
            bounds (tuple[float, float] | None, optional): The bounds of the variable. Defaults to `None`.
            encoding (_EncodingMethodBase | None, optional): The encoding method for the variable. Defaults to `None`.
        """
        self._poly = _generator.scalar(var_type, bounds if bounds is not None else (None, None))
        self._encoding = encoding or _AmplifyEncoding()

    @property
    def name(self) -> str:
        """Returns the name of the variable."""
        return self._poly.name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("value type must be str")
        self._poly.name = value

    @property
    def type(self) -> amplify.VariableType:
        """Returns the type of the variable."""
        return self._poly.type

    @property
    def possible_values(self) -> list[float | int] | tuple[float, float]:
        """Returns a list of possible values for a discrete variable, or a pair of boundary values for a continuous variable.

        Returns:
            list[float | int] | tuple[float, float]: The possible values or bounds.
        """  # noqa: E501
        match self.type:
            case amplify.VariableType.Binary:
                return list(range(2))
            case amplify.VariableType.Ising:
                return list(range(-1, 2, 2))
            case amplify.VariableType.Integer:
                assert isinstance(self._poly.lower_bound, float)
                assert isinstance(self._poly.upper_bound, float)
                return list(range(int(self._poly.lower_bound), int(self._poly.upper_bound) + 1))
            case amplify.VariableType.Real:
                if isinstance(self._encoding, _DiscretizationEncoding):
                    return self._encoding.discrete_values

                # continuous variables must have a bound range.
                assert self.bounds is not None
                assert self.bounds[0] is not None
                assert self.bounds[1] is not None

                # return bounds for continuous variable
                return (self.bounds[0], self.bounds[1])
            case _ as unreachable:
                assert_never(unreachable)

    @property
    def bounds(self) -> tuple[float | None, float | None] | None:
        """Returns the bounds of the variable."""
        if self._poly.type == amplify.VariableType.Binary:
            return None
        return (self._poly.lower_bound, self._poly.upper_bound)

    @property
    def encoding(self) -> _EncodingMethodBase:
        """Returns the encoding method for the variable."""
        return self._encoding

    def to_poly(self) -> amplify.Poly:
        """Converts the variable to the Amplify SDK's polynomial representation.

        Returns:
            amplify.Poly: The Amplify SDK's polynomial representation of the variable.
        """
        return self._poly

    def __add__(self, other: Variable | amplify.Poly | float) -> amplify.Poly:
        if isinstance(other, (amplify.Poly, int, float)):
            return self._poly + other
        if isinstance(other, Variable):
            return self._poly + other._poly

        raise TypeError("Unsupported type for addition.")

    def __radd__(self, other: amplify.Poly | float) -> amplify.Poly:
        return other + self._poly

    def __sub__(self, other: Variable | amplify.Poly | float) -> amplify.Poly:
        if isinstance(other, (amplify.Poly, int, float)):
            return self._poly - other
        if isinstance(other, Variable):
            return self._poly - other._poly

        raise TypeError("Unsupported type for subtraction.")

    def __rsub__(self, other: amplify.Poly | float) -> amplify.Poly:
        return other - self._poly

    def __mul__(self, other: Variable | amplify.Poly | float) -> amplify.Poly:
        if isinstance(other, (amplify.Poly, int, float)):
            return self._poly * other
        if isinstance(other, Variable):
            return self._poly * other._poly

        raise TypeError("Unsupported type for multiplication.")

    def __rmul__(self, other: amplify.Poly | float) -> amplify.Poly:
        return other * self._poly

    def __truediv__(self, other: float) -> amplify.Poly:
        return self._poly / other

    def __pos__(self) -> amplify.Poly:
        return self._poly

    def __neg__(self) -> amplify.Poly:
        return -self._poly

    def __pow__(self, other: int) -> amplify.Poly:
        return self._poly**other

    def __eq__(self, other: object) -> bool:
        if isinstance(other, amplify.Poly):
            return self._poly == other
        if isinstance(other, Variable):
            return self._poly == other._poly

        return False

    def __hash__(self) -> int:
        return hash(self._poly)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str(self._poly)

    def __repr__(self) -> str:
        return repr(self._poly)

    def _repr_latex_(self) -> str:  # noqa: PLW3201
        return self._poly._repr_latex_()  # type: ignore[reportAttributeAccessIssue]


class _DiscretizationEncoding(_EncodingMethodBase):
    def __init__(
        self,
        discrete_values: list[float],
        method: Literal[EncodingMethod.OneHot, EncodingMethod.DomainWall],
        discrete_ranges: list[float] | None = None,
    ) -> None:
        self._discrete_values = discrete_values
        self._method: Literal[EncodingMethod.OneHot, EncodingMethod.DomainWall] = method
        self._discrete_ranges = discrete_ranges
        self._encode_cache: tuple[list[amplify.Poly], amplify.Poly, amplify.Constraint] | None = None

    @property
    def method(self) -> Literal[EncodingMethod.OneHot, EncodingMethod.DomainWall]:
        return self._method

    @property
    def num_bins(self) -> int:
        return len(self._discrete_values)

    @property
    def discrete_values(self) -> list[float]:
        return self._discrete_values

    @property
    def is_approx(self) -> bool:
        return self._discrete_ranges is not None

    def encode(self, var_name: str = "") -> tuple[list[amplify.Poly], amplify.Poly, amplify.Constraint]:
        if self._encode_cache is not None:
            return self._encode_cache

        if self.method == EncodingMethod.OneHot:
            q = _generator.array("Binary", shape=self.num_bins, name=var_name)
            self._encode_cache = (q.to_list(), (q * self.discrete_values).sum(), amplify.one_hot(q))
            return self._encode_cache
        if self.method == EncodingMethod.DomainWall:
            # Create a sequence of variables such that the left end is 0 and the right end is 1.
            # The number of variables is equal to the number of bins + 1.
            # e.g. q = [0, [q_1, q_2], 1] for num_bins = 3
            q = _generator.array("Binary", shape=self.num_bins + 1, name=var_name)
            q[0] = 0
            q[-1] = 1
            self._encode_cache = (
                q[1:-1].to_list(),
                ((q[1:] - q[:-1]) * self.discrete_values).sum(),
                amplify.domain_wall(q[1:-1]),
            )
            return self._encode_cache

        raise TypeError("Invalid encoding method.")

    def encode_value(self, value: float) -> list[int]:
        if self._discrete_ranges is not None:  # equivalent to `if self.is_approx`
            seq = [
                1 if self._discrete_ranges[i] <= value < self._discrete_ranges[i + 1] else 0
                for i in range(self.num_bins)
            ]
            if sum(seq) != 1:
                raise ValueError("Value must be in the range of discrete values.")
        else:
            seq = [1 if isclose(value, v) else 0 for v in self.discrete_values]
            if sum(seq) != 1:
                raise ValueError("Value must be one of the discrete values.")

        if self.method == EncodingMethod.OneHot:
            return seq

        if self.method == EncodingMethod.DomainWall:
            return [*accumulate(seq[:-1])]

        raise TypeError("Invalid encoding method.")


class BinaryVariable(Variable):
    """Represents a binary variable."""

    def __init__(self) -> None:
        super().__init__(amplify.VariableType.Binary)


class IntegerVariable(Variable):
    """Represents an integer variable with specified bounds."""

    def __init__(
        self,
        bounds: tuple[int, int],
        encoding: EncodingMethod = EncodingMethod.DomainWall,
    ) -> None:
        """Initializes an integer variable with specified bounds and encoding method.

        Args:
            bounds (tuple[int, int]): The lower and upper bounds for the variable.
            encoding (EncodingMethod, optional): The encoding method to use. Defaults to EncodingMethod.DomainWall.

        Raises:
            ValueError: If the bounds are invalid.
            TypeError: If the bounds are not integers.
            TypeError: If the encoding method is invalid.
        """
        if bounds[0] > bounds[1]:
            raise ValueError("Lower bound must be less than or equal to upper bound.")
        if not isinstance(bounds[0], int) or not isinstance(bounds[1], int):
            raise TypeError("Bounds must be integer values.")

        if encoding == EncodingMethod.Amplify:
            super().__init__(amplify.VariableType.Integer, bounds, _AmplifyEncoding())
        elif encoding == EncodingMethod.OneHot:
            super().__init__(
                amplify.VariableType.Integer,
                bounds,
                _DiscretizationEncoding(list(range(bounds[0], bounds[1] + 1)), EncodingMethod.OneHot),
            )
        elif encoding == EncodingMethod.DomainWall:
            super().__init__(
                amplify.VariableType.Integer,
                bounds,
                _DiscretizationEncoding(list(range(bounds[0], bounds[1] + 1)), EncodingMethod.DomainWall),
            )
        else:
            raise TypeError("Invalid encoding method.")


class DiscretizationSpec(NamedTuple):
    """Specifies the discretization method and number of bins for a variable.

    Attributes:
        method (DiscretizationMethod): The discretization method to use. Defaults to DiscretizationMethod.Uniform.
        num_bins (int): The number of bins to divide the variable into. Defaults to 11.
    """

    method: DiscretizationMethod = DiscretizationMethod.Uniform
    num_bins: int = 11


class RealVariable(Variable):
    """Represents a real-valued variable with specified bounds, discretization and encoding method."""

    def __init__(
        self,
        bounds: tuple[float, float],
        encoding: EncodingMethod = EncodingMethod.DomainWall,
        discretization_spec: DiscretizationSpec | None = None,
    ) -> None:
        """Initializes a real-valued variable with specified bounds, discretization and encoding method.

        Args:
            bounds (tuple[float, float]): The lower and upper bounds for the variable.
            encoding (EncodingMethod, optional): The encoding method to use. Defaults to EncodingMethod.DomainWall.
            discretization_spec (DiscretizationSpec | None, optional): The discretization specification to use. Defaults to None (DiscretizationSpec()).

        Raises:
            ValueError: If the discretization is specified with Amplify encoding.
            ValueError: If the bounds are invalid.
            TypeError: If the bounds are not float values.
            ValueError: If the number of bins is invalid.
            ValueError: If the non-uniform discretization method is specified with Amplify encoding.
            ValueError: If the lower bound is not greater than 0 for `LogUniform` discretization.
            TypeError: If the encoding method is invalid.
        """  # noqa: E501
        if encoding == EncodingMethod.Amplify and discretization_spec is not None:
            raise ValueError("Amplify encoding does not support specifying discretization method.")

        desc_method, num_bins = discretization_spec or DiscretizationSpec()

        if bounds[0] > bounds[1]:
            raise ValueError("Lower bound must be less than or equal to upper bound.")
        if not isinstance(bounds[0], (int, float)) or not isinstance(bounds[1], (int, float)):
            raise TypeError("Bounds must be integer or float values.")

        if num_bins <= 1:
            raise ValueError("Number of bins must be greater than 1.")

        def tolerance(value: float) -> float:
            return max(abs(value) * 1e-09, 1e-09)

        if encoding == EncodingMethod.Amplify and desc_method != DiscretizationMethod.Uniform:
            raise ValueError("Amplify encoding only supports Uniform discretization.")

        if desc_method == DiscretizationMethod.Uniform:
            discrete_values = [bounds[0] + (bounds[1] - bounds[0]) * i / (num_bins - 1) for i in range(num_bins)]
            discrete_ranges = (
                [discrete_values[0] - tolerance(discrete_values[0])]
                + [bounds[0] + (bounds[1] - bounds[0]) * (i + 0.5) / (num_bins - 1) for i in range(num_bins - 1)]
                + [discrete_values[-1] + tolerance(discrete_values[-1])]
            )
        elif desc_method == DiscretizationMethod.LogUniform:
            if bounds[0] <= 0:
                raise ValueError("Lower bound must be greater than 0 for `LogUniform` discretization.")
            discrete_values = [bounds[0] * (bounds[1] / bounds[0]) ** (i / (num_bins - 1)) for i in range(num_bins)]
            discrete_ranges = (
                [discrete_values[0] - tolerance(discrete_values[0])]
                + [bounds[0] * (bounds[1] / bounds[0]) ** ((i + 0.5) / (num_bins - 1)) for i in range(num_bins - 1)]
                + [discrete_values[-1] + tolerance(discrete_values[-1])]
            )

        if encoding == EncodingMethod.Amplify:
            super().__init__(amplify.VariableType.Real, bounds, _AmplifyEncoding())
        elif encoding == EncodingMethod.OneHot:
            super().__init__(
                amplify.VariableType.Real,
                bounds,
                _DiscretizationEncoding(discrete_values, EncodingMethod.OneHot, discrete_ranges=discrete_ranges),
            )
        elif encoding == EncodingMethod.DomainWall:
            super().__init__(
                amplify.VariableType.Real,
                bounds,
                _DiscretizationEncoding(discrete_values, EncodingMethod.DomainWall, discrete_ranges=discrete_ranges),
            )
        else:
            raise TypeError("Invalid encoding method.")


class DiscreteVariable(Variable):
    """Represents a discrete variable."""

    def __init__(
        self,
        values: list[float],
        encoding: Literal[EncodingMethod.OneHot, EncodingMethod.DomainWall] = EncodingMethod.DomainWall,
    ) -> None:
        """Initializes a discrete variable with specified values and encoding method.

        Args:
            values (list[float]): The discrete values.
            encoding (Literal[EncodingMethod.OneHot, EncodingMethod.DomainWall], optional): The encoding method. Defaults to EncodingMethod.DomainWall.

        Raises:
            ValueError: If the values list is empty.
            ValueError: If the values list contains duplicates.
            ValueError: If the values list is not sorted.
            TypeError: If the encoding method is invalid.
        """  # noqa: E501
        if len(values) == 0:
            raise ValueError("Empty list is not allowed for discrete values.")

        if len(values) != len(set(values)):
            raise ValueError("Values must be unique.")

        values.sort()

        if encoding == EncodingMethod.Amplify:
            raise ValueError("DiscreteVariable does not support Amplify encoding.")

        # DiscreteVariable is treated as RealVariable without bounds
        if encoding == EncodingMethod.OneHot:
            super().__init__(
                amplify.VariableType.Real,
                None,
                _DiscretizationEncoding(values, EncodingMethod.OneHot),
            )
        elif encoding == EncodingMethod.DomainWall:
            super().__init__(
                amplify.VariableType.Real,
                None,
                _DiscretizationEncoding(values, EncodingMethod.DomainWall),
            )
        else:
            raise TypeError("Invalid encoding method.")
