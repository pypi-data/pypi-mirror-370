from __future__ import annotations

import copy
import sys
from abc import ABC, abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING, Any, Final

import numpy as np
import torch
from torch.optim.adamw import AdamW
from torch.utils.data import DataLoader, TensorDataset, random_split

from .bbopt_logging import AMPLIFY_BBOPT_LOGGER_NAME

if TYPE_CHECKING:
    from collections.abc import Callable

    import amplify
    from numpy.typing import NDArray

logger = getLogger(AMPLIFY_BBOPT_LOGGER_NAME)


def compute_low_percentile_corrcoefs(
    y_values: NDArray[np.float64],
    y_predict: NDArray[np.float64],
    percentile_cutoffs: list[int],
) -> dict[int, float]:
    """Compute the lower percentile correlation coefficients.

    Args:
        y_values (NDArray[np.float64]): The true values.
        y_predict (NDArray[np.float64]): The predicted values.
        percentile_cutoffs (list[int]): The percentile cutoffs.

    Returns:
        dict[int, float]: The lower percentile correlation coefficients.
    """

    def corrcoef(
        y_values: NDArray[np.float64],
        y_predict: NDArray[np.float64],
    ) -> float:
        return float(np.corrcoef(y_values, y_predict)[0, 1])

    corrcoefs: dict[int, float] = {}
    for cutoff in percentile_cutoffs:
        lower_tail = y_values <= np.percentile(y_values, cutoff)
        corrcoefs[cutoff] = corrcoef(y_values[lower_tail], y_predict[lower_tail]) if np.sum(lower_tail) > 1 else np.nan
    return corrcoefs


def format_low_tail_corrcoefs(
    corrcoefs: dict[int, float] | None,
) -> str | None:
    """Format lower percentile correlation coefficients for display.

    Returns:
        str | None: A formatted string representing the lower percentile correlation coefficients.
    """
    if corrcoefs is None:
        return None
    return ", ".join(f"<={k}%: {v:.3f}" if k < 100 else f"all: {v:.3f}" for k, v in corrcoefs.items())  # noqa: PLR2004


class Dataset:
    """Represents a dataset for surrogate model training."""

    def __init__(self, x: np.ndarray, y: np.ndarray) -> None:
        """Initializes a dataset for surrogate model training.

        Args:
            x (np.ndarray): The input features (must be flattened).
            y (np.ndarray): The target values.
        """
        self._x: NDArray[np.float64] = np.array(x)
        self._y: NDArray[np.float64] = np.array(y)
        self._check()

    def _check(self) -> None:
        dim_x: Final[int] = 2
        if self._x.ndim != dim_x:
            raise ValueError("x must be a two-dimensional numpy array")
        if self._y.ndim != 1:
            raise ValueError("y must be a one-dimensional numpy array")

        if self._x.shape[0] != self._y.shape[0]:
            raise ValueError("x and y must have the same number of rows")

    @classmethod
    def empty(cls, num_variables: int) -> Dataset:
        """Creates an empty dataset for surrogate model training.

        Args:
            num_variables (int): The number of input variables.

        Returns:
            Dataset: An empty dataset.
        """
        return cls(np.empty((0, num_variables)), np.empty(0))

    def append(self, x: np.ndarray, y: float | np.ndarray) -> None:
        """Appends a new data point to the dataset.

        Args:
            x (np.ndarray): The input features (must be flattened).
            y (float | np.ndarray): The target value(s).
        """
        self._x = np.vstack((self._x, x))
        self._y = np.append(self._y, y)

        self._check()

    @property
    def x(self) -> NDArray[np.float64]:
        """Returns the input features of the dataset, flattened."""
        return self._x

    @property
    def y(self) -> NDArray[np.float64]:
        """Returns the target values of the dataset."""
        return self._y

    def __len__(self) -> int:
        return len(self._y)

    def __iter__(self) -> zip[tuple[NDArray[np.float64], float]]:
        return zip(self._x, self._y, strict=True)

    def find(self, x: NDArray[np.float64]) -> int | None:
        """Finds the index of a data point in the dataset.

        Args:
            x (NDArray[np.float64]): The input features of the data point to find.

        Raises:
            ValueError: If the input shape is not 1-dimensional or does not match the number of features in the model.
            ValueError: If the input features do not match any data point in the dataset.

        Returns:
            int | None: The index of the data point in the dataset, or None if not found.
        """
        if len(x.shape) != 1:
            raise ValueError("The input shape must be 1-dimensional.")
        if len(x) != self._x.shape[1]:
            raise ValueError("The input length must match the number of features in the model.")

        indices = np.where(np.all(self._x == x, axis=1))
        if len(indices[0]) == 0:
            return None
        return indices[0][0]


