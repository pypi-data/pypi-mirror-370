import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


class HS93(AbstractConstrainedMinimisation):
    """Problem 93 from the Hock-Schittkowski test collection.

    A 6-variable nonlinear objective function with two inequality constraints.

    f(x) = 0.0204*x₁*x₄*(x₁ + x₂ + x₃) + 0.0187*x₂*x₃*(x₁ + 1.57*x₂ + x₄)
           + 0.0607*x₁*x₄*x₅²*(x₁ + x₂ + x₃) + 0.0437*x₂*x₃*x₆²*(x₁ + 1.57*x₂ + x₄)

    Subject to:
        0.001*x₁*x₂*x₃*x₄*x₅*x₆ ≥ 2.07
        0.00062*x₁*x₄*x₅²*(x₁ + x₂ + x₃) + 0.00058*x₂*x₃*x₆²*(x₁ + 1.57*x₂ + x₄) ≤ 1
        0 ≤ xᵢ, i=1,...,6

    Source: problem 93 in
    W. Hock and K. Schittkowski,
    "Test examples for nonlinear programming codes",
    Lectures Notes in Economics and Mathematical Systems 187, Springer
    Verlag, Heidelberg, 1981.

    Classification: PGR-P1-5
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    def objective(self, y, args):
        x1, x2, x3, x4, x5, x6 = y
        # Precompute common terms
        sum_123 = x1 + x2 + x3
        sum_124 = x1 + 1.57 * x2 + x4
        x1x4 = x1 * x4
        x2x3 = x2 * x3
        x5_sq = x5 * x5
        x6_sq = x6 * x6

        return (
            0.0204 * x1x4 * sum_123
            + 0.0187 * x2x3 * sum_124
            + 0.0607 * x1x4 * x5_sq * sum_123
            + 0.0437 * x2x3 * x6_sq * sum_124
        )

    @property
    def y0(self):
        return jnp.array([5.54, 4.4, 12.02, 11.82, 0.702, 0.852])

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return jnp.array([5.332666, 4.656744, 10.43299, 12.08230, 0.7526074, 0.8420251])

    @property
    def expected_objective_value(self):
        return jnp.array(135.075961)

    @property
    def bounds(self):
        # All variables have lower bound 0, no upper bound
        lower = jnp.zeros(6)
        upper = jnp.full(6, jnp.inf)
        return lower, upper

    def constraint(self, y):
        x1, x2, x3, x4, x5, x6 = y
        # Precompute common terms
        sum_123 = x1 + x2 + x3
        sum_124 = x1 + 1.57 * x2 + x4
        x1x4 = x1 * x4
        x2x3 = x2 * x3
        x5_sq = x5 * x5
        x6_sq = x6 * x6

        # Inequality constraints from SIF file
        # C1 is a 'G' type: 0.001 * x1*x2*x3*x4*x5*x6 >= 2.07
        # pycutest reports the raw constraint value
        ineq1 = 0.001 * x1x4 * x2x3 * x5 * x6 - 2.07

        # C2 is an 'L' type constraint
        # 0.00062*OE3 + 0.00058*OE4 <= 1
        # where OE3 = x1*x4*x5²*(x1 + x2 + x3)
        # and OE4 = x2*x3*x6²*(x1 + 1.57*x2 + x4)
        oe3 = x1x4 * x5_sq * sum_123
        oe4 = x2x3 * x6_sq * sum_124
        ineq2 = 0.00062 * oe3 + 0.00058 * oe4 - 1.0

        inequality_constraints = jnp.array([ineq1, ineq2])
        return None, inequality_constraints
