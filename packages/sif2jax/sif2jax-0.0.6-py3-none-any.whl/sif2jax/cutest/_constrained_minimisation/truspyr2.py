import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


class TRUSPYR2(AbstractConstrainedMinimisation):
    """TRUSPYR2 problem - 8-bar truss structure optimization with stress constraints.

    This is a structural optimization problem. The problem is to minimize the weight
    of a given 8-bar truss structure formed as a pyramid for a given external load.
    There are upper bounds on the normal stresses in the bars and lower bounds
    on the cross-sectional areas of the bars.

    Source: K. Svanberg, "Local and global optima",
    Proceedings of the NATO/DFG ASI on Optimization of large structural systems,
    G. I. N. Rozvany, ed., Kluwer, 1993, pp. 579-588.

    SIF input: A. Forsgren, Royal Institute of Technology, December 1993.

    Classification: LQR2-MN-11-11
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    @property
    def n(self):
        """Number of variables (8 cross-sectional areas + 3 displacements)."""
        return 11

    def _get_problem_data(self):
        """Get the problem-specific data for the truss structure."""
        # Constants
        sqrt17 = jnp.sqrt(17.0)
        sqrt18 = jnp.sqrt(18.0)

        # External loads
        p = jnp.array([40.0, 20.0, 200.0])

        # Truss lengths
        l = jnp.array(
            [
                sqrt17 / 8.0,
                sqrt17 / 8.0,
                sqrt17 / 8.0,
                sqrt17 / 8.0,
                sqrt18 / 8.0,
                sqrt18 / 8.0,
                sqrt18 / 8.0,
                sqrt18 / 8.0,
            ]
        )

        # Modulus of elasticity
        e = 21.0

        # Direction vectors for bars
        r = jnp.array(
            [
                [0.250, 0.250, 0.375],
                [0.250, -0.250, 0.375],
                [-0.250, -0.250, 0.375],
                [-0.250, 0.250, 0.375],
                [0.375, 0.000, 0.375],
                [0.000, -0.375, 0.375],
                [-0.375, 0.000, 0.375],
                [0.000, 0.375, 0.375],
            ]
        )

        # Bar weights
        w = l * 0.78

        # Pre-compute coefficients
        l2 = l**2
        l3 = l**3
        gamma = e / l3
        dl2 = l2 / e
        strup = dl2 * 10.0  # Upper bounds on normal stresses

        # RR coefficients for equilibrium constraints
        def compute_rr():
            rr = jnp.zeros((3, 8, 3))
            for i in range(3):
                for j in range(8):
                    rg = gamma[j] * r[j, i]
                    for k in range(3):
                        rr = rr.at[i, j, k].set(rg * r[j, k])
            return rr

        rr = compute_rr()

        return p, w, r, rr, strup

    def objective(self, y, args):
        """Compute the truss weight objective."""
        del args
        # Extract cross-sectional areas (first 8 variables)
        xarea = y[:8]

        # Get problem data
        p, w, r, rr, strup = self._get_problem_data()

        # Objective is sum of weights * areas
        return jnp.dot(w, xarea)

    def constraint(self, y):
        """Compute the constraints."""
        # Extract variables
        xarea = y[:8]  # Cross-sectional areas
        displ = y[8:]  # Displacements

        # Get problem data
        p, w, r, rr, strup = self._get_problem_data()

        # Equilibrium constraints (equality)
        # EQUIL(k) = sum_i sum_j RR(i,j,k) * DISPL(i) * XAREA(j) - P(k) = 0
        def compute_equil(k):
            total = 0.0
            for i in range(3):
                for j in range(8):
                    total += rr[i, j, k] * displ[i] * xarea[j]
            return total - p[k]

        equil = jnp.array([compute_equil(k) for k in range(3)])

        # Stress constraints (inequality)
        # sum_i R(i,j) * DISPL(i) <= STRUP(j) for each bar j
        # =>  sum_i R(i,j) * DISPL(i) - STRUP(j) <= 0
        def compute_stress(j):
            return jnp.dot(r[j], displ) - strup[j]

        stress_constraints = jnp.array([compute_stress(j) for j in range(8)])

        return equil, stress_constraints

    @property
    def y0(self):
        """Initial guess - all zeros as in pycutest."""
        return jnp.zeros(11)

    @property
    def args(self):
        """Additional arguments (none for this problem)."""
        return None

    @property
    def bounds(self):
        """Bounds on variables."""
        # Cross-sectional areas have lower bound of 1.0, displacements unbounded
        lower = jnp.array(
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -jnp.inf, -jnp.inf, -jnp.inf]
        )
        upper = jnp.full(11, jnp.inf)
        return lower, upper

    @property
    def expected_result(self):
        """Expected optimal solution."""
        return None  # Not provided in SIF

    @property
    def expected_objective_value(self):
        """Expected optimal objective value."""
        return jnp.array(11.2287408808)
