import jax
import jax.numpy as jnp
from jax import Array

from ..._problem import AbstractNonlinearEquations


class BRYBNDNE(AbstractNonlinearEquations):
    """
    Broyden banded system of nonlinear equations.
    This is a nonlinear equation variant of BRYBND

    Source: problem 31 in
    J.J. More', B.S. Garbow and K.E. Hillstrom,
    "Testing Unconstrained Optimization Software",
    ACM Transactions on Mathematical Software, vol. 7(1), pp. 17-41, 1981.

    See also Buckley#73 (p. 41) and Toint#18

    SIF input: Ph. Toint, Dec 1989.
              Nick Gould (nonlinear equation version), Jan 2019

    classification NOR2-AN-V-V

    TODO: Human review needed - constraint values don't match pycutest
    Same systematic differences as BROYDNBD. Implementation follows SIF file.
    """

    n: int = 5000
    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    # Problem parameters
    kappa1: float = 2.0
    kappa2: float = 5.0
    kappa3: float = 1.0
    lb: int = 5  # Lower bandwidth
    ub: int = 1  # Upper bandwidth

    def starting_point(self) -> Array:
        return jnp.ones(self.n, dtype=jnp.float64)

    def num_residuals(self) -> int:
        return self.n

    def residual(self, y: Array, args) -> Array:
        """Compute the residuals of the Broyden banded nonlinear equations"""
        n = self.n
        lb = self.lb
        ub = self.ub
        kappa1 = self.kappa1
        kappa2 = self.kappa2
        kappa3 = self.kappa3

        def compute_residual_i(i):
            # Linear part: kappa1 * y[i]
            res_i = kappa1 * y[i]

            # Nonlinear part: kappa2 * (y[i]^3 or y[i]^2 depending on position)
            # The pattern from the SIF file shows:
            # - For i < lb: use Q(i) = CB (cubic) for y[i]
            # - For lb <= i < n-ub: use E(i) = SQ (square) for y[i]
            # - For i >= n-ub: use Q(i) = CB (cubic) for y[i]
            use_cubic = jnp.logical_or(i < lb, i >= n - ub)
            nonlinear_part = jnp.where(
                use_cubic, kappa2 * y[i] ** 3, kappa2 * y[i] ** 2
            )
            res_i += nonlinear_part

            # Add contributions from other variables based on SIF GROUP USES
            # Lower band contributions
            j_offsets_lower = jnp.arange(-lb, 0)  # [-lb, -lb+1, ..., -1]
            j_lower_indices = i + j_offsets_lower
            # Mask for valid indices (j >= 0 and j < i)
            lower_mask = jnp.logical_and(j_lower_indices >= 0, j_lower_indices < i)

            # Determine which element type to use for lower band
            # Upper left corner (i < lb): use E(j) = SQ for all j < i
            # Middle part (lb <= i < n-ub): use Q(j) = CB for j in [i-lb, i-1]
            # Lower right (i >= n-ub): use E(j) = SQ for j in [i-lb, i-1]
            j_lower_safe = jnp.clip(j_lower_indices, 0, n - 1)
            y_lower = y[j_lower_safe]

            # For upper left and lower right corners, use SQ (square)
            # For middle part, use CB (cubic)
            use_square_lower = jnp.logical_or(i < lb, i >= n - ub)
            lower_contrib = jnp.where(
                use_square_lower, kappa3 * y_lower**2, kappa3 * y_lower**3
            )
            # Apply mask and sum
            res_i -= jnp.sum(lower_contrib * lower_mask.astype(y.dtype))

            # Upper band contributions
            j_offsets_upper = jnp.arange(1, ub + 1)  # [1, 2, ..., ub]
            j_upper_indices = i + j_offsets_upper
            # Mask for valid indices (j < n)
            upper_mask = j_upper_indices < n

            # For all regions, upper band uses E(j) = SQ
            j_upper_safe = jnp.clip(j_upper_indices, 0, n - 1)
            y_upper = y[j_upper_safe]
            upper_contrib = kappa3 * y_upper**2
            # Apply mask and sum
            res_i -= jnp.sum(upper_contrib * upper_mask.astype(y.dtype))

            return res_i

        # Vectorize over all indices
        indices = jnp.arange(n)
        residuals = jax.vmap(compute_residual_i)(indices)

        return residuals

    @property
    def y0(self) -> Array:
        """Initial guess for the optimization problem."""
        return self.starting_point()

    @property
    def args(self):
        """Additional arguments for the residual function."""
        return None

    @property
    def expected_result(self) -> None:
        """Expected result of the optimization problem."""
        # The SIF file mentions solution value 0.0 but not the exact solution vector
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
