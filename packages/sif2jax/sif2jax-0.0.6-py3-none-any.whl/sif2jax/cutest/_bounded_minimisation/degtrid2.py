import jax.numpy as jnp
from jax import Array

from ..._misc import inexact_asarray
from ..._problem import AbstractBoundedMinimisation


class DEGTRID2(AbstractBoundedMinimisation):
    """
    A degenerate bound constrained convex quadratic program with a tri-diagonal Hessian.

    The problem has the form:
    minimize    0.5 * x^T H x - c^T x
    subject to  x >= lower_bounds

    where H is a tridiagonal matrix with 1 on the diagonal and 0.5 on the
    off-diagonals, c is [-0.5, -1.5, -2.0, ..., -2.0, -1.5], and
    lower bounds are 0.0 for x_0 and 1.0 for all other variables.

    SIF input: Nick Gould, August 2011

    classification QBR2-AN-V-0
    """

    _n: int = 100001  # Number of variables (N+1 where N=100000)
    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    @property
    def n(self) -> int:
        """Number of variables is N+1"""
        return self._n

    def objective(self, y: Array, args) -> Array:
        """Compute the quadratic objective function"""
        n = self._n

        # Linear term coefficients
        c = jnp.ones(n) * (-2.0)
        c = c.at[0].set(-0.5)
        c = c.at[1].set(-1.5)
        c = c.at[-1].set(-1.5)

        # Quadratic term: 0.5 * x^T H x
        # H is tridiagonal with 1 on diagonal and 0.5 on off-diagonals

        # Diagonal contribution: sum(x_i^2)
        quad_diag = jnp.sum(y**2)

        # Off-diagonal contribution: 2 * 0.5 * sum(x_i * x_{i-1}) = sum(x_i * x_{i-1})
        quad_offdiag = jnp.sum(y[1:] * y[:-1])

        # Total quadratic term
        quad_term = 0.5 * (quad_diag + quad_offdiag)

        # Linear term
        linear_term = jnp.dot(c, y)

        return quad_term + linear_term

    @property
    def bounds(self):
        """Lower bounds: 0.0 for x_0, 1.0 for all others"""
        n = self._n
        lbs = jnp.ones(n)
        lbs = lbs.at[0].set(0.0)
        ubs = jnp.full(n, jnp.inf)
        return lbs, ubs

    @property
    def y0(self) -> Array:
        """Initial point: all components set to 2.0"""
        return inexact_asarray(jnp.full(self._n, 2.0))

    @property
    def args(self):
        return None

    @property
    def expected_result(self) -> None:
        """Solution not provided in SIF file"""
        return None

    @property
    def expected_objective_value(self) -> None:
        """Optimal value not provided in SIF file"""
        return None
