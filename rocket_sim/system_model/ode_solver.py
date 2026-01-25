"""
ODE Solver for Rocket System Dynamics

This module simulates the complete system dynamics by integrating:
1. Combustion pressure data from Module 1
2. Structural response (elastic deformation)
3. Failure detection

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-2 (ODE solver), FR-3 (Burst prediction), NFR-5 (Performance)
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple
import warnings

from ..combustion.cantera_wrapper import CombustionResult
from .materials import MaterialProperties
from .burst_calculator import (
    VesselGeometry,
    calculate_stress_state,
    calculate_safety_factor,
    check_failure
)


@dataclass
class SystemState:
    """
    Complete system state over time.

    Attributes:
        time: Time array (s)
        pressure: Internal pressure (Pa)
        temperature: Gas temperature (K)
        volume: Internal volume (m³), may change with deformation
        hoop_stress: Hoop stress in vessel wall (Pa)
        axial_stress: Axial stress in vessel wall (Pa)
        von_mises_stress: Von Mises equivalent stress (Pa)
        safety_factor: Safety factor against yield
        strain_hoop: Hoop strain (dimensionless)
        failed: Whether vessel has failed
        failure_time: Time of failure (s), None if no failure
        failure_mode: Mode of failure, None if no failure
    """
    time: np.ndarray
    pressure: np.ndarray
    temperature: np.ndarray
    volume: np.ndarray
    hoop_stress: np.ndarray
    axial_stress: np.ndarray
    von_mises_stress: np.ndarray
    safety_factor: np.ndarray
    strain_hoop: np.ndarray
    failed: bool = False
    failure_time: Optional[float] = None
    failure_mode: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for export."""
        return {
            'time': self.time.tolist() if isinstance(self.time, np.ndarray) else self.time,
            'pressure': self.pressure.tolist() if isinstance(self.pressure, np.ndarray) else self.pressure,
            'temperature': self.temperature.tolist() if isinstance(self.temperature, np.ndarray) else self.temperature,
            'volume': self.volume.tolist() if isinstance(self.volume, np.ndarray) else self.volume,
            'hoop_stress': self.hoop_stress.tolist() if isinstance(self.hoop_stress, np.ndarray) else self.hoop_stress,
            'axial_stress': self.axial_stress.tolist() if isinstance(self.axial_stress, np.ndarray) else self.axial_stress,
            'von_mises_stress': self.von_mises_stress.tolist() if isinstance(self.von_mises_stress, np.ndarray) else self.von_mises_stress,
            'safety_factor': self.safety_factor.tolist() if isinstance(self.safety_factor, np.ndarray) else self.safety_factor,
            'strain_hoop': self.strain_hoop.tolist() if isinstance(self.strain_hoop, np.ndarray) else self.strain_hoop,
            'failed': self.failed,
            'failure_time': self.failure_time,
            'failure_mode': self.failure_mode,
        }


