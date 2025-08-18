import jax.numpy as jnp

from ..._problem import AbstractUnconstrainedMinimisation


# TODO: Needs verification against another CUTEst interface
class COSINE(AbstractUnconstrainedMinimisation):
    """The COSINE function.

    A function with nontrivial groups and repetitious elements.

    Source: N. Gould, private communication.

    SIF input: N. Gould, Jan 1996

    Classification: OUR2-AN-V-0
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    n: int = 10000  # Other suggested dimensions 10, 100, 10000

    def objective(self, y, args):
        del args
        return jnp.sum(jnp.cos(-0.5 * y[1:] + y[:-1] ** 2))

    @property
    def y0(self):
        # Initial guess - specified as 1.0 for all variables
        return jnp.ones(self.n)

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return None

    @property
    def expected_objective_value(self):
        # According to line 83 in the SIF file, the objective is bounded
        # below by -(n-1), but no exact solution value is given
        return None
