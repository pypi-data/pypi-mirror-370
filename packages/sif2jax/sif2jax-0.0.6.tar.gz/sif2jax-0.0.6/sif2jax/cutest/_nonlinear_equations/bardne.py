from jax import numpy as jnp
from jaxtyping import Array, Float

from ..._problem import AbstractNonlinearEquations


class BARDNE(AbstractNonlinearEquations):
    """Bard problem in 3 variables.
    This function is a nonlinear least squares with 15 groups. Each
    group has a linear and a nonlinear element. This is a nonlinear equation
    version of problem BARD

    Source: Problem 3 in
    J.J. More', B.S. Garbow and K.E. Hillstrom,
    "Testing Unconstrained Optimization Software",
    ACM Transactions on Mathematical Software, vol. 7(1), pp. 17-41, 1981.

    See also Buckley#16.
    SIF input: Ph. Toint, Dec 1989.
    Modification as a set of nonlinear equations: Nick Gould, Oct 2015.

    classification NOR2-AN-3-15
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    def constraint(self, y) -> tuple[Float[Array, "15"], None]:
        """Returns the nonlinear equations as equality constraints."""
        x1, x2, x3 = y

        # Y data from constants
        y_data = jnp.array(
            [
                0.14,
                0.18,
                0.22,
                0.25,
                0.29,
                0.32,
                0.35,
                0.39,
                0.37,
                0.58,
                0.73,
                0.96,
                1.34,
                2.10,
                4.39,
            ]
        )

        # Vectorized computation
        i = jnp.arange(15, dtype=float)
        u = i + 1.0  # i = 1 to 15 in 1-indexed
        v = 16.0 - u

        # For i = 1 to 8: w = u
        # For i = 9 to 15: w = 16 - i = v
        w = jnp.where(i < 8, u, v)

        # Model: x1 + u / (v * x2 + w * x3)
        denominator = v * x2 + w * x3
        model = x1 + u / denominator

        residuals = model - y_data

        return residuals, None

    @property
    def y0(self) -> Float[Array, "3"]:
        """Initial guess for the optimization problem."""
        return jnp.array([1.0, 1.0, 1.0])

    @property
    def args(self):
        """Additional arguments for the residual function."""
        return None

    @property
    def expected_result(self) -> None:
        """Expected result of the optimization problem."""
        # The SIF file doesn't provide a solution
        return None

    @property
    def expected_objective_value(self) -> Float[Array, ""]:
        """Expected value of the objective at the solution."""
        # For nonlinear equations with pycutest formulation, this is always zero
        return jnp.array(0.0)

    @property
    def bounds(self) -> tuple[Array, Array] | None:
        """No bounds for this problem."""
        return None
