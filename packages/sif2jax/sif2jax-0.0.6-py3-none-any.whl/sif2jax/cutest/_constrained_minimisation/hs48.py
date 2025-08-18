import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


class HS48(AbstractConstrainedMinimisation):
    """Problem 48 from the Hock-Schittkowski test collection.

    A 5-variable quadratic objective function with two linear equality constraints.

    f(x) = (x₁ - 1)² + (x₂ - x₃)² + (x₄ - x₅)²

    Subject to:
        x₁ + x₂ + x₃ + x₄ + x₅ - 5 = 0
        x₃ - 2(x₄ + x₅) + 3 = 0

    Source: problem 48 in
    W. Hock and K. Schittkowski,
    "Test examples for nonlinear programming codes",
    Lectures Notes in Economics and Mathematical Systems 187, Springer
    Verlag, Heidelberg, 1981.

    Also cited: Huang, Aggerwal [34], Miele e.al. [43]

    Classification: QLR-T1-5
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    def objective(self, y, args):
        x1, x2, x3, x4, x5 = y
        return (x1 - 1) ** 2 + (x2 - x3) ** 2 + (x4 - x5) ** 2

    @property
    def y0(self):
        return jnp.array([3.0, 5.0, -3.0, 2.0, -2.0])

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return jnp.array([1.0, 1.0, 1.0, 1.0, 1.0])

    @property
    def expected_objective_value(self):
        return jnp.array(0.0)

    @property
    def bounds(self):
        return None

    def constraint(self, y):
        x1, x2, x3, x4, x5 = y
        # Equality constraints
        eq1 = x1 + x2 + x3 + x4 + x5 - 5
        eq2 = x3 - 2 * (x4 + x5) + 3
        equality_constraints = jnp.array([eq1, eq2])
        return equality_constraints, None
