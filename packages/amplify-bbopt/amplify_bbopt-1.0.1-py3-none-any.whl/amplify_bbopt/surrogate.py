from typing import Generic, TypeVar

import amplify

from .trainer import Dataset, Trainer

_T = TypeVar("_T", bound=Trainer)


class SurrogateModel(Generic[_T]):
    """A generic surrogate model class for approximating expensive objective functions.

    Type Parameters:
        _T: A type variable that must be a subclass of `Trainer`. This allows the surrogate model to use any specific trainer implementation for training and evaluation.
    """  # noqa: E501

    def __init__(
        self,
        surrogate_variables: amplify.PolyArray,
        trainer: _T,
    ) -> None:
        """Initializes the surrogate model class.

        Args:
            surrogate_variables (amplify.PolyArray): The Amplify SDK variables for the model.
            trainer (_T): The trainer to use for the model.
        """
        super().__init__()
        self._surrogate_variables: amplify.PolyArray = surrogate_variables
        self._trainer: _T = trainer

    @property
    def variables(self) -> amplify.PolyArray:
        """Returns the variables used in the model."""
        return self._surrogate_variables

    @property
    def trainer(self) -> _T:
        """Returns the trainer used in the model."""
        return self._trainer

    def train(self, training_data: Dataset) -> None:
        """Trains the surrogate model on the given dataset.

        Args:
            training_data (Dataset): The dataset to train on.
        """
        self._trainer.train(training_data)

    def to_poly(self) -> amplify.Poly:
        """Converts the surrogate model to an Amplify Poly object.

        Returns:
            amplify.Poly: The Amplify Poly representation of the surrogate model.
        """
        return self._trainer.to_poly(self._surrogate_variables)
