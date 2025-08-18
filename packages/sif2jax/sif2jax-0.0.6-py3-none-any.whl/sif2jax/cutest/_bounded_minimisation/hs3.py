import jax.numpy as jnp

from ..._problem import AbstractBoundedMinimisation


class HS3(AbstractBoundedMinimisation):
    """Problem 3 from the Hock-Schittkowski test collection.

    A 2-variable quadratic function with a bound on x₂.

    f(x) = x₂ + 10⁻⁵(x₂ - x₁)²

    Subject to: x₂ ≥ 0

    Source: problem 3 in
    W. Hock and K. Schittkowski,
    "Test examples for nonlinear programming codes",
    Lectures Notes in Economics and Mathematical Systems 187, Springer
    Verlag, Heidelberg, 1981.

    Also cited: Schuldt [56]

    Classification: QBR-T1-1
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    def objective(self, y, args):
        x1, x2 = y
        return x2 + 1e-5 * (x2 - x1) ** 2

    @property
    def y0(self):
        return jnp.array([10.0, 1.0])

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return jnp.array([0.0, 0.0])

    @property
    def expected_objective_value(self):
        return jnp.array(0.0)

    @property
    def bounds(self):
        # Only x2 has a lower bound of 0, x1 is unbounded
        lower = jnp.array([-jnp.inf, 0.0])
        upper = jnp.array([jnp.inf, jnp.inf])
        return lower, upper
