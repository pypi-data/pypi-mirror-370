import jax.numpy as jnp
import jax.scipy as jsp

from ..._problem import AbstractConstrainedMinimisation


class HS69(AbstractConstrainedMinimisation):
    """Problem 69 from the Hock-Schittkowski test collection (cost optimal inspection
    plan).

    A 4-variable nonlinear objective function with two equality constraints and bounds.

    f(x) = (a₂*n₂ - b₂*(exp(x₁) - 1) - x₃) * x₄/x₁, where a₂=0.1, b₂=1000, d₂=1, n₂=4

    Subject to:
        x₃ - 2*ℓ(-x₂) = 0
        x₄ - ℓ(-x₂ + d₂√n₂) - ℓ(-x₂ - d₂√n₂) = 0
        where ℓ(x) = ∫ᵡ₋∞ exp(-y²/2)/√2π dy

        0.0001 ≤ x₁ ≤ 100, 0 ≤ x₂ ≤ 100, 0 ≤ x₃ ≤ 2, 0 ≤ x₄ ≤ 2

    Source: problem 69 in
    W. Hock and K. Schittkowski,
    "Test examples for nonlinear programming codes",
    Lectures Notes in Economics and Mathematical Systems 187, Springer
    Verlag, Heidelberg, 1981.

    Also cited: Collani [19]

    Classification: GGR-P1-(1,2)
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    def _normal_cdf(self, x):
        """Standard normal cumulative distribution function."""
        return 0.5 * (1 + jsp.special.erf(x / jnp.sqrt(2)))

    def objective(self, y, args):
        x1, x2, x3, x4 = y
        # Problem parameters from SIF file
        a, b, n = 0.1, 1000.0, 4.0
        # Based on SIF: AN*(1/x1) - x4*(b*(exp(x1)-1) - x3)/(exp(x1) - 1 + x4)/x1
        recip_term = (a * n) / x1
        nasty_term = x4 * (b * (jnp.exp(x1) - 1) - x3) / (jnp.exp(x1) - 1 + x4) / x1
        return recip_term - nasty_term

    @property
    def y0(self):
        return jnp.array([1.0, 1.0, 1.0, 1.0])  # not feasible according to the problem

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return jnp.array([0.02937141, 1.1902534, 0.23394676, 0.7916678])

    @property
    def expected_objective_value(self):
        return jnp.array(-956.71288)

    @property
    def bounds(self):
        return (jnp.array([0.0001, 0.0, 0.0, 0.0]), jnp.array([100.0, 100.0, 2.0, 2.0]))

    def constraint(self, y):
        x1, x2, x3, x4 = y
        # Problem parameters
        d2, n2 = 1.0, 4.0
        # Equality constraints
        eq1 = x3 - 2 * self._normal_cdf(-x2)
        eq2 = (
            x4
            - self._normal_cdf(-x2 + d2 * jnp.sqrt(n2))
            - self._normal_cdf(-x2 - d2 * jnp.sqrt(n2))
        )
        equality_constraints = jnp.array([eq1, eq2])
        return equality_constraints, None
