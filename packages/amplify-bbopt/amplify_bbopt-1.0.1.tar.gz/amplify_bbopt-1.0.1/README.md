# Amplify-BBOpt

Amplify-BBOpt is a powerful Python package by [Fixstars Amplify](https://amplify.fixstars.com/en), designed to streamline the implementation and execution of black-box optimization algorithms.

*   Documentation:  
 <https://amplify.fixstars.com/docs/amplify-bbopt/v1/>
*   Contributing (bug reports, improvements):  
 <https://amplify.fixstars.com/en/contact>

## Features

Amplify-BBOpt is built upon the powerful [Amplify SDK](https://amplify.fixstars.com/en/docs/amplify/), bridging the gap between black-box optimization and specialized hardware. It uniquely offers annealing-based optimization methods, including Factorization Machine Quantum Annealing (FMQA) and Kernel-QA, which are designed to run on quantum annealers and various Ising machine backends.

*   **Intuitive API**: A clean, straightforward interface enables rapid experimentation and allows users to easily swap between different optimization methods.
*   **High-Dimensional Scalability**: Engineered to effectively solve complex optimization problems, even those with a high-dimensional parameter space.
*   **Built-in Constraint Handling**: Natively supports both unconstrained and constrained optimization problems, providing a versatile framework for real-world applications.

## Basic Usage

```py
from amplify import FixstarsClient

from amplify_bbopt import FMTrainer, Optimizer, RealVariable, blackbox


# Define a test function
# (This represents a simulation or experiment)
def spherical_func(a: float, b: float) -> float:
    return (a + 1) ** 2 + (b - 1) ** 2


# Make a black-box function and define relevant decision variables
@blackbox
def bb_func(
    a: float = RealVariable((-5, 5)),  # type: ignore
    b: float = RealVariable((-5, 5)),  # type: ignore
) -> float:
    return spherical_func(a, b)


# Prepare solver client
client = FixstarsClient()
client.parameters.timeout = 1000

# Execute optimization
opt = Optimizer(bb_func, FMTrainer(), client)
opt.add_random_training_data(num_data=5)
opt.optimize(num_iterations=10)

# View results
print(opt.best.objective)
print(opt.best.values)
```

## For Developers

Amplify-BBOpt requires Python 3.10 or later.
Also, it depends on `amplify` and `torch` packages, which can be installed via pip.
After installing the dependencies, you can install Amplify-BBOpt in editable mode.

```bash
$ pip install -e amplify-bbopt
```

Instead, we recommend using `uv` for managing the development environment and running tests.

```bash
$ uv sync
```

Testing:

```bash
$ uv run pytest
```