class Trainer(ABC):
    """Base class for surrogate model trainers."""

    def __init__(self) -> None:
        """Initializes the trainer with default settings."""
        self._percentile_cutoffs: list[int] = [10, 25, 50, 100]
        self._low_percentile_corrcoefs: dict[int, float] | None = None

    @property
    def percentile_cutoffs(self) -> list[int]:
        """Returns the lower percentile cutoffs for the trainer."""
        return self._percentile_cutoffs

    @percentile_cutoffs.setter
    def percentile_cutoffs(self, value: list[int]) -> None:
        if len(value) == 0:
            raise ValueError("The lower percentile cutoffs must not be empty.")
        if any(v < 0 or v > 100 for v in value):  # noqa: PLR2004
            raise ValueError("The lower percentile cutoffs must be between 0 and 100.")
        self._percentile_cutoffs = value

    @property
    def low_percentile_corrcoefs(self) -> dict[int, float] | None:
        """Returns the lower percentile correlation coefficients of the last trained model."""
        return self._low_percentile_corrcoefs

    @abstractmethod
    def train(self, dataset: Dataset) -> None:
        """Trains the surrogate model on the given dataset.

        Args:
            dataset (Dataset): The dataset to train on.
        """
        pass  # noqa: PIE790

    @abstractmethod
    def to_poly(self, x: amplify.PolyArray) -> amplify.Poly:
        """Converts a trained model to QUBO model as amplify.Poly.

        Args:
            x (amplify.PolyArray): The Amplify SDK's variables as amplify.PolyArray.

        Returns:
            amplify.Poly: The converted QUBO model as amplify.Poly.
        """
        pass  # noqa: PIE790

    @property
    @abstractmethod
    def model(self) -> object | None:
        """Returns the trained model."""
        pass  # noqa: PIE790


