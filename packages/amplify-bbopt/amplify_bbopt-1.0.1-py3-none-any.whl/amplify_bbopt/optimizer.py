from __future__ import annotations

import copy
import time
from logging import getLogger
from typing import Final, Generic, NamedTuple, TypeVar

import amplify
import numpy as np
import numpy.typing as npt

from .amplify_model import AmplifyModel
from .bbopt_logging import AMPLIFY_BBOPT_LOGGER_NAME
from .blackbox import BlackBoxFuncBase
from .encoder import EncodingInfo, decode_values, encode_constraints, encode_input, encode_variables
from .surrogate import SurrogateModel
from .trainer import Dataset, Trainer

_T = TypeVar("_T", bound=Trainer)
_C = TypeVar("_C", bound=amplify.AmplifyClient)

_default_client = amplify.FixstarsClient()

logger = getLogger(AMPLIFY_BBOPT_LOGGER_NAME)


class FlattenedSolution(NamedTuple):
    """Represents the flattened solution set.

    This class holds three types of flattened solution:

    - `blackbox` solution is the original solution for the black-box function.

    - `surrogate` solution is the solution for the surrogate model (subject to encoding for `pre-encoding=True` setting).

    - `amplify` solution is the solution for the Amplify model (subject to encoding regardless of pre-encoding setting).

    Attributes:
        blackbox (npt.NDArray[np.float64]): The solution for the black-box function.
        surrogate (npt.NDArray[np.float64]): The solution for the surrogate model.
        amplify (npt.NDArray[np.float64]): The solution for the Amplify model.
    """

    blackbox: npt.NDArray[np.float64]
    surrogate: npt.NDArray[np.float64]
    amplify: npt.NDArray[np.float64]


class IterationResult(NamedTuple):
    """A class to represent the result of an iteration.

    Attributes:
        annealing_best_solution (Solution): The best solution found by the annealing process.
        annealing_new_solution (Solution | None): The new (unique) solution found by the annealing process.
        fallback_solution (Solution | None): The fallback solution if the annealing process did not find a new (unique) solution.
        timing (Timing | None): The timing information for the iteration.
        surrogate_model_info (SurrogateModelInfo | None): Information about the surrogate model, such as correlation coefficients.
        amplify_result (amplify.Result | None): The raw result from the Amplify SDK.
    """  # noqa: E501

    class Timing(NamedTuple):
        """A class to represent the timing information for an iteration.

        Attributes:
            training (float): Time taken for training the surrogate model.
            minimization (float): Time taken for minimizing the surrogate model (annealing).
            find_unique_solution (float): Time taken to find a unique solution.
            fallback (float): Time taken for fallback solution generation.
            update_dataset (float): Time taken to update the training dataset.
            update_history (float): Time taken to update the optimization history.
        """

        minimization: float = 0.0
        training: float = 0.0
        find_unique_solution: float = 0.0
        fallback: float = 0.0
        update_dataset: float = 0.0
        update_history: float = 0.0

    class SurrogateModelInfo(NamedTuple):
        """Information about the surrogate model.

        Attributes:
            corrcoef (dict[int, float]): Lower percentile correlation coefficients for the surrogate model.
        """

        corrcoef: dict[int, float]

    annealing_best_solution: Solution
    annealing_new_solution: Solution | None = None
    fallback_solution: Solution | None = None
    timing: IterationResult.Timing | None = None
    surrogate_model_info: SurrogateModelInfo | None = None
    amplify_result: amplify.Result | None = None


class Solution(NamedTuple):
    """Represents a solution in the optimization process.

    Attributes:
        values (dict[str, list[float | int] | float | int]): The values of the solution.
        objective (float): The objective value of the solution.
    """

    values: dict[str, list[float | int] | float | int]
    objective: float


