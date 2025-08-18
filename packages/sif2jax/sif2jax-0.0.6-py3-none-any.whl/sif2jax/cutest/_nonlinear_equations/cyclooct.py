import jax.numpy as jnp
from jax import Array

from ..._misc import inexact_asarray
from ..._problem import AbstractNonlinearEquations


class CYCLOOCT(AbstractNonlinearEquations):
    """
    The cyclooctane molecule configuration problem.

    The cyclooctane molecule is comprised of eight carbon atoms aligned
    in an equally spaced ring. When they take a position of minimum
    potential energy so that next-neighbours are equally spaced.

    Given positions v_1, ..., v_p in R^3 (with p = 8 for cyclooctane),
    and given a spacing c^2 we have that

       ||v_i - v_i+1,mod p||^2 = c^2 for i = 1,..,p, and
       ||v_i - v_i+2,mod p||^2 = 2p/(p-2) c^2

    where (arbitrarily) we have v_1 = 0 and component 1 of v_2 = 0

    Source:
    an extension of the cyclooctane molecule configuration space as
    described in (for example)

     E. Coutsias, S. Martin, A. Thompson & J. Watson
     "Topology of cyclooctane energy landscape"
     J. Chem. Phys. 132-234115 (2010)

    SIF input: Nick Gould, Feb 2020.

    classification  NQR2-MN-V-V
    """

    p: int = 10000  # Number of molecules
    c: float = 1.0  # Radius
    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    @property
    def n(self) -> int:
        """Number of variables is 3*P"""
        return 3 * self.p

    def constraint(self, y: Array):
        """Compute the constraint equations for cyclooctane configuration"""
        p = self.p
        c2 = self.c**2
        sc2 = (2.0 * p / (p - 2)) * c2

        # Reshape into (p, 3) for easier manipulation - each row is a position vector
        positions = y.reshape(p, 3)

        # Note: Fixed variables (X1, Y1, Z1 = 0 and X2 = 0) are handled through bounds,
        # not by modifying the positions here

        # Nearest neighbor constraints: ||v_i - v_{i+1}||^2 = c^2
        next_indices = (jnp.arange(p) + 1) % p
        diff_next = positions - positions[next_indices]
        dist_sq_next = jnp.sum(diff_next**2, axis=1)
        constraints_a = dist_sq_next - c2

        # Next-next neighbor constraints: ||v_i - v_{i+2}||^2 = 2p/(p-2)*c^2
        next2_indices = (jnp.arange(p) + 2) % p
        diff_next2 = positions - positions[next2_indices]
        dist_sq_next2 = jnp.sum(diff_next2**2, axis=1)
        constraints_b = dist_sq_next2 - sc2

        # Interleave constraints as A(1), B(1), A(2), B(2), ..., A(P), B(P)
        # This matches the SIF file constraint ordering
        eq_constraints = jnp.stack([constraints_a, constraints_b], axis=1).flatten()

        # No inequality constraints for this problem
        return eq_constraints, None

    @property
    def y0(self) -> Array:
        """Initial point: i/P for molecule i"""
        p = self.p
        values = jnp.arange(1, p + 1) / p

        # Create initial positions
        x_coords = values
        y_coords = values
        z_coords = values

        # Stack into single array
        initial = jnp.stack([x_coords, y_coords, z_coords], axis=1).flatten()

        # Note: Fixed variables (X1, Y1, Z1 = 0 and X2 = 0) are handled through bounds,
        # not by modifying the initial point, to match pycutest behavior

        return inexact_asarray(initial)

    @property
    def args(self):
        return None

    @property
    def expected_result(self) -> None:
        """Solution represents minimum energy configuration"""
        return None

    @property
    def bounds(self):
        """Bounds with first molecule fixed at origin and x-component of second fixed"""
        p = self.p
        lbs = jnp.full(3 * p, -jnp.inf)
        ubs = jnp.full(3 * p, jnp.inf)

        # Fix first molecule at origin (indices 0, 1, 2 for X1, Y1, Z1)
        lbs = lbs.at[0:3].set(0.0)
        ubs = ubs.at[0:3].set(0.0)

        # Fix x-component of second molecule (index 3 for X2)
        lbs = lbs.at[3].set(0.0)
        ubs = ubs.at[3].set(0.0)

        return lbs, ubs

    @property
    def expected_objective_value(self) -> Array:
        """Expected optimal objective value: 0"""
        return inexact_asarray(0.0)
