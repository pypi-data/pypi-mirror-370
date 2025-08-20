from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal, NamedTuple

import amplify
import numpy as np

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping

    import numpy.typing as npt

    from .variable import Variable


class EncodingInfo(NamedTuple):
    """Encoding information for the variables.

    Attributes:
        variables (amplify.PolyArray[amplify.Dim1]): The encoded variables.
        mapping (dict[amplify.Poly, amplify.Poly]): The mapping from original variables (key) to encoded variables (value).
        constraints (amplify.ConstraintList): The constraints for the encoded variables.
    """

    variables: amplify.PolyArray[amplify.Dim1]
    mapping: dict[amplify.Poly, amplify.Poly]
    constraints: amplify.ConstraintList


def encode_variables(variables: Iterable[Variable]) -> EncodingInfo:
    """Generate encoding information for the given variables.

    Args:
        variables (Iterable[Variable]): The variables to encode.

    Returns:
        EncodingInfo: The encoding information containing the encoded variables, mapping, and related constraints.
    """
    encoded_variables: list[amplify.Poly] = []
    mapping: dict[amplify.Poly, amplify.Poly] = {}
    constraints = amplify.ConstraintList()

    for var in variables:
        encoded = var.encoding.encode(var.name)
        if encoded is None:
            encoded_variables.append(var.to_poly())
            mapping[var.to_poly()] = var.to_poly()
        else:
            encoded_variables.extend(encoded[0])
            mapping[var.to_poly()] = encoded[1]
            if encoded[2] is not None:
                constraints.append(encoded[2])

    return EncodingInfo(amplify.PolyArray(encoded_variables), mapping, constraints)


def decode_values(
    enc_info: EncodingInfo,
    values: npt.NDArray[np.float64],
) -> npt.NDArray:
    """Decode the values using the encoding information.

    Args:
        enc_info (EncodingInfo): The encoding information.
        values (npt.NDArray[np.float64]): The encoded values.

    Raises:
        ValueError: If the number of values does not match the number of encoded variables.
        ValueError: If the values do not satisfy the constraints.

    Returns:
        npt.NDArray: The decoded values.
    """
    if len(enc_info.variables) != len(values):
        raise ValueError("The number of values must be the same as that of encoded variables")
    map_var_val = dict(zip(enc_info.variables.tolist(), values, strict=True))

    # Check if the values satisfy the constraints
    for c in enc_info.constraints:
        if not c.is_satisfied(map_var_val):
            raise ValueError("The input values do not satisfy the constraints")

    return np.array([float(v.substitute(map_var_val)) for v in enc_info.mapping.values()])


def _encode_1d_input(values: npt.NDArray[np.float64], variables: Collection[Variable]) -> list[float]:
    encoded_values: list[float] = []
    for var, val in zip(variables, values, strict=True):
        encoded = var.encoding.encode_value(val)
        if encoded is None:
            encoded_values.append(val)
        else:
            encoded_values.extend(encoded)

    return encoded_values


def _encode_2d_input(dataset: npt.NDArray[np.float64], variables: Collection[Variable]) -> npt.NDArray[np.float64]:
    if len(dataset) == 0:
        raise ValueError("The input dataset must not be empty")

    encoded_dataset: npt.NDArray | None = None
    for values in dataset:
        encoded_values = _encode_1d_input(values, variables)
        if encoded_dataset is None:
            encoded_dataset = np.array([encoded_values], dtype=np.float64)
        else:
            encoded_dataset = np.vstack((encoded_dataset, encoded_values))
    return encoded_dataset  # type: ignore


def encode_input(dataset: npt.NDArray[np.float64], variables: Collection[Variable]) -> npt.NDArray[np.float64]:
    """Encode the input dataset using the provided variable encodings.

    Args:
        dataset (npt.NDArray[np.float64]): The input dataset to encode.
        variables (Collection[Variable]): The variables corresponding to the input dataset.

    Raises:
        ValueError: If the input dataset is not 1D or 2D.
        ValueError: If the number of variables in the input dataset does not match the number of variables in the black-box function.

    Returns:
        npt.NDArray[np.float64]: The encoded input dataset.
    """
    dataset_dim_max: Final[int] = 2
    if dataset.ndim > dataset_dim_max:
        raise ValueError("The input dataset must be 1D or 2D")

    err = ValueError(
        "The number of variables in the input dataset must be the same as the number of variables"
        " in the blackbox function"
    )

    if dataset.ndim == 1:
        if len(dataset) != len(variables):
            raise err
        return np.array(_encode_1d_input(dataset, variables), dtype=np.float64)

    if dataset.shape[1] != len(variables):
        raise err
    return _encode_2d_input(dataset, variables)


def encode_constraints(
    constraints: amplify.ConstraintList | Iterable[amplify.Constraint],
    mapping: Mapping[amplify.Poly, amplify.Poly | float],
) -> amplify.ConstraintList:
    """Encode the constraints using the provided mapping.

    Note that Amplify SDK's ``custom'' penalty formulation method is not supported yet.

    Args:
        constraints (amplify.ConstraintList | Iterable[amplify.Constraint]): The constraints to encode.
        mapping (Mapping[amplify.Poly, amplify.Poly  |  float]): The mapping to use for encoding.

    Raises:
        ValueError: If the constraints are invalid.

    Returns:
        amplify.ConstraintList: The encoded constraints.
    """
    encoded_constraints = amplify.ConstraintList()
    for c in constraints:
        label = c.label
        weight = c.weight
        op: Literal["EQ", "GE", "GT", "LE", "LT", "BW"] = c.conditional[1]  # type:ignore
        left = c.conditional[0].substitute(mapping)

        # FIXME: add support for penalty formulation method but how?
        if op == "EQ":
            right = c.conditional[2]
            assert isinstance(right, float)
            encoded_constraints += weight * amplify.equal_to(left, right, label=label)
        elif op == "GE":
            right = c.conditional[2]
            assert isinstance(right, float)
            encoded_constraints += weight * amplify.greater_equal(left, right, label=label)
        elif op == "LE":
            right = c.conditional[2]
            assert isinstance(right, float)
            encoded_constraints += weight * amplify.less_equal(left, right, label=label)
        elif op == "BW":
            right = c.conditional[2]
            assert isinstance(right, tuple)
            encoded_constraints += weight * amplify.clamp(left, right, label=label)
        else:
            raise ValueError(f"Unsupported operator: {op}")
    return encoded_constraints
