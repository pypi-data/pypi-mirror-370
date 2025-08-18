import jax.numpy as jnp
from jax import Array

from ..._problem import AbstractNonlinearEquations


class PALMER2ANE(AbstractNonlinearEquations):
    """
    A nonlinear least squares problem with bounds
    arising from chemical kinetics.

    model: H-N=C=O TZVP + MP2
    fitting Y to A2 X**2 + A4 X**4 + A6 X**6
                 + B / ( C + X**2 ), B, C nonnegative.

    Source:
    M. Palmer, Edinburgh, private communication.

    SIF input: Nick Gould, 1990.
    Bound-constrained nonlinear equations version: Nick Gould, June 2019.

    classification NOR2-RN-6-23
    """

    n: int = 6
    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    # No custom __init__ needed - using Equinox module defaults

    def num_residuals(self) -> int:
        """Number of residuals equals number of data points."""
        return 23

    def starting_point(self) -> Array:
        """Return the starting point for the problem."""
        return jnp.ones(self.n, dtype=jnp.float64)

    def _get_data(self):
        """Get the data points for the problem."""
        # X values (radians)
        x = jnp.array(
            [
                -1.745329,
                -1.570796,
                -1.396263,
                -1.221730,
                -1.047198,
                -0.937187,
                -0.872665,
                -0.698132,
                -0.523599,
                -0.349066,
                -0.174533,
                0.0,
                0.174533,
                0.349066,
                0.523599,
                0.698132,
                0.872665,
                0.937187,
                1.047198,
                1.221730,
                1.396263,
                1.570796,
                1.745329,
            ],
            dtype=jnp.float64,
        )

        # Y values (KJmol-1)
        y = jnp.array(
            [
                72.676767,
                40.149455,
                18.8548,
                6.4762,
                0.8596,
                0.00000,
                0.2730,
                3.2043,
                8.1080,
                13.4291,
                17.7149,
                19.4529,
                17.7149,
                13.4291,
                8.1080,
                3.2053,
                0.2730,
                0.00000,
                0.8596,
                6.4762,
                18.8548,
                40.149455,
                72.676767,
            ],
            dtype=jnp.float64,
        )

        return x, y

    def residual(self, v: Array, args) -> Array:
        """Compute the residual vector."""
        # Variables: A0, A2, A4, A6, B, C
        a0, a2, a4, a6, b, c = v

        x, y = self._get_data()

        # Compute powers of x
        x_sqr = x * x
        x_quart = x_sqr * x_sqr
        x_sext = x_quart * x_sqr

        # Model: A0 + A2*X^2 + A4*X^4 + A6*X^6 + B/(C + X^2)
        model = a0 + a2 * x_sqr + a4 * x_quart + a6 * x_sext + b / (c + x_sqr)

        # Residuals
        residuals = model - y

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
    def expected_result(self):
        """Expected result of the optimization problem."""
        return None

    @property
    def expected_objective_value(self):
        """Expected value of the objective at the solution."""
        return jnp.array(0.0)

    def constraint(self, y):
        """Returns the residuals as equality constraints."""
        return self.residual(y, self.args), None

    @property
    def bounds(self) -> tuple[Array, Array] | None:
        """Bounds for variables.

        A0, A2, A4, A6 are free
        B >= 0.00001
        C >= 0.00001
        """
        lower = jnp.array(
            [-jnp.inf, -jnp.inf, -jnp.inf, -jnp.inf, 0.00001, 0.00001],
            dtype=jnp.float64,
        )
        upper = jnp.full(self.n, jnp.inf, dtype=jnp.float64)
        return lower, upper
