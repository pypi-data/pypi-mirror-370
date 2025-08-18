import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


# TODO: Human review needed
# Attempts made:
# 1. Fixed c5 constraint to match SIF file formulation
# 2. Fixed c6 constraint to match SIF file formulation
# 3. Traced through SIF file element definitions
# Suspected issues:
# - Jacobian mismatch at element 39999 (difference of 8.0)
# - Complex conditional indexing with jnp.where may not differentiate correctly
# - c4 constraint uses X(N-5) which requires n > 5 check
# Resources needed:
# - Debug why Jacobian has difference of 8.0 at last column of c4
# - Verify conditional constraints are handled correctly in JAX autodiff
class LUKVLE9(AbstractConstrainedMinimisation):
    """LUKVLE9 - Modified Brown function with simplified seven-diagonal constraints.

    Problem 5.9 from Luksan and Vlcek test problems.

    The objective is a modified Brown function:
    f(x) = Σ[i=1 to n/2] [x_{2i-1}^2/1000 - (x_{2i-1} - x_{2i}) +
                          exp(20(x_{2i-1} - x_{2i}))]

    Note: Paper shows (x_{2i-1} - 3)^2/1000 but SIF file has x_{2i-1}^2/1000

    Subject to equality constraints:
    c_1(x) = 4(x_1 - x_2^2) + x_2 - x_3^2 + x_3 - x_4^2 = 0
    c_2(x) = 8x_2(x_2^2 - x_1) - 2(1 - x_2) + 4(x_2 - x_3^2) + x_1^2 + x_3 - x_4^2
             + x_4 - x_5^2 = 0
    c_3(x) = 8x_3(x_3^2 - x_2) - 2(1 - x_3) + 4(x_3 - x_4^2) + x_2^2 - x_1 + x_4 - x_5^2
             + x_1^2 + x_5 - x_6^2 = 0
    c_4(x) = 8x_{n-2}(x_{n-2}^2 - x_{n-3}) - 2(1 - x_{n-2}) + 4(x_{n-2} - x_{n+1}^2)
             + x_{n-3}^2 - x_{n-4} + x_{n-1} - x_n^2 + x_{n-4}^2 + x_n - x_{n-5} = 0
    c_5(x) = 8x_{n-1}(x_{n-1}^2 - x_{n-2}) - 2(1 - x_{n-1}) + 4(x_{n-1} - x_n^2)
             + x_{n-2}^2 - x_{n-3} + x_n + x_{k-2}^2 - x_{k-3} = 0
    c_6(x) = 8x_n(x_n^2 - x_{n-1}) - 2(1 - x_n) + x_{n-1}^2 - x_{n-2}
             + x_{n-2}^2 - x_{n-3} = 0

    Starting point: x_i = -1 for i = 1, ..., n

    Source: L. Luksan and J. Vlcek,
    "Sparse and partially separable test problems for
    unconstrained and equality constrained optimization",
    Technical Report 767, Inst. Computer Science, Academy of Sciences
    of the Czech Republic, 182 07 Prague, Czech Republic, 1999

    SIF input: Nick Gould, April 2001

    Classification: OOR2-AY-V-V
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    n: int = 10000  # Default dimension, can be overridden

    def objective(self, y, args):
        del args

        # Create indices for the sum over i = 1 to n/2
        # We need pairs (x_{2i-1}, x_{2i}) for i = 1, ..., n//2

        # Extract pairs of elements efficiently
        x_odd = y[::2]  # x_1, x_3, x_5, ... (indices 0, 2, 4, ...)
        x_even = y[1::2]  # x_2, x_4, x_6, ... (indices 1, 3, 5, ...)

        # Ensure we have matching pairs
        min_len = min(len(x_odd), len(x_even))
        x_odd = x_odd[:min_len]
        x_even = x_even[:min_len]

        # Vectorized computation of all terms
        terms = x_odd**2 / 1000 - (x_odd - x_even) + jnp.exp(20 * (x_odd - x_even))

        return jnp.sum(terms)

    @property
    def y0(self):
        # Starting point: x_i = -1 for all i
        return jnp.full(self.n, -1.0)

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        # Solution pattern based on problem structure
        return None  # Unknown exact solution

    @property
    def expected_objective_value(self):
        return None  # Unknown exact objective value

    @property
    def bounds(self):
        return None

    def constraint(self, y):
        n = len(y)
        if n < 4:
            return jnp.array([]), None

        # Build all six constraints using JAX operations
        # We'll use jnp.where to handle conditional elements

        # c_1: 4(x_1 - x_2^2) + x_2 - x_3^2 + x_3 - x_4^2 = 0
        c1 = 4 * (y[0] - y[1] ** 2) + y[1] - y[2] ** 2 + y[2] - y[3] ** 2

        # c_2: Complex constraint
        c2 = jnp.where(
            n >= 5,
            8 * y[1] * (y[1] ** 2 - y[0])
            - 2 * (1 - y[1])
            + 4 * (y[1] - y[2] ** 2)
            + y[0] ** 2
            + y[2]
            - y[3] ** 2
            + y[3]
            - y[4] ** 2,
            0.0,
        )

        # c_3: Complex constraint
        c3 = jnp.where(
            n >= 6,
            8 * y[2] * (y[2] ** 2 - y[1])
            - 2 * (1 - y[2])
            + 4 * (y[2] - y[3] ** 2)
            + y[1] ** 2
            - y[0]
            + y[3]
            - y[4] ** 2
            + y[0] ** 2
            + y[4]
            - y[5] ** 2,
            0.0,
        )

        # c_4: Complex constraint with conditional terms
        # Use jnp.where for conditional indexing
        y_n_minus_5 = jnp.where(n > 5, y[n - 5], 0.0)
        y_n_minus_5_sq = jnp.where(n > 5, y[n - 5] ** 2, 0.0)
        y_n_minus_6 = jnp.where(n > 6, y[n - 6], 0.0)

        c4 = jnp.where(
            n >= 6,
            8 * y[n - 3] * (y[n - 3] ** 2 - y[n - 4])
            - 2 * (1 - y[n - 3])
            + 4 * (y[n - 3] - y[n - 1] ** 2)
            + y[n - 4] ** 2
            - y_n_minus_5
            + y[n - 2]
            - y[n - 1] ** 2
            + y_n_minus_5_sq
            + y[n - 1]
            - y_n_minus_6,
            0.0,
        )

        # c_5: From SIF file
        # Linear: 6*X(N-1) - X(N-3) + X(N) - X(N-4) with constant 2
        # Elements: C1(5)=8*CUBEP(X(N-1),X(N-2)), C2(5)=-4*SQR(X(N)),
        #          C3(5)=1*SQR(X(N-2)), C4(5)=1*SQR(X(N-3))
        if n >= 5:
            c5 = (
                8 * y[n - 2] * (y[n - 2] ** 2 - y[n - 3])  # 8*CUBEP(X(N-1),X(N-2))
                - 2 * (1 - y[n - 2])  # Expanding 6*X(N-1) + 2 = 8*X(N-1) - 2*(1-X(N-1))
                + 4 * (y[n - 2] - y[n - 1] ** 2)  # Expanding 8*X(N-1) - 4*X(N)^2
                + y[n - 3] ** 2  # SQR(X(N-2))
                - y[n - 4]  # -X(N-3)
                + y[n - 1]  # X(N)
                + y[n - 4] ** 2  # SQR(X(N-3))
                - y[n - 5]  # -X(N-4)
            )
        else:
            c5 = (
                8 * y[n - 2] * (y[n - 2] ** 2 - y[n - 3])
                - 2 * (1 - y[n - 2])
                + 4 * (y[n - 2] - y[n - 1] ** 2)
                + y[n - 3] ** 2
                - y[n - 4]
                + y[n - 1]
                + y[n - 4] ** 2
            )

        # c_6: Final constraint
        # From SIF: 2*X(N) - X(N-3) - X(N-2)
        # Elements: C1(6)=8*CUBEP(X(N),X(N-1)), C2(6)=1*SQR(X(N-1)), C3(6)=1*SQR(X(N-2))
        c6 = (
            8 * y[n - 1] * (y[n - 1] ** 2 - y[n - 2])  # 8*CUBEP(X(N),X(N-1))
            + 2 * y[n - 1]  # 2*X(N)
            + y[n - 2] ** 2  # SQR(X(N-1))
            + y[n - 3] ** 2  # SQR(X(N-2))
            - y[n - 4]  # -X(N-3)
            - y[n - 3]  # -X(N-2)
        )

        # Stack all constraints
        # Only include constraints that are valid for the given n
        constraints = [c1]
        if n >= 5:
            constraints.append(c2)
        if n >= 6:
            constraints.extend([c3, c4])
        constraints.extend([c5, c6])

        equality_constraints = jnp.array(constraints)
        return equality_constraints, None