class TorchFM(torch.nn.Module):
    """Factorization Machine model implemented in PyTorch."""

    def __init__(self, d: int, k: int) -> None:
        """Initializes the Factorization Machine model.

        Args:
            d (int): The number of input features.
            k (int): The number of factors.
        """
        super().__init__()
        self._d = d
        self._k = k
        self._v = torch.randn((d, k), requires_grad=True)
        self._w = torch.randn((d,), requires_grad=True)
        self._w0 = torch.randn((), requires_grad=True)

    @property
    def num_factors(
        self,
    ) -> int:
        """Returns the number of factors in the model."""
        return self._k

    @property
    def num_features(self) -> int:
        """Returns the number of input features in the model."""
        return self._d

    @property
    def quadratic(self) -> torch.Tensor:
        """Returns the quadratic weights of the model."""
        return self._v

    @property
    def linear(self) -> torch.Tensor:
        """Returns the linear weights of the model."""
        return self._w

    @property
    def bias(self) -> torch.Tensor:
        """Returns the bias term of the model."""
        return self._w0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Computes the forward pass of the model.

        Args:
            x (torch.Tensor): The input tensor.

        Returns:
            torch.Tensor: The output tensor.
        """
        out_linear = torch.matmul(x, self._w) + self._w0
        out_1 = torch.matmul(x, self._v).pow(2).sum(1)
        out_2 = torch.matmul(x.pow(2), self._v.pow(2)).sum(1)
        out_quadratic = 0.5 * (out_1 - out_2)

        return out_linear + out_quadratic


class FMTrainer(Trainer):
    """Trainer for Factorization Machine models."""

    def __init__(self, num_threads: int | None = 8) -> None:
        """Initializes the trainer for Factorization Machine models.

        Args:
            num_threads (int | None, optional): The number of threads to use for training. Defaults to 8.
        """
        super().__init__()

        if num_threads is not None:
            torch.set_num_threads(num_threads)

        self._fm: TorchFM | None = None
        self._num_factors: int = 10

        # Set default training parameters
        self._batch_size: int = 8
        self._epochs: int = 2000
        self._loss: type[torch.nn.modules.loss._Loss] = torch.nn.MSELoss
        self._optimizer: type[torch.optim.optimizer.Optimizer] = AdamW
        self._optimizer_params: dict[str, Any] = {"lr": 0.5}
        self._lr_scheduler: type[torch.optim.lr_scheduler.LRScheduler] | None = torch.optim.lr_scheduler.StepLR
        self._lr_scheduler_params: dict[str, Any] = {"step_size": 100, "gamma": 0.8}
        self._train_data_split_ratio: float = 0.8

    @property
    def model(self) -> TorchFM | None:
        """Returns the trained Factorization Machine model."""
        return self._fm

    @property
    def num_factors(self) -> int:
        """Returns the number of factors in the model."""
        return self._num_factors

    @num_factors.setter
    def num_factors(self, value: int) -> None:
        """Sets the number of factors in the model."""
        self._num_factors = value

    @property
    def batch_size(self) -> int:
        """Returns the batch size for training."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: int) -> None:
        """Sets the batch size for training."""  # noqa: DOC501
        if value <= 1:
            raise ValueError("The batch size must be a greater than 0.")
        self._batch_size = value

    @property
    def epochs(self) -> int:
        """Returns the number of epochs for training."""
        return self._epochs

    @epochs.setter
    def epochs(self, value: int) -> None:
        """Sets the number of epochs for training."""
        self._epochs = value

    @property
    def loss_class(self) -> type[torch.nn.modules.loss._Loss]:
        """Returns the loss function class used for training."""
        return self._loss

    @loss_class.setter
    def loss_class(self, value: type[torch.nn.modules.loss._Loss]) -> None:
        """Sets the loss function class used for training.

        Args:
            value (type[torch.nn.modules.loss._Loss]): The loss function class.
        """
        self._loss = value

    @property
    def optimizer_class(self) -> type[torch.optim.optimizer.Optimizer]:
        """Returns the optimizer class used for training."""
        return self._optimizer

    @optimizer_class.setter
    def optimizer_class(self, value: type[torch.optim.optimizer.Optimizer]) -> None:
        """Sets the optimizer class used for training.

        Args:
            value (type[torch.optim.optimizer.Optimizer]): The optimizer class.
        """
        self._optimizer = value

    @property
    def optimizer_params(self) -> dict[str, Any]:
        """Returns the parameters for the optimizer used for training."""
        return self._optimizer_params

    @optimizer_params.setter
    def optimizer_params(self, value: dict[str, Any]) -> None:
        """Sets the parameters for the optimizer used for training.

        Args:
            value (dict[str, Any]): The optimizer parameters.
        """
        self._optimizer_params = value

    @property
    def lr_scheduler_class(self) -> type[torch.optim.lr_scheduler.LRScheduler] | None:
        """Returns the learning rate scheduler class used for training."""
        return self._lr_scheduler

    @lr_scheduler_class.setter
    def lr_scheduler_class(self, value: type[torch.optim.lr_scheduler.LRScheduler] | None) -> None:
        """Sets the learning rate scheduler class used for training.

        Args:
            value (type[torch.optim.lr_scheduler.LRScheduler] | None): The learning rate scheduler class.
        """
        self._lr_scheduler = value

    @property
    def lr_scheduler_params(self) -> dict[str, Any]:
        """Returns the parameters for the learning rate scheduler used for training."""
        return self._lr_scheduler_params

    @lr_scheduler_params.setter
    def lr_scheduler_params(self, value: dict[str, Any]) -> None:
        """Sets the parameters for the learning rate scheduler used for training.

        Args:
            value (dict[str, Any]): The learning rate scheduler parameters.
        """
        self._lr_scheduler_params = value

    @property
    def train_data_split_ratio(self) -> float:
        """Returns the ratio of training data split for validation."""
        return self._train_data_split_ratio

    @train_data_split_ratio.setter
    def train_data_split_ratio(self, value: float) -> None:
        """Sets the ratio of training data split for validation.

        Args:
            value (float): The training data split ratio.
        """
        self._train_data_split_ratio = value

    def train(self, dataset: Dataset) -> None:
        """Trains the model using the provided dataset.

        Args:
            dataset (Dataset): The dataset to train on.

        Raises:
            ValueError: If the dataset is empty.
            ValueError: If the number of input values and output values are not the same.
            ValueError: If the input dataset is not 2D.
        """
        input_dataset_dim: Final[int] = 2

        if len(dataset.x) == 0 or len(dataset.y) == 0:
            raise ValueError("The dataset must not be empty.")
        if len(dataset.x) != len(dataset.y):
            raise ValueError("The number of input values and output values must be the same.")
        if len(dataset.x.shape) != input_dataset_dim:
            raise ValueError("The input dataset must be 2D")

        self._fm = TorchFM(dataset.x.shape[1], self._num_factors)

        optimizer = self._optimizer([self._fm.quadratic, self._fm.linear, self._fm.bias], **self._optimizer_params)
        criterion = self._loss()
        scheduler = (
            self._lr_scheduler(optimizer, **self._lr_scheduler_params) if self._lr_scheduler is not None else None
        )
        x_tensor, y_tensor = (
            torch.from_numpy(dataset.x).float(),
            torch.from_numpy(dataset.y).float(),
        )
        tensor_dataset = TensorDataset(x_tensor, y_tensor)

        split_ratio = self._train_data_split_ratio
        if int(len(y_tensor) * split_ratio) * int(len(y_tensor) * (1 - split_ratio)) == 0:
            # If self._train_data_split_ratio is 0 or 1, no data split is intentional
            # so the following warning is suppressed.
            if split_ratio * (1 - split_ratio) > 0:
                logger.warning(
                    f"Either training or validation data will be empty with the given "
                    f"train_data_split_ratio = {split_ratio}. "
                    f"No data split is performed for this cycle.",
                    stacklevel=2,
                )
            train_data = tensor_dataset
            valid_data = tensor_dataset
        else:
            train_data, valid_data = random_split(tensor_dataset, [split_ratio, 1 - split_ratio])

        train_loader = DataLoader(train_data, batch_size=self._batch_size, shuffle=True)
        valid_loader = DataLoader(valid_data, batch_size=self._batch_size, shuffle=True)

        min_loss = sys.float_info.max
        best_parameters = copy.deepcopy(self._fm.state_dict())
        for _ in range(self._epochs):
            # Training
            for x_train, y_train in train_loader:
                optimizer.zero_grad()
                out = self._fm(x_train)
                loss = criterion(out, y_train)
                loss.backward()
                optimizer.step()

            # Validation
            with torch.no_grad():
                loss = 0
                for x_valid, y_valid in valid_loader:
                    y_pred = self._fm(x_valid)
                    loss += criterion(y_pred, y_valid)
                # If the loss is updated, update the parameters
                if loss < min_loss:
                    best_parameters = copy.deepcopy(self._fm.state_dict())
                    min_loss = loss
            if scheduler is not None:
                scheduler.step()

        # Make a model with the parameters with lowest loss in validation
        with torch.no_grad():
            self._fm.load_state_dict(best_parameters)
            self._fm.eval()
            self._low_percentile_corrcoefs = compute_low_percentile_corrcoefs(
                y_values=dataset.y,
                y_predict=self._fm(torch.from_numpy(dataset.x).float()).detach().numpy().ravel(),
                percentile_cutoffs=self._percentile_cutoffs,
            )
            logger.info(f"model corrcoefs: {format_low_tail_corrcoefs(self._low_percentile_corrcoefs)}")

    def to_poly(self, x: amplify.PolyArray[amplify.Dim1]) -> amplify.Poly:
        """Converts a trained model to QUBO model as amplify.Poly.

        Args:
            x (amplify.PolyArray[amplify.Dim1]): The variables in amplify.PolyArray.

        Raises:
            ValueError: If the input array is not 1D.
            ValueError: If the input length does not match the number of features.
            ValueError: If the surrogate model has not been trained.

        Returns:
            amplify.Poly: The resulting QUBO polynomial.
        """
        if self._fm is None:
            raise ValueError("The surrogate model has not been trained yet.")

        if len(x.shape) != 1:
            raise ValueError("The input shape must be 1-dimensional.")

        if len(x) != self._fm.num_features:
            raise ValueError("The input length must match the number of features in the model.")

        v = self._fm.quadratic
        w = self._fm.linear
        w0 = float(self._fm.bias)  # cast 0-dim array to float

        out_linear = w0 + (x * w).sum()
        out_1: amplify.Poly = ((x[:, np.newaxis] * v).sum(axis=0) ** 2).sum()  # type: ignore
        out_2: amplify.Poly = ((x[:, np.newaxis] * v) ** 2).sum()  # type: ignore

        return out_linear + (out_1 - out_2) / 2


