from logging import getLogger
from typing import Generic, TypeVar

import amplify
import numpy as np
import numpy.typing as npt

from .bbopt_logging import AMPLIFY_BBOPT_LOGGER_NAME

_C = TypeVar("_C", bound=amplify.AmplifyClient)

_default_client = amplify.FixstarsClient()

logger = getLogger(AMPLIFY_BBOPT_LOGGER_NAME)


class AmplifyModel(Generic[_C]):
    """A class to represent an optimization model using Amplify SDK."""

    def __init__(
        self,
        variables: amplify.PolyArray,
        client: _C = _default_client,
    ) -> None:
        """Initialize the AmplifyModel.

        Args:
            variables (amplify.PolyArray): The variables of the optimization model.
            client (_C, optional): The Amplify client to use. Defaults to _default_client.
        """
        super().__init__()
        self._variables: amplify.PolyArray = variables
        self._client: _C = client
        self._objective = amplify.Poly()
        self._constraints = amplify.ConstraintList()
        if isinstance(self._client, amplify.FixstarsClient):
            self._client.parameters.outputs.num_outputs = 0
            self._client.parameters.outputs.duplicate = True

    @property
    def variables(self) -> amplify.PolyArray:
        """Return the variables of the optimization model."""
        return self._variables

    @property
    def client(self) -> _C:
        """Return the Amplify client used by the model."""
        return self._client

    @property
    def objective(self) -> amplify.Poly:
        """Return the objective function of the optimization model."""
        return self._objective

    @objective.setter
    def objective(self, objective: amplify.Poly) -> None:
        """Set the objective function of the optimization model.

        Args:
            objective (amplify.Poly): The objective function to set.
        """
        self._objective = objective

    @property
    def constraints(self) -> amplify.ConstraintList:
        """Return the constraints of the optimization model."""
        return self._constraints

    @constraints.setter
    def constraints(self, constraints: amplify.ConstraintList) -> None:
        """Set the constraints of the optimization model.

        Args:
            constraints (amplify.ConstraintList): The constraints to set.
        """
        self._constraints = constraints

    def solve(
        self,
        constraint_weight: float = 1.0,
        max_retries: int = 10,
    ) -> tuple[list[npt.NDArray[np.float64]], amplify.Result]:
        """Solve the given problem.

        The return value is lists of solutions in binary variables that this class holds.
        When some of the variables are not contained in the given problem,
        default values are used for those variables.

        Args:
            constraint_weight (float): Weight of constraints. Defaults to 1.0.
            max_retries (int, optional): Max number of retries when no feasible solution is found. Defaults to 10.

        Returns:
            tuple[list[npt.NDArray[np.float64]], amplify.Result]: List of solutions in Amplify SDK's variables and
            the Amplify SDK's raw result.
        """
        model = amplify.Model(self.objective, constraint_weight * self.constraints)
        for _ in range(max_retries):
            result = amplify.solve(model, self._client)
            if len(result) > 0:
                break
            # if feasible solution is found, double constraints' weight to retry
            model.constraints *= 2
        if len(result) == 0:
            logger.warning("No feasible solution was found. Increase max_retries", stacklevel=2)

        # return solution in binary variables
        return [self._variables.evaluate(r.values) for r in result], result
