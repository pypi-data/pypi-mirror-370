import jax
import jax.numpy as jnp

from ..._misc import inexact_asarray
from ..._problem import AbstractUnconstrainedMinimisation


# TODO: This implementation requires human review and verification against
# another CUTEst interface
class EXP2(AbstractUnconstrainedMinimisation):
    """The EXP2 function.

    SCIPY global optimization benchmark example Exp2
    Fit: y = e^{-i/10 x_1} - 5e^{-i/10 x_2} - e^{-i/10} + 5e^{-i} + e

    Source: Problem from the SCIPY benchmark set
    https://github.com/scipy/scipy/tree/master/benchmarks/benchmarks/go_benchmark_functions

    SIF input: Nick Gould

    Classification: SUR2-MN-2-0
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    n: int = 2  # Problem has 2 variables

    def objective(self, y, args):
        del args
        x1, x2 = y

        # Define target values for each i from 0 to 9
        # target_i = exp(-i/10) - 5 * exp(-i) (from SIF constants section)
        def compute_target(i):
            return jnp.exp(-i / 10) - 5 * jnp.exp(-i)

        # Define a function to compute a single residual given an index
        def compute_residual(i):
            predicted = jnp.exp(-i / 10 * x1) - 5 * jnp.exp(-i / 10 * x2)
            target = compute_target(i)
            return predicted - target

        # Vectorize the residual computation across all indices
        indices = jnp.arange(10.0)
        residuals = jax.vmap(compute_residual)(indices)

        # Sum of squared residuals
        return jnp.sum(jnp.square(residuals))

    @property
    def y0(self):
        # Initial values from SIF file
        return inexact_asarray(jnp.array([1.0, 5.0]))

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return None

    @property
    def expected_objective_value(self):
        return None