class KernelModel:
    """Kernel model class."""

    def __init__(self, beta: float = 0.0, gamma: float = 0.0) -> None:
        """Initializes the KernelModel with given parameters.

        Args:
            beta (float, optional): Weight for 'sigma' in the lower confidence bound (LCB). Defaults to 0.0.
            gamma (float, optional): Weight for a linear term in the model. Defaults to 0.0.
        """
        self._coef_matrix_mu: np.ndarray | None = None
        self._coef_vector_mu: np.ndarray | None = None
        self._coef_matrix_sigma: np.ndarray | None = None
        self._coef_vector_sigma: np.ndarray | None = None

        # A weight for 'sigma' in the lower confidence bound (LCB)
        self._beta: float = beta
        # A weight for a linear term in the model
        self._gamma: float = gamma

    @property
    def coef_matrix(self) -> np.ndarray:
        """Returns the coefficient matrix of the kernel model."""
        assert self._coef_matrix_mu is not None
        if self._beta == 0.0:
            return self._coef_matrix_mu
        assert self._coef_matrix_sigma is not None
        return self._coef_matrix_mu - self._beta * self._coef_matrix_sigma

    @property
    def coef_vector(self) -> np.ndarray:
        """Returns the coefficient vector of the kernel model."""
        assert self._coef_vector_mu is not None
        if self._beta == 0.0:
            return self._coef_vector_mu
        assert self._coef_vector_sigma is not None
        return self._coef_vector_mu - self._beta * self._coef_vector_sigma

    @property
    def coef_matrix_mu(self) -> np.ndarray | None:
        """Returns the coefficient matrix for the mean of the kernel model."""
        return self._coef_matrix_mu

    @coef_matrix_mu.setter
    def coef_matrix_mu(self, value: np.ndarray) -> None:
        """Sets the coefficient matrix for the mean of the kernel model.

        Args:
            value (np.ndarray): The new coefficient matrix.
        """
        self._coef_matrix_mu = value

    @property
    def coef_vector_mu(self) -> np.ndarray | None:
        """Returns the coefficient vector for the mean of the kernel model."""
        return self._coef_vector_mu

    @coef_vector_mu.setter
    def coef_vector_mu(self, value: np.ndarray) -> None:
        """Sets the coefficient vector for the mean of the kernel model.

        Args:
            value (np.ndarray): The new coefficient vector.
        """
        self._coef_vector_mu = value

    @property
    def coef_matrix_sigma(self) -> np.ndarray | None:
        """Returns the coefficient matrix for the sigma of the kernel model."""
        return self._coef_matrix_sigma

    @coef_matrix_sigma.setter
    def coef_matrix_sigma(self, value: np.ndarray) -> None:
        """Sets the coefficient matrix for the sigma of the kernel model.

        Args:
            value (np.ndarray): The new coefficient matrix.
        """
        self._coef_matrix_sigma = value

    @property
    def coef_vector_sigma(self) -> np.ndarray | None:
        """Returns the coefficient vector for the sigma of the kernel model."""
        return self._coef_vector_sigma

    @coef_vector_sigma.setter
    def coef_vector_sigma(self, value: np.ndarray) -> None:
        """Sets the coefficient vector for the sigma of the kernel model.

        Args:
            value (np.ndarray): The new coefficient vector.
        """
        self._coef_vector_sigma = value

    def _predict(self, x: np.ndarray) -> float | np.ndarray:
        """Returns the predicted value of the kernel model.

        Args:
            x (np.ndarray): _description_

        Returns:
            float | np.ndarray: _description_
        """
        if self._gamma == 0.0:
            return x @ self.coef_matrix @ x.T

        return x @ self.coef_matrix @ x.T + 2 * self._gamma * (self.coef_vector[None, :] @ x.T).sum(axis=0)

    def __call__(self, x: np.ndarray) -> np.ndarray | float:
        if x.ndim not in {1, 2}:
            raise ValueError(f"Expected x to have 1 or 2 dimensions, got shape {x.shape}")

        if x.ndim == 1:
            x = x[None, :]  # reshape to (1, n_features) for consistency

        n_features = x.shape[1]
        expected_features = self.coef_matrix.shape[0]

        if n_features != expected_features:
            raise ValueError(f"Input x has {n_features} features, but coef_matrix expects {expected_features}")

        ret = self._predict(x)
        if isinstance(ret, np.ndarray):
            # for multiple predictions
            return np.diag(ret)
        return float(ret)


