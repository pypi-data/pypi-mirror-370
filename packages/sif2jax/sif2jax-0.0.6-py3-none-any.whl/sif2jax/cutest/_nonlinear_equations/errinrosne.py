import jax.numpy as jnp
from jax import Array

from ..._problem import AbstractNonlinearEquations


# TODO: Human review needed
# Attempts made: Basic implementation following SIF structure
# Suspected issues: PyCUTEst returns 98 constraints (49 pairs) for n=50
# Additional resources needed: Understanding of how PyCUTEst handles grouped constraints


class ERRINROSNE(AbstractNonlinearEquations):
    """
    A nonlinear function similar to the chained Rosenbrock
    problem CHNROSNB.
    This is a nonlinear equation variant of ERRINROS

    Source:
    An error in specifying problem CHNROSNB.
    SIF input: Ph. Toint, Sept 1990.
              Nick Gould (nonlinear equation version), Jan 2019

    classification NOR2-AN-V-V
    """

    n: int = 50  # Number of variables (at most 50)
    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    @property
    def alpha(self) -> Array:
        """Alpha parameters for the problem"""
        alphas = [
            1.25,
            1.40,
            2.40,
            1.40,
            1.75,
            1.20,
            2.25,
            1.20,
            1.00,
            1.10,
            1.50,
            1.60,
            1.25,
            1.25,
            1.20,
            1.20,
            1.40,
            0.50,
            0.50,
            1.25,
            1.80,
            0.75,
            1.25,
            1.40,
            1.60,
            2.00,
            1.00,
            1.60,
            1.25,
            2.75,
            1.25,
            1.25,
            1.25,
            3.00,
            1.50,
            2.00,
            1.25,
            1.40,
            1.80,
            1.50,
            2.20,
            1.40,
            1.50,
            1.25,
            2.00,
            1.50,
            1.25,
            1.40,
            0.60,
            1.50,
        ]
        # If n < 50, use only the first n alphas
        return jnp.array(alphas[: self.n])

    def residual(self, y: Array, args) -> Array:
        """Compute the residuals of the error in Rosenbrock nonlinear equations"""
        n = self.n
        alpha = self.alpha
        # There are 2*(n-1) residuals: SQ(2) to SQ(n) and B(2) to B(n)
        residuals = jnp.zeros(2 * (n - 1), dtype=y.dtype)

        # For i = 2 to n:
        # SQ(i): x(i-1) + 16*alpha(i)^2 * (-x(i)^2) = 0
        # B(i): x(i) - 1 = 0
        for i in range(2, n + 1):
            idx = 2 * (i - 2)  # Index for SQ(i) and B(i)

            # SQ(i): x(i-1) + 16*alpha(i)^2 * (-x(i)^2)
            ai = 16.0 * alpha[i - 1] ** 2
            residuals = residuals.at[idx].set(y[i - 2] + ai * (-(y[i - 1] ** 2)))

            # B(i): x(i) - 1
            residuals = residuals.at[idx + 1].set(y[i - 1] - 1.0)

        return residuals

    @property
    def y0(self) -> Array:
        """Initial guess for the optimization problem."""
        # Starting point: all variables = -1.0
        return jnp.full(self.n, -1.0, dtype=jnp.float64)

    @property
    def args(self):
        """Additional arguments for the residual function."""
        return None

    @property
    def expected_result(self) -> None:
        """Expected result of the optimization problem."""
        # Solution not specified exactly in SIF file
        return None

    @property
    def expected_objective_value(self) -> Array:
        """Expected value of the objective at the solution."""
        # For nonlinear equations with pycutest formulation, this is always zero
        return jnp.array(0.0)

    def constraint(self, y):
        """Returns the residuals as equality constraints."""
        return self.residual(y, self.args), None

    @property
    def bounds(self) -> tuple[Array, Array] | None:
        """No bounds for this problem."""
        return None
