import jax.numpy as jnp

from ..._problem import AbstractUnconstrainedMinimisation


# TODO: This problem still has to be verified against another CUTEst interface.
class ARWHEAD(AbstractUnconstrainedMinimisation):
    """The ARWHEAD function.

    A quartic problem whose Hessian is an arrow-head (downwards) with diagonal central
    part and border-width of 1.

    Source: Problem 55 in
    A.R. Conn, N.I.M. Gould, M. Lescrenier and Ph.L. Toint,
    "Performance of a multifrontal scheme for partially separable optimization",
    Report 88/4, Dept of Mathematics, FUNDP (Namur, B), 1988.

    SIF input: Ph. Toint, Dec 1989.
    Classification: OUR2-AN-V-0
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    n: int = 5000  # SIF file lists 100, 500, 1000, 5000 as suggested dimensions

    def objective(self, y, args):
        del args
        # Based on AMPL model in arwhead.mod
        # sum {i in 1..N-1} (-4*x[i]+3.0) + sum {i in 1..N-1} (x[i]^2+x[N]^2)^2
        yn = y[-1]
        f1 = -4 * y[:-1] + 3  # First sum: -4*x[i] + 3 (not squared!)
        f2 = (y[:-1] ** 2 + yn**2) ** 2  # Second sum: (x[i]^2 + x[N]^2)^2
        return jnp.sum(f1 + f2)

    @property
    def y0(self):
        return jnp.ones(self.n)

    @property
    def args(self):
        return None

    @property
    def expected_result(self):
        return None

    @property
    def expected_objective_value(self):
        return jnp.array(0.0)
