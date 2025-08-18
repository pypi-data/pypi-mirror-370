import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


class BT9(AbstractConstrainedMinimisation):
    """BT9 - Boggs-Tolle test problem 9.

    n = 4, m = 2.
    f(x) = -x₁.
    g₁(x) = x₂ - x₁³ - x₃².
    g₂(x) = x₁² - x₂ - x₄².

    Start 1: xᵢ = 2, i = 1, ..., 4.
    Start 2: xᵢ = 20, i = 1, ..., 4.
    Start 3: xᵢ = 50, i = 1, ..., 4.
    Solution: x* = (1.0, 1.0, 0.0, 0.0).

    Source: Boggs, P.T. and Tolle, J.W.,
    "A strategy for global convergence in a sequential
    quadratic programming algorithm",
    SIAM J. Numer. Anal. 26(3), pp. 600-623, 1989.

    Note: The problem as stated in the paper seems to contain a typo.
    In order to make the problem bounded below and the second constraint
    feasible at the proposed solution, the sign of x₂ in the second constraint
    has been changed from + to -.

    Classification: LOR2-AN-4-2
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0, 1, 2})

    def objective(self, y, args):
        del args
        x1, x2, x3, x4 = y
        return -x1

    @property
    def y0(self):
        if self.y0_iD == 0:
            return jnp.array([2.0, 2.0, 2.0, 2.0])
        elif self.y0_iD == 1:
            return jnp.array([20.0, 20.0, 20.0, 20.0])
        elif self.y0_iD == 2:
            return jnp.array([50.0, 50.0, 50.0, 50.0])

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return jnp.array([1.0, 1.0, 0.0, 0.0])

    @property
    def expected_objective_value(self):
        return jnp.array(-1.0)

    @property
    def bounds(self):
        return None

    def constraint(self, y):
        x1, x2, x3, x4 = y
        # Equality constraints
        g1 = x2 - x1**3 - x3**2
        g2 = x1**2 - x2 - x4**2  # Note: sign of x2 changed from + to - per SIF file
        equality_constraints = jnp.array([g1, g2])
        return equality_constraints, None
