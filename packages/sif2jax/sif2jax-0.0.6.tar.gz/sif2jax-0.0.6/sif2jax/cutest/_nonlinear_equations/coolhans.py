import jax.numpy as jnp

from ..._problem import AbstractNonlinearEquations


class COOLHANS(AbstractNonlinearEquations):
    """Cooley-Hansen economy with loglinear approximation - nonlinear equations problem.

    A problem arising from the analysis of a Cooley-Hansen economy with
    loglinear approximation. The problem is to solve the matrix equation

                    A * X * X + B * X + C = 0

    where A, B and C are known N times N matrices and X an unknown matrix
    of matching dimension. The instance considered here has N = 3.

    Source:
    S. Ceria, private communication, 1995.

    SIF input: Ph. Toint, Feb 1995.

    Classification: NQR2-RN-9-9
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    # Matrix dimension
    N = 3

    # Matrix A
    A = jnp.array([[0.0, 0.0, 0.0], [0.13725e-6, 937.62, -42.207], [0.0, 0.0, 0.0]])

    # Matrix B
    B = jnp.array(
        [
            [0.0060893, -44.292, 2.0011],
            [0.13880e-6, -1886.0, 42.362],
            [-0.13877e-6, 42.362, -2.0705],
        ]
    )

    # Matrix C
    C = jnp.array([[0.0, 44.792, 0.0], [0.0, 948.21, 0.0], [0.0, -42.684, 0.0]])

    @property
    def n(self):
        """Number of variables."""
        return self.N * self.N  # 9 variables for 3x3 matrix

    def num_residuals(self):
        """Number of residuals."""
        return self.N * self.N  # 9 residuals for 3x3 matrix equation

    def residual(self, y, args):
        """Compute the residuals of the matrix equation.

        The residuals are from the matrix equation:
        R = A*X*X + B*X + C = 0
        """
        del args

        # Reshape flat vector to matrix
        X = y.reshape((self.N, self.N))

        # Compute residual: A*X*X + B*X + C
        AXX = jnp.matmul(self.A, jnp.matmul(X, X))
        BX = jnp.matmul(self.B, X)
        residual = AXX + BX + self.C

        # Flatten residual to vector form
        return residual.flatten()

    @property
    def y0(self):
        """Initial guess."""
        # Zero initial guess
        return jnp.zeros(self.n)

    @property
    def args(self):
        """No additional arguments."""
        return None

    @property
    def expected_result(self):
        """Expected optimal solution."""
        # Not provided in SIF file
        return None

    @property
    def expected_objective_value(self):
        """Expected optimal objective value."""
        # Should be 0.0 at solution
        return jnp.array(0.0)

    def constraint(self, y):
        """Returns the residuals as equality constraints."""
        return self.residual(y, self.args), None

    @property
    def bounds(self) -> tuple[jnp.ndarray, jnp.ndarray] | None:
        """No bounds for this problem."""
        return None
