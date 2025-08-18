import jax.numpy as jnp

from ..._problem import AbstractUnconstrainedMinimisation


# TODO: This implementation requires human review and verification against
# another CUTEst interface
class CUBE(AbstractUnconstrainedMinimisation):
    """A cubic variant of the Rosenbrock test function.

    This problem is a modification of the Rosenbrock function, using
    a cubic term instead of a quadratic. The objective function includes
    terms with (x_i - x_{i-1}^3)^2.

    Source: problem 5 (p. 89) in
    A.R. Buckley,
    "Test functions for unconstrained minimization",
    TR 1989CS-3, Mathematics, statistics and computing centre,
    Dalhousie University, Halifax (CDN), 1989.

    SIF input: Ph. Toint, Dec 1989.

    Classification: SUR2-AN-2-0
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    n: int = 2  # Number of variables

    def objective(self, y, args):
        del args

        # First term: (x_1 - 1)^2
        term1 = (y[0] - 1.0) ** 2

        # Second term: 100 * (x_2 - x_1^3)^2
        # Note: SIF shows scale 0.01 but pycutest uses 100.0
        term2 = 100.0 * (y[1] - y[0] ** 3) ** 2

        return term1 + term2

    @property
    def y0(self):
        # Initial values from SIF file
        return jnp.array([-1.2, 1.0])

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        # Based on the optimal objective value of 0.0,
        # the solution must satisfy:
        # x_1 = 1
        # x_2 = x_1^3 = 1
        return jnp.array([1.0, 1.0])

    @property
    def expected_objective_value(self):
        # According to the SIF file, line 91
        return jnp.array(0.0)