# Trainer for the kernel model
class KMTrainer(Trainer):
    class GramMatrixHandler:
        """Compute and update the inverse of a Gram matrix sequentially with addition of a new data set."""

        def __init__(self, kernel_func: Callable, init_x: np.ndarray, reg_param: float) -> None:
            """Initialize a Gram matrix with the initial training data.

            Args:
                kernel_func (Callable): A kernel function for Gram matrix.
                init_x (np.ndarray): Input value vectors in the initial training data.
                reg_param (float): A regularization parameter.
            """
            self._kernel_func = kernel_func
            self._reg_param = reg_param
            self._inv_gram_matrix = np.linalg.inv(
                self._kernel_func(init_x, init_x) + self._reg_param * np.eye(len(init_x))
            )
            self._scalar: float = 0.0
            self._vector: np.ndarray = np.array([])
            self._sum_vx: np.ndarray = np.array([])

        @property
        def inv_gram_matrix(self) -> np.ndarray:
            """The inverse of a Gram matrix."""
            return self._inv_gram_matrix

        @property
        def s(self) -> float:
            """The intermediate output scalar, s."""
            return self._scalar

        @property
        def v(self) -> np.ndarray:
            """The intermediate output vector, v."""
            return self._vector

        @property
        def sum_vx(self) -> np.ndarray:
            """sum(x * v)."""
            return self._sum_vx

        def update(self, x: np.ndarray) -> None:
            """Update a Gram matrix and related intermediate variables sequentially with addition of a new data set.

            Args:
                x (np.ndarray): Input value vectors in the training data (with the last element being a newly added input value vector).
            """  # noqa: E501
            x_new = x[-1, :]
            x_all_prev = x[: x.shape[0] - 1, :]
            kernel_vec = self._kernel_func(x_all_prev, x_new[None, :])
            kernel_n = self._kernel_func(x_new[None, :], x_new[None, :])
            self._scalar = (kernel_n + self._reg_param) - kernel_vec.T @ self._inv_gram_matrix @ kernel_vec
            self._vector = self._inv_gram_matrix @ kernel_vec
            a = self._scalar * self._inv_gram_matrix + self._vector @ self._vector.T
            b = -self._vector
            c = -self._vector.T
            d = 1
            self._inv_gram_matrix = np.block([[a, b], [c, d]]) / self._scalar
            self._sum_vx = np.sum(x_all_prev * self._vector, axis=0)

    class PolyCoefMatrixHandler:
        """Compute and update polynomial coefficient matrices and vectors sequentially with addition of a new data set for the kernel-QA optimization."""  # noqa: E501

        def __init__(
            self,
            init_x: np.ndarray,
            init_y: np.ndarray,
            kernel_func_mu: Callable,
            kernel_func_sigma: Callable | None,
            reg_param: float,
        ) -> None:
            """Initialize coefficient matrices and vectors with the initial training data.

            Args:
                init_x (np.ndarray): A list of the input value vectors in the initial training data.
                init_y (np.ndarray): Corresponding output values.
                kernel_func_mu (Callable): A kernel function for the mean.
                kernel_func_sigma (Callable | None): A kernel function for the sigma. When sigma is not considered throughout the optimization (`beta = 0` or `min(beta) = 0` in :obj:`ModelKernel`), set `None`.
                reg_param (float): A regularization parameter.
            """  # noqa: E501
            self._gram_matrix_handler_mu = KMTrainer.GramMatrixHandler(kernel_func_mu, init_x, reg_param)
            self._gram_matrix_handler_sigma: KMTrainer.GramMatrixHandler | None = None

            # Initialize coef_matrix_mu (Q_mu)
            c_hat = self._gram_matrix_handler_mu.inv_gram_matrix @ init_y
            x_c_hat = init_x * c_hat[None, :].T
            self._coef_matrix_mu = x_c_hat.T @ init_x
            self._coef_vector_mu = x_c_hat.sum(axis=0)

            # Initialize coef_matrix_lxx for Q_sigma sequentially.
            num_samples = init_x.shape[0]
            size_input = init_x.shape[1]
            self._coef_matrix_lxx: np.ndarray | None = None
            self._coef_vector_sigma: np.ndarray | None = None
            if kernel_func_sigma is not None:
                self._gram_matrix_handler_sigma = KMTrainer.GramMatrixHandler(kernel_func_sigma, init_x, reg_param)
                inv_gram_matrix_sigma = self._gram_matrix_handler_sigma.inv_gram_matrix
                self._coef_matrix_lxx = np.zeros((size_input, size_input))
                self._coef_vector_sigma = np.zeros(size_input)
                for i in range(num_samples):
                    for j in range(num_samples):
                        xi = init_x[i, :]
                        xj = init_x[j, :]
                        xx = xi[None, :].T @ xj[None, :]
                        self._coef_matrix_lxx += xx * inv_gram_matrix_sigma[i, j]
                        self._coef_vector_sigma += xi * inv_gram_matrix_sigma[i, j]
                self._coef_vector_sigma = (inv_gram_matrix_sigma @ init_x).sum(axis=0)

        @property
        def coef_matrix_mu(self) -> np.ndarray:
            """Returns the coefficient matrix for the mean of the kernel model."""
            return self._coef_matrix_mu

        @property
        def coef_vector_mu(self) -> np.ndarray:
            """Returns the coefficient vector for the mean of the kernel model."""
            return self._coef_vector_mu

        @property
        def coef_matrix_lxx(self) -> np.ndarray | None:
            """Returns the coefficient matrix for the sigma of the kernel model."""
            return self._coef_matrix_lxx

        @property
        def coef_vector_sigma(self) -> np.ndarray | None:
            """Returns the coefficient vector for the sigma of the kernel model."""
            return self._coef_vector_sigma

        def update(self, x: np.ndarray, y: np.ndarray) -> None:
            """Update polynomial coefficient matrices and vectors sequentially with addition of a new data set.

            Args:
                x (np.ndarray): All input value vectors in the training data (with the last element being a newly added input value vector).
                y (np.ndarray): Corresponding output values.
            """  # noqa: E501
            x_new = x[-1, :]
            # Update coef_matrix_lxx for Q_sigma sequentially.
            if self._gram_matrix_handler_sigma is not None:
                self._gram_matrix_handler_sigma.update(x)
                sum_vx = self._gram_matrix_handler_sigma.sum_vx
                a1 = (sum_vx[None, :].T @ sum_vx[None, :]) / self._gram_matrix_handler_sigma.s
                a2 = (
                    -sum_vx[None, :].T @ x_new[None, :] - x_new[None, :].T @ sum_vx[None, :]
                ) / self._gram_matrix_handler_sigma.s
                a3 = (x_new[None, :].T @ x_new[None, :]) / self._gram_matrix_handler_sigma.s
                self._coef_matrix_lxx += a1 + a2 + a3  # type: ignore
                self._coef_vector_sigma = (self._gram_matrix_handler_sigma.inv_gram_matrix @ x).sum(axis=0)

            # Update inv_gram_matrix and compute coef_matrix_mu (Q_mu).
            self._gram_matrix_handler_mu.update(x)
            c_hat = self._gram_matrix_handler_mu.inv_gram_matrix @ y
            x_c_hat = x * c_hat[None, :].T
            self._coef_matrix_mu = x_c_hat.T @ x
            self._coef_vector_mu = x_c_hat.sum(axis=0)

    def __init__(self) -> None:
        """Initializes the trainer for kernel models."""
        super().__init__()

        self._km: KernelModel | None = None
        self._reg_param: float = 1.0
        # A weight for 'sigma' in the lower confidence bound (LCB)
        self._beta: float = 0.0
        # A weight for a linear term in the model
        self._gamma: float = 0.0

        self._matrix_handler: KMTrainer.PolyCoefMatrixHandler | None = None

    @property
    def model(self) -> KernelModel | None:
        """Returns the trained kernel model."""
        return self._km

    @property
    def reg_param(self) -> float:
        """Returns the regularization parameter for the kernel model."""
        return self._reg_param

    @reg_param.setter
    def reg_param(self, value: float) -> None:
        """Sets the regularization parameter for the kernel model.

        Args:
            value (float): The new regularization parameter.
        """
        self._reg_param = value

    @property
    def beta(self) -> float:
        """Returns the weight for 'sigma' in the lower confidence bound (LCB)."""
        return self._beta

    @beta.setter
    def beta(self, value: float) -> None:
        """Sets the weight for 'sigma' in the lower confidence bound (LCB).

        Args:
            value (float): The new weight for 'sigma'.
        """
        self._beta = value

    @property
    def gamma(self) -> float:
        """Returns the weight for a linear term in the model."""
        return self._gamma

    @gamma.setter
    def gamma(self, value: float) -> None:
        """Sets the weight for a linear term in the model.

        Args:
            value (float): The new weight for the linear term.
        """
        self._gamma = value

    def train(self, dataset: Dataset) -> None:
        """Trains the kernel model using the provided dataset.

        Args:
            dataset (Dataset): The dataset to train the model.

        Raises:
            ValueError: If the dataset is empty.
            ValueError: If the number of input values and output values are not the same.
            ValueError: If the input dataset is not 2D.
        """

        def generate_kernel_functions(beta: float) -> tuple[Callable, Callable | None]:
            def kernel_func_mu(x, y):  # noqa: ANN001, ANN202
                return (x @ y.T + self._gamma) ** 2

            def kernel_func_sigma(x, y):  # noqa: ANN001, ANN202
                return x @ y.T + self._gamma

            return (kernel_func_mu, kernel_func_sigma) if beta > 0 else (kernel_func_mu, None)

        self._km = KernelModel(beta=self._beta, gamma=self._gamma)

        dataset_x, dataset_y = dataset.x, dataset.y

        if len(dataset_x) == 0 or len(dataset_y) == 0:
            raise ValueError("The dataset must not be empty.")
        if len(dataset_x) != len(dataset_y):
            raise ValueError("The number of input values and output values must be the same.")

        if self._matrix_handler is None:
            kernel_mu, kernel_sigma = generate_kernel_functions(self._beta)
            self._matrix_handler = KMTrainer.PolyCoefMatrixHandler(
                dataset_x, dataset_y, kernel_mu, kernel_sigma, self._reg_param
            )
        else:
            self._matrix_handler.update(dataset_x, dataset_y)

        # Update model coefficients
        self._km.coef_matrix_mu = self._matrix_handler.coef_matrix_mu
        self._km.coef_vector_mu = self._matrix_handler.coef_vector_mu
        if self._matrix_handler.coef_matrix_lxx is not None:
            self._km.coef_matrix_sigma = (
                np.eye(self._matrix_handler.coef_matrix_lxx.shape[0]) - self._matrix_handler.coef_matrix_lxx
            )
        if self._matrix_handler.coef_vector_sigma is not None:
            self._km.coef_vector_sigma = self._matrix_handler.coef_vector_sigma

        self._low_percentile_corrcoefs = compute_low_percentile_corrcoefs(
            y_values=dataset_y,
            y_predict=self._km(dataset_x),  # type: ignore
            percentile_cutoffs=self._percentile_cutoffs,
        )

        logger.info(f"model corrcoefs: {format_low_tail_corrcoefs(self._low_percentile_corrcoefs)}")

    def to_poly(self, x: amplify.PolyArray[amplify.Dim1]) -> amplify.Poly:
        """Converts a trained kernel model to QUBO model as amplify.Poly.

        Args:
            x (amplify.PolyArray[amplify.Dim1]): The variables in amplify.PolyArray.

        Raises:
            ValueError: If the kernel model has not been trained.
            ValueError: If the input length does not match the number of features.
            ValueError: If the input shape is not 1-dimensional.

        Returns:
            amplify.Poly: The resulting QUBO polynomial.
        """
        if self._km is None:
            raise ValueError("The surrogate model has not been trained yet.")

        if len(x.shape) != 1:
            raise ValueError("The input shape must be 1-dimensional.")

        if len(x) != len(self._km.coef_matrix):
            raise ValueError("The input length must match the size of the coefficient matrix.")

        if len(x) != len(self._km.coef_matrix[0]):
            raise ValueError("The input length must match the size of the coefficient matrix.")

        if self._gamma == 0.0:
            return x @ self._km.coef_matrix @ x.T  # type: ignore

        return x @ self._km.coef_matrix @ x.T + 2 * self._gamma * (self._km.coef_vector[None, :] @ x.T).sum(axis=0)  # type: ignore