class Optimizer(Generic[_T, _C]):
    def __init__(
        self,
        blackbox: BlackBoxFuncBase,
        trainer: _T,
        client: _C = _default_client,
        *,
        training_data: Dataset | None = None,
        constraints: amplify.Constraint | amplify.ConstraintList | None = None,
        pre_encoding: bool = True,
        seed: int = 0,
    ) -> None:
        """Initialize the optimizer.

        Args:
            blackbox (BlackBoxFuncBase): A black-box function defined with the `@blackbox` decorator.
            trainer (_T): A `Trainer` class instance.
            client (_C, optional): A solver client defined with the Amplify SDK. Defaults to `_default_client`.
            training_data (Dataset | None): A training dataset for the surrogate model. Defaults to `None`.
            constraints (amplify.Constraint | amplify.ConstraintList | None, optional): Constraints. Defaults to `None`.
            pre_encoding (bool, optional): Whether to perform pre-encoding (`True`) or post-encoding (`False`). Defaults to `True`.
            seed (int, optional): A random seed. Defaults to `0`.

        Raises:
            TypeError: If `blackbox` is not an subclass of `BlackBoxFuncBase`.
            TypeError: If `trainer` is not an instance of `Trainer`.
            TypeError: If `client` is not an instance of `amplify.AmplifyClient`.
            TypeError: If `training_data` is not an instance of `Dataset` or `None`.
            TypeError: If `constraints` is not an instance of `amplify.Constraint`, `amplify.ConstraintList` or `None`.
        """  # noqa: E501
        if not isinstance(blackbox, BlackBoxFuncBase):
            raise TypeError("blackbox must be an subclass of BlackBoxFuncBase")
        if not isinstance(trainer, Trainer):
            raise TypeError("trainer must be an instance of Trainer")
        if not isinstance(client, amplify.AmplifyClient):
            raise TypeError("client must be an instance of amplify.AmplifyClient")
        if training_data is not None and not isinstance(training_data, Dataset):
            raise TypeError("training_data must be an instance of Dataset")
        if constraints is not None and not isinstance(constraints, amplify.Constraint | amplify.ConstraintList):
            raise TypeError("constraints must be an instance of amplify.Constraint or amplify.ConstraintList")
        if isinstance(constraints, amplify.Constraint):
            constraints = amplify.ConstraintList([constraints])
        elif constraints is None:
            constraints = amplify.ConstraintList()

        # User-defined black-box function and constraints
        self._blackbox = blackbox
        self._blackbox_var_values = blackbox.flattened_variables_dict.values()
        self._constraints = constraints

        # encoding info
        self._enc_info = encode_variables(self._blackbox_var_values)

        # make training dataset for surrogate model
        if training_data is not None and len(training_data.x) > 0:
            # training dataset for surrogate model
            self._training_data = training_data
            self._surrogate_training_data = (
                Dataset(encode_input(self._training_data.x, self._blackbox_var_values), self._training_data.y)
                if pre_encoding
                else self._training_data
            )
        else:
            self._training_data = Dataset.empty(len(self._blackbox_var_values))
            self._surrogate_training_data = (
                Dataset.empty(len(self._enc_info.variables)) if pre_encoding else self._training_data
            )

        # surrogate model
        surrogate_vars = (
            self._enc_info.variables
            if pre_encoding
            else amplify.PolyArray([v.to_poly() for v in self._blackbox_var_values])
        )
        self._surrogate_model = SurrogateModel(surrogate_vars, trainer)

        # Amplify model
        self._amplify_model = AmplifyModel(self._enc_info.variables, client)
        self._amplify_model.constraints = (
            encode_constraints(self._constraints, self._enc_info.mapping) + self._enc_info.constraints
        )

        # History of optimization
        self._history: list[IterationResult] = []

        # misc
        self._pre_encoding: Final[bool] = pre_encoding
        self._num_initial_data: Final[int] = len(self._training_data.x)
        self._rng = np.random.default_rng(seed=seed)

    @property
    def blackbox(self) -> BlackBoxFuncBase:
        """Returns the black-box function."""
        return self._blackbox

    @property
    def training_data(self) -> Dataset:
        """Returns the training data for the black-box function."""
        return self._training_data

    @property
    def surrogate_training_data(self) -> Dataset:
        """Returns the training data for the surrogate model (encoded if `pre_encoding` is True)."""
        return self._surrogate_training_data

    @property
    def initial_training_data(self) -> Dataset:
        """Returns the initial training data for the black-box function."""
        return Dataset(self._training_data.x[: self._num_initial_data], self._training_data.y[: self._num_initial_data])

    @property
    def surrogate_model(self) -> SurrogateModel:
        """Returns the surrogate model."""
        return self._surrogate_model

    @property
    def amplify_model(self) -> AmplifyModel:
        """Returns the amplify model."""
        return self._amplify_model

    @property
    def encoding_info(self) -> EncodingInfo:
        """Returns the encoding information for the black-box function."""
        return self._enc_info

    def _solution_from_flattened_values(
        self, flattened_values: list[float | int]
    ) -> dict[str, list[float | int] | float | int]:
        flattened_values_dict = {
            k: flattened_values[i] for i, k in enumerate(self._blackbox.flattened_variables_dict.keys())
        }
        return {
            k: [flattened_values_dict[v_in] for v_in in v] if isinstance(v, list) else flattened_values_dict[v]
            for k, v in self._blackbox.mapping.items()
        }

    @property
    def best(self) -> Solution:
        """Returns the best solution found so far."""
        idx = np.argmin(self._training_data.y)
        return Solution(
            values=self._solution_from_flattened_values(self._training_data.x[idx].tolist()),
            objective=float(self._training_data.y[idx]),
        )

    @property
    def history(self) -> list[IterationResult]:
        """Returns the history of optimization iterations."""
        return self._history

    @property
    def rng(self) -> np.random.Generator:
        """Returns the random number generator used in the optimizer."""
        return self._rng

    def _mutate_solution(self, solution: npt.NDArray[np.float64]) -> None:
        # Randomly select an index
        var_idx = self._rng.integers(len(self._blackbox.flattened_variables_dict))

        # Randomly select a value from the possible values
        var_name = list(self._blackbox.flattened_variables_dict.keys())[var_idx]
        possible_values = self._blackbox.flattened_variables_dict[var_name].possible_values

        if isinstance(possible_values, tuple):
            # Real except DiscretizationEncoding
            lower_bound, upper_bound = possible_values
            solution[var_idx] = (lower_bound - upper_bound) * self._rng.random() + lower_bound
        else:
            # Otherwise
            assert isinstance(possible_values, list)
            ref_value = solution[var_idx]
            alt_value_idx = np.argmin(np.abs(possible_values - ref_value)) + self._rng.choice([-1, 1])
            alt_value_idx = (alt_value_idx + len(possible_values)) % len(possible_values)
            solution[var_idx] = possible_values[alt_value_idx]

    def _generate_mutated_solutions(self, solution_blackbox: npt.NDArray[np.float64]) -> list[npt.NDArray[np.float64]]:
        """Generate mutated inputs for black-box function.

        Args:
            solution_blackbox (npt.NDArray[np.float64]): The reference solution for the black-box function. This is typically a duplicate solution.

        Returns:
            list[npt.NDArray[np.float64]]: Mutated solutions.
        """  # noqa: E501
        solution_cpy = solution_blackbox.copy()
        self._mutate_solution(solution_cpy)

        # Unconstrained: return a mutated solution
        if len(self._constraints) == 0:
            return [solution_cpy]

        # Constrained: Find another solution near the reference solution
        # The result contains values for all the variables in self._blackbox.flattened_variables_dict.
        obj = amplify.sum([(var - solution_cpy[i]) ** 2 for i, var in enumerate(self._blackbox_var_values)])
        self._amplify_model.objective = obj.substitute(self._enc_info.mapping)
        feasible_result, _ = self._amplify_model.solve()
        return [decode_values(self._enc_info, r) for r in feasible_result]

    def _generate_random_solutions(self) -> list[npt.NDArray[np.float64]]:
        """Generate random inputs for black-box function.

        Returns:
            list[npt.NDArray[np.float64]]: Random inputs.
        """

        def generate_random_solution() -> dict[str, float | int]:
            random_vector: dict[str, float | int] = {}
            for name, var in self._blackbox.flattened_variables_dict.items():
                possible_values = var.possible_values
                if isinstance(possible_values, list):
                    random_vector[name] = self._rng.choice(np.array(possible_values))
                else:
                    assert isinstance(possible_values, tuple)
                    lower_bound, upper_bound = possible_values
                    random_vector[name] = (upper_bound - lower_bound) * self._rng.random() + lower_bound
            return random_vector

        # Unconstrained: Return a random solution
        if len(self._constraints) == 0:
            return [np.array(list(generate_random_solution().values()))]

        # Constrained: Solve with only constraints
        self._amplify_model.objective = amplify.Poly()
        feasible_solutions_amplify, _ = self._amplify_model.solve()
        feasible_solutions_blackbox = [decode_values(self._enc_info, r) for r in feasible_solutions_amplify]

        # Construct solutions
        solutions: list[npt.NDArray[np.float64]] = []
        for s_bbx in feasible_solutions_blackbox:
            # For variables not included in the constraints, generate random values
            random_solution_blackbox = generate_random_solution()
            for i, k in enumerate(self._blackbox.flattened_variables_dict.keys()):
                if k in {var.name for c in self._constraints for var in c.conditional[0].variables}:
                    random_solution_blackbox[k] = float(s_bbx[i])
            solutions.append(np.array(list(random_solution_blackbox.values())))
        return solutions

    def _encode_blackbox_solution(self, blackbox_solution: npt.NDArray) -> FlattenedSolution:
        encoded_solution = encode_input(blackbox_solution, self._blackbox_var_values)
        surrogate_solution = encoded_solution if self._pre_encoding else blackbox_solution
        return FlattenedSolution(blackbox_solution, surrogate_solution, encoded_solution)

    def _search_dataset(self, solution: FlattenedSolution) -> int | None:
        return self._surrogate_training_data.find(solution.surrogate)

    def train_surrogate(self) -> None:
        """Train the surrogate model."""
        self._surrogate_model.train(self._surrogate_training_data)

    def minimize_surrogate(self, max_retries: int = 10) -> tuple[list[FlattenedSolution], amplify.Result]:
        """Find solutions that minimize the surrogate model.

        Args:
            max_retries (int, optional): Maximum number of retries for annealing. Defaults to 10.

        Returns:
            tuple[list[FlattenedSolution], amplify.Result]: List of optimized solutions and the Amplify SDK's raw result. Solutions are in order of the objective value (from lowest to highest).
        """  # noqa: E501
        # Solve the Amplify model
        poly = self._surrogate_model.to_poly()
        if not self._pre_encoding:
            poly = poly.substitute(self._enc_info.mapping)
        self._amplify_model.objective = poly
        solutions_amplify, amplify_result = self._amplify_model.solve(
            np.abs(self._surrogate_training_data.y).max(), max_retries
        )

        # Decode the result for black-box and surrogate models
        solutions: list[FlattenedSolution] = []
        for s_amplify in solutions_amplify:
            s_decoded = decode_values(self._enc_info, s_amplify)
            solutions.append(
                FlattenedSolution(s_decoded, s_amplify, s_amplify)
                if self._pre_encoding
                else FlattenedSolution(s_decoded, s_decoded, s_amplify)
            )
        return solutions, amplify_result

    def evaluate_objective(self, solution: FlattenedSolution, use_cache: bool = False) -> float:
        """Evaluate the objective function for a given solution.

        Args:
            solution (FlattenedSolution): The solution to evaluate.
            use_cache (bool, optional): Whether to use cached results. Defaults to False.

        Returns:
            float: The objective value for the given solution.
        """
        cache_idx = self._search_dataset(solution) if use_cache else None
        return (
            self._blackbox.evaluate({
                var.name: int(val)
                if var.type in {amplify.VariableType.Integer, amplify.VariableType.Binary, amplify.VariableType.Ising}
                else float(val)
                for var, val in zip(
                    self._blackbox.flattened_variables_dict.values(),
                    solution.blackbox,
                    strict=True,
                )
            })
            if cache_idx is None
            else self._training_data.y[cache_idx]
        )

    def add_solution(self, solution: FlattenedSolution, objective: float) -> None:
        """Add a new solution to the training data.

        Args:
            solution (FlattenedSolution): The solution to add.
            objective (float): The objective value for the solution.
        """
        self._training_data.append(solution.blackbox, objective)
        if self._pre_encoding:
            self._surrogate_training_data.append(solution.surrogate, objective)
        else:
            assert self._training_data is self._surrogate_training_data

    def find_unique_solution(self, solutions: list[FlattenedSolution]) -> FlattenedSolution | None:
        """Find a unique solution from a list of solutions.

        Args:
            solutions (list[FlattenedSolution]): The list of solutions to search.

        Returns:
            FlattenedSolution | None: The unique solution if found, otherwise `None`.
        """
        for sol in solutions:
            if self._search_dataset(sol) is None:
                return sol
        return None

    def fallback_solution(self, solutions: list[FlattenedSolution], max_trials: int) -> FlattenedSolution | None:
        """Try to find an alternative solution when only duplicate solutions are returned from annealing.

        If user-defined constraints are given to the optimizer, the generated fallback solution is expected to satisfy the constraints.

        Args:
            solutions (list[FlattenedSolution]): The duplicate input vectors (solutions of the optimization).
            max_trials (int): The max number of trials to find an alternative solution that satisfies the given constraints if any. If `max_trials` is `0` or `max_trials` runs out, the first solution (annealing best) is returned regardless of the uniqueness of the solution.

        Returns:
            FlattenedSolution | None: The alternative solution if found, otherwise `None`.

        Raises:
            ValueError: If `max_trials` is less than `0`.
        """  # noqa: E501
        if max_trials < 0:
            raise ValueError("max_trials must be greater than or equal to 0")

        if max_trials == 0:
            return solutions[0]

        # Step 1: Try to find mutated solutions
        for r in solutions:
            for _ in range(max_trials):
                mutated_inputs_blackbox = self._generate_mutated_solutions(r.blackbox)
                for x_blackbox in mutated_inputs_blackbox:
                    solution = self._encode_blackbox_solution(x_blackbox)
                    if self._search_dataset(solution) is None:
                        return solution

        logger.warning("No mutated solution was found in fallback", stacklevel=2)

        # Step 2: If no mutated solution has been found, append a random solution
        for _ in range(max_trials):
            random_inputs_blackbox = self._generate_random_solutions()
            for x_blackbox in random_inputs_blackbox:
                solution = self._encode_blackbox_solution(x_blackbox)
                if self._search_dataset(solution) is None:
                    return solution

        logger.warning("No random solution was found in fallback", stacklevel=2)
        return None

    def optimize(self, num_iterations: int, max_deduplication_trials: int | None = None) -> None:
        """Optimize the black-box function.

        Args:
            num_iterations (int):  The number of iterations to perform.
            max_deduplication_trials (int | None, optional): The maximum number of trials to find an alternative solution when duplicate solutions are returned from annealing. If 0 is set, the first solution (annealing best) is returned regardless of the uniqueness of the solution. If `None` is given, it is set as the number of variables in the black-box function. Defaults to None.

        Raises:
            ValueError: If `num_iterations` is less than or equal to `0`.
            ValueError: If `max_deduplication_trials` is less than `0`.
            RuntimeError: If no feasible solution was found in the iteration.
        """  # noqa: E501
        if num_iterations <= 0:
            raise ValueError("num_iterations must be greater than 0")

        if max_deduplication_trials is None:
            max_deduplication_trials = len(self._blackbox.flattened_variables_dict)

        if max_deduplication_trials < 0:
            raise ValueError("max_deduplication_trials must be greater than or equal to 0")

        for n_iter in range(num_iterations):
            logger.info(f"=== Iteration: {n_iter + 1}/{num_iterations} ===")
            # Step 1: Train surrogate model
            start_training = time.perf_counter()
            self.train_surrogate()
            time_training = time.perf_counter() - start_training

            # Step 2: Minimize surrogate model
            start_minimization = time.perf_counter()
            solutions, amplify_result = self.minimize_surrogate()
            if len(solutions) == 0:
                raise RuntimeError(f"No feasible solution was found in iteration {n_iter}")
            time_minimization = time.perf_counter() - start_minimization

            # Step 3: Find a unique solution
            start_find_unique = time.perf_counter()
            unique_solution = self.find_unique_solution(solutions)
            time_find_unique_solution = time.perf_counter() - start_find_unique

            # Step 4: Find an alternative solution if no unique solution was found
            start_fallback = time.perf_counter()
            fallback_solution = (
                self.fallback_solution(solutions, max_deduplication_trials) if unique_solution is None else None
            )
            time_fallback = time.perf_counter() - start_fallback

            # Step 5: Add the unique or alternative solution to the training data
            start_update_dataset = time.perf_counter()
            new_solution = unique_solution or fallback_solution
            new_objective: float | None = None
            assert new_solution is not None
            new_objective = self.evaluate_objective(new_solution)
            self.add_solution(new_solution, new_objective)
            time_update_dataset = time.perf_counter() - start_update_dataset

            # Step 6: Update history
            start_update_history = time.perf_counter()
            best_objective = (
                new_objective  # case when best solution is unique
                if unique_solution is not None and np.array_equal(solutions[0].blackbox, unique_solution.blackbox)
                else self.evaluate_objective(solutions[0], use_cache=True)
            )
            # The alternative solution is identical to new_solution if it is not None
            fallback_objective = None if fallback_solution is None else new_objective
            time_update_history = time.perf_counter() - start_update_history

            # Append the iteration result to the history
            assert best_objective is not None, "best_objective must not be None"
            self._history.append(
                IterationResult(
                    annealing_best_solution=Solution(
                        self._solution_from_flattened_values(solutions[0].blackbox.tolist()), best_objective
                    ),
                    annealing_new_solution=Solution(
                        self._solution_from_flattened_values(unique_solution.blackbox.tolist()), new_objective
                    )
                    if unique_solution is not None
                    else None,
                    fallback_solution=Solution(
                        self._solution_from_flattened_values(fallback_solution.blackbox.tolist()), fallback_objective
                    )
                    if fallback_solution is not None and fallback_objective is not None
                    else None,
                    timing=IterationResult.Timing(
                        time_training,
                        time_minimization,
                        time_find_unique_solution,
                        time_fallback,
                        time_update_dataset,
                        time_update_history,
                    ),
                    surrogate_model_info=IterationResult.SurrogateModelInfo(
                        corrcoef=copy.deepcopy(self.surrogate_model.trainer.low_percentile_corrcoefs)
                    ),
                    amplify_result=amplify_result,
                )
            )

            logger.info(f"   objective: {float(self._training_data.y[-1]):.3e}")
            logger.info(f"current best: {float(self.best.objective):.3e}")

    def add_random_training_data(self, num_data: int, max_trials: int | None = None) -> None:
        """Add randomly generated solution vectors to the training data.

        If user-defined constraints are given to the optimizer, the random solutions are generated to satisfy the constraints.

        Args:
            num_data (int): The number of solutions to be added.
            max_trials (int | None, optional): The max number of trials. This value must be greater than or equal to
            `num_data`. If `None` is given `max_trials` is set as `2 * num_data`. Defaults to None.

        Raises:
            ValueError: If `max_trials` is less than `num_data`.
        """  # noqa: E501
        if max_trials is None:
            max_trials = 2 * num_data
        if max_trials < num_data:
            raise ValueError("max_trials must be greater than or equal to num_data")

        # Add random solutions to the training data
        num_append: int = 0
        for _ in range(max_trials):
            random_inputs_blackbox = self._generate_random_solutions()
            for x_blackbox in random_inputs_blackbox:
                solution = self._encode_blackbox_solution(x_blackbox)
                if self._search_dataset(solution) is None:
                    logger.info(f"Random data sample: {num_append + 1}/{num_data}")
                    self.add_solution(solution, self.evaluate_objective(solution))
                    num_append += 1
                if num_append == num_data:
                    break
            if num_append == num_data:
                break

        if num_append < num_data:
            logger.warning(f"Not enough unique initial data was generated: {num_append}/{num_data}", stacklevel=2)