def simulate_system_dynamics(
    combustion_result: CombustionResult,
    geometry: VesselGeometry,
    material: MaterialProperties,
    end_time: Optional[float] = None,
    max_step: float = 1e-4,
    failure_criterion: str = "yield",
    include_deformation: bool = False
) -> SystemState:
    """
    Simulate complete system dynamics with combustion + structural response.

    This function integrates combustion data from Module 1 with structural
    analysis to predict system behavior and detect failure.

    Args:
        combustion_result: Results from Module 1 combustion simulation
        geometry: Vessel geometry
        material: Material properties
        end_time: Simulation end time (s). If None, use combustion end time.
        max_step: Maximum ODE integration step size (s)
        failure_criterion: "yield" (conservative) or "ultimate" (catastrophic)
        include_deformation: If True, account for elastic volume change

    Returns:
        SystemState with complete time history

    Example:
        >>> from rocket_sim.combustion import simulate_combustion
        >>> from rocket_sim.system_model import get_material, VesselGeometry
        >>>
        >>> # Run combustion simulation
        >>> comb_result = simulate_combustion(volume=0.001, mix_ratio=2.0)
        >>>
        >>> # Define vessel
        >>> geometry = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        >>> material = get_material("PET")
        >>>
        >>> # Run system simulation
        >>> sys_result = simulate_system_dynamics(comb_result, geometry, material)
        >>> print(f"Peak pressure: {np.max(sys_result.pressure)/1e5:.1f} bar")
        >>> if sys_result.failed:
        ...     print(f"Failed at t={sys_result.failure_time:.4f} s")
    """
    # Determine simulation time
    if end_time is None:
        end_time = combustion_result.time[-1]

    # Create interpolation function for combustion pressure
    # This allows us to query P(t) at any time during ODE integration
    P_interp = interp1d(
        combustion_result.time,
        combustion_result.pressure,
        kind='cubic',
        fill_value='extrapolate',
        bounds_error=False
    )

    T_interp = interp1d(
        combustion_result.time,
        combustion_result.temperature,
        kind='cubic',
        fill_value='extrapolate',
        bounds_error=False
    )

    # Initial volume
    V0 = geometry.inner_diameter**2 * np.pi / 4 * (geometry.length or 0.3)
    if geometry.length is None:
        warnings.warn(
            "Vessel length not specified, assuming 0.3 m for volume calculation",
            UserWarning
        )

    # Storage for results
    time_points = []
    pressure_points = []
    temperature_points = []
    volume_points = []
    hoop_stress_points = []
    axial_stress_points = []
    vm_stress_points = []
    safety_factor_points = []
    strain_points = []

    # Event function to detect failure
    failure_detected = [False]
    failure_time_val = [None]

    def failure_event(t, y):
        """Event function: SF = 1.0 triggers failure."""
        P = P_interp(t)
        SF = calculate_safety_factor(P, geometry, material, criterion=failure_criterion)
        return SF - 1.0  # Zero when SF = 1

    failure_event.terminal = True  # Stop integration at failure
    failure_event.direction = -1   # Trigger when SF decreases through 1

    # ODE system (simplified - just track time and compute stresses)
    def system_ode(t, y):
        """
        ODE system for rocket dynamics.

        For now, this is simplified: we track the combustion pressure
        and compute stresses analytically. Future: add thermal expansion,
        gas leakage, etc.
        """
        # y[0] could be a state variable if needed
        # For this version, we just use t to query combustion data
        return [0.0]  # Dummy derivative

    # Time span
    t_span = (0, end_time)
    t_eval = np.linspace(0, end_time, int(end_time / max_step))

    # Solve ODE (in this simple version, just time-stepping)
    sol = solve_ivp(
        system_ode,
        t_span,
        [0.0],  # Dummy initial condition
        method='RK45',
        t_eval=t_eval,
        events=failure_event,
        max_step=max_step,
        rtol=1e-6,
        atol=1e-9
    )

    # Check if failure occurred
    if len(sol.t_events[0]) > 0:
        failure_detected[0] = True
        failure_time_val[0] = sol.t_events[0][0]
        # Extend time array to include failure point
        time_array = np.append(sol.t, failure_time_val[0])
    else:
        time_array = sol.t

    # Calculate stresses and safety factors at each time point
    for t in time_array:
        P = P_interp(t)
        T = T_interp(t)

        # Calculate stresses
        stress_state = calculate_stress_state(P, geometry)
        SF = calculate_safety_factor(P, geometry, material, criterion=failure_criterion)

        # Calculate strain (elastic)
        epsilon_hoop = stress_state.hoop_stress / material.elastic_modulus

        # Volume change (if including deformation)
        if include_deformation:
            # ΔV/V ≈ 2*ε_hoop + ε_axial (for thin cylinder)
            epsilon_axial = stress_state.axial_stress / material.elastic_modulus
            dV_V = 2 * epsilon_hoop + epsilon_axial
            V = V0 * (1 + dV_V)
        else:
            V = V0

        # Store results
        time_points.append(t)
        pressure_points.append(P)
        temperature_points.append(T)
        volume_points.append(V)
        hoop_stress_points.append(stress_state.hoop_stress)
        axial_stress_points.append(stress_state.axial_stress)
        vm_stress_points.append(stress_state.von_mises_stress)
        safety_factor_points.append(SF)
        strain_points.append(epsilon_hoop)

    # Convert to arrays
    result = SystemState(
        time=np.array(time_points),
        pressure=np.array(pressure_points),
        temperature=np.array(temperature_points),
        volume=np.array(volume_points),
        hoop_stress=np.array(hoop_stress_points),
        axial_stress=np.array(axial_stress_points),
        von_mises_stress=np.array(vm_stress_points),
        safety_factor=np.array(safety_factor_points),
        strain_hoop=np.array(strain_points),
        failed=failure_detected[0],
        failure_time=failure_time_val[0],
        failure_mode="Yield exceeded" if failure_detected[0] else None
    )

    return result


# Demonstration
if __name__ == "__main__":
    print("=== System Dynamics Solver ===\n")
    print("This module requires Module 1 (combustion) to run.")
    print("See integration tests for examples.\n")
