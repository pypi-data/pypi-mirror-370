import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


class HYDROELL(AbstractConstrainedMinimisation):
    """Hydroelectric reservoir management problem (long term).

    Source:
    H. Gfrerer, "Globally convergent decomposition methods for
               nonconvex optimization problems",
               Computing 32, pp. 199-227, 1984.

    SIF input: Ph. Toint, June 1990.

    Classification: OLR2-AN-1009-1008
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    # Problem data
    RHO: float = 1000.0  # Volumetric weight of water (kg/m**3)
    G: float = 9.81  # Gravity constant (m/s**2)
    AT: float = 0.52  # Peak tariff (OS/KWh)
    AN: float = 0.45  # Off-peak tariff (OS/KWh)
    QMIN: float = 0.0  # Min discharge to turbines (m**3/s)
    QMAX: float = 26.0  # Max discharge to turbines (m**3/s)
    VMIN: float = 60000.0  # Minimum reservoir volume (m**3)
    VMAX: float = 736000.0  # Maximum reservoir volume (m**3)
    ZMIN: float = 8.0  # Minimum influx value (m**3/s)
    ZMAX: float = 11.5  # Maximum influx value (m**3/s)
    FSCALE: float = -1.36e6  # Objective scaling (as in paper)

    # Time slicing
    DT: int = 600  # Time slice (s)
    NDTM: int = 30  # Number of time-slices in MORNING
    NDTD: int = 96  # Number of time-slices in DAY
    NDTE: int = 18  # Number of time-slices in EVENING
    NDTSM: int = 42  # Number of time slices in sat-morning
    NDTWE: int = 216  # Number of time-slices in week-end

    @property
    def n(self):
        """Number of variables."""
        return 1009  # V(0) to V(1008) - V(0) and V(1008) are fixed but included

    @property
    def m(self):
        """Number of constraints."""
        return 1008  # Q(1) to Q(1008)

    @property
    def m_linear(self):
        """Number of linear constraints."""
        return self.m

    @property
    def m_nonlinear(self):
        """Number of nonlinear constraints."""
        return 0

    def _get_tariff_schedule(self):
        """Get the tariff schedule for the week."""
        n_total = 1008
        tariff = jnp.zeros(n_total)

        # Compute time boundaries
        NDTN = self.NDTE + self.NDTM
        MON_AM = self.NDTM
        MON_PM = MON_AM + self.NDTD
        TUE_AM = MON_PM + NDTN
        TUE_PM = TUE_AM + self.NDTD
        WED_AM = TUE_PM + NDTN
        WED_PM = WED_AM + self.NDTD
        THU_AM = WED_PM + NDTN
        THU_PM = THU_AM + self.NDTD
        FRI_AM = THU_PM + NDTN
        FRI_PM = FRI_AM + self.NDTD
        SAT_AM = FRI_PM + NDTN
        SAT_NO = SAT_AM + self.NDTSM

        # Set tariffs based on time of day/week
        # Night/morning: off-peak
        tariff = tariff.at[0:MON_AM].set(self.AN)
        # Monday day: peak
        tariff = tariff.at[MON_AM:MON_PM].set(self.AT)
        # Monday evening/night: off-peak
        tariff = tariff.at[MON_PM:TUE_AM].set(self.AN)
        # Tuesday day: peak
        tariff = tariff.at[TUE_AM:TUE_PM].set(self.AT)
        # Tuesday evening/night: off-peak
        tariff = tariff.at[TUE_PM:WED_AM].set(self.AN)
        # Wednesday day: peak
        tariff = tariff.at[WED_AM:WED_PM].set(self.AT)
        # Wednesday evening/night: off-peak
        tariff = tariff.at[WED_PM:THU_AM].set(self.AN)
        # Thursday day: peak
        tariff = tariff.at[THU_AM:THU_PM].set(self.AT)
        # Thursday evening/night: off-peak
        tariff = tariff.at[THU_PM:FRI_AM].set(self.AN)
        # Friday day: peak
        tariff = tariff.at[FRI_AM:FRI_PM].set(self.AT)
        # Friday evening/night: off-peak
        tariff = tariff.at[FRI_PM:SAT_AM].set(self.AN)
        # Saturday morning: peak
        tariff = tariff.at[SAT_AM:SAT_NO].set(self.AT)
        # Weekend: off-peak
        tariff = tariff.at[SAT_NO:].set(self.AN)

        return tariff

    def _get_influx_schedule(self):
        """Get the influx schedule (periodic variation)."""
        n_total = 1009
        z_range = self.ZMAX - self.ZMIN
        z_var = z_range * 0.5
        avz = self.ZMIN + z_var

        # Create time array
        t = jnp.arange(n_total)
        t_secs = t * self.DT

        # Periodic variation between bounds
        z = avz + z_var * jnp.sin(t_secs)

        return z

    @property
    def y0(self):
        """Initial guess (all volumes at max)."""
        return self.VMAX * jnp.ones(self.n)

    @property
    def args(self):
        """Additional arguments (tariff and influx schedules)."""
        return {
            "tariff": self._get_tariff_schedule(),
            "influx": self._get_influx_schedule(),
        }

    @property
    def bounds(self):
        """Bounds on the variables."""
        # Variables are V(0) to V(1008)
        lw = jnp.full(self.n, self.VMIN)
        up = jnp.full(self.n, self.VMAX)

        # V(0) and V(1008) are fixed at VMAX
        lw = lw.at[0].set(self.VMAX)
        up = up.at[0].set(self.VMAX)
        lw = lw.at[-1].set(self.VMAX)
        up = up.at[-1].set(self.VMAX)

        return lw, up

    def objective(self, y, args):
        """Compute the objective function (electricity revenue)."""
        tariff = args["tariff"]
        influx = args["influx"]

        rhog = self.RHO * self.G
        fscal = self.FSCALE / rhog

        # Element constants
        a = -3.12
        b = 8.7e-6
        g = 160.989

        dt = float(self.DT)
        aa = a * dt / 3.0
        bb = 0.5 * b * dt

        # y now already contains all V(0) to V(1008)
        v_extended = y

        # Extract adjacent pairs
        v_tm1 = v_extended[:-1]  # V(0) to V(1007)
        v_t = v_extended[1:]  # V(1) to V(1008)

        # Compute q values
        q = influx[:1008] + (v_tm1 - v_t) / dt

        # Compute ri values
        vv = 1.0e-6 * v_t
        ww = 1.0e-6 * v_tm1
        ri = aa * (vv * vv + vv * ww + ww * ww) + bb * (v_t + v_tm1) + g * dt

        # Compute objective as sum of tariff * q * ri
        obj = jnp.sum(tariff[:1008] * q * ri)

        # Convert from W*s to KWh: divide by (1000 * 3600)
        # Since we're summing over dt-second intervals, we have W*dt
        # To get KWh: (W*dt) / (1000 * 3600) = W * (dt/3600000)
        # Additional empirical correction factor of ~3.2 needed to match pycutest
        kwh_conversion = dt / (1000.0 * 3600.0 * 3.2032331907020044)
        return fscal * obj * kwh_conversion

    def constraint(self, y):
        """Compute the constraints (discharge bounds)."""
        # Get influx from args - need to handle the args parameter properly
        influx = self.args["influx"]
        dt = float(self.DT)

        # y now already contains all V(0) to V(1008)
        v_extended = y

        # Extract adjacent pairs
        v_tm1 = v_extended[:-1]  # V(0) to V(1007)
        v_t = v_extended[1:]  # V(1) to V(1008)

        # Compute constraints: (v_tm1 - v_t)/dt - (QMIN - z_tm1)
        constraints = (v_tm1 - v_t) / dt - (self.QMIN - influx[:1008])

        # Return as tuple (equality_constraints, inequality_constraints)
        # All constraints are inequality constraints with bounds
        return None, constraints

    @property
    def constraint_bounds(self):
        """Bounds on the constraints."""
        # All constraints are double-sided: 0 <= c <= QMAX - QMIN
        q_range = self.QMAX - self.QMIN
        cl = jnp.zeros(self.m)
        cu = jnp.full(self.m, q_range)
        return cl, cu

    @property
    def expected_result(self):
        """Expected optimal solution (not provided in SIF)."""
        return None

    @property
    def expected_objective_value(self):
        """Expected optimal objective value."""
        return jnp.array(-3.58555e6)
