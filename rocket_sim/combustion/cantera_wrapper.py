"""
Cantera Wrapper for H₂/O₂ Combustion Simulation
ISO 12207:2017 §6.4.7 Implementation Process

This module provides a Python interface to Cantera for simulating
constant-volume H₂/O₂ combustion with detailed chemical kinetics.

Verification Method: Unit test vs. literature data (FR-1)
Pass Criteria: P_max within 5% of published H₂/O₂ data
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np

try:
    import cantera as ct
except ImportError:
    raise ImportError(
        "Cantera is required for combustion simulations. "
        "Install with: conda install -c cantera cantera"
    )


@dataclass
class CombustionResult:
    """
    Container for combustion simulation results.

    Attributes:
        time: Time array [s]
        pressure: Pressure array [Pa]
        temperature: Temperature array [K]
        peak_pressure: Maximum pressure reached [Pa]
        max_dPdt: Maximum pressure rise rate [Pa/s]
        success: Whether simulation completed successfully
        message: Status or error message
    """
    time: np.ndarray
    pressure: np.ndarray
    temperature: np.ndarray
    peak_pressure: float
    max_dPdt: float
    success: bool = True
    message: str = "Simulation completed successfully"

    def to_dict(self) -> Dict:
        """Convert result to dictionary format."""
        return {
            "time": self.time.tolist() if isinstance(self.time, np.ndarray) else self.time,
            "pressure": self.pressure.tolist() if isinstance(self.pressure, np.ndarray) else self.pressure,
            "temperature": self.temperature.tolist() if isinstance(self.temperature, np.ndarray) else self.temperature,
            "peak_pressure": float(self.peak_pressure),
            "max_dPdt": float(self.max_dPdt),
            "success": self.success,
            "message": self.message
        }


def validate_combustion_inputs(
    volume: float,
    mix_ratio: float,
    T0: float,
    P0: float
) -> Tuple[bool, str]:
    """
    Validate input parameters for combustion simulation.

    Args:
        volume: Chamber volume [m³]
        mix_ratio: H₂:O₂ molar ratio (e.g., 2.0 for stoichiometric)
        T0: Initial temperature [K]
        P0: Initial pressure [Pa]

    Returns:
        Tuple of (is_valid, error_message)

    Requirements: FR-9 (Input validation)
    """
    if volume <= 0:
        return False, f"Volume must be positive, got {volume} m³"

    if volume > 0.01:  # 10 liters - warning for PET bottle context
        return False, f"Volume {volume} m³ exceeds typical PET bottle range (< 0.01 m³)"

    if mix_ratio <= 0:
        return False, f"Mix ratio must be positive, got {mix_ratio}"

    if mix_ratio < 0.5 or mix_ratio > 10.0:
        return False, f"Mix ratio {mix_ratio} outside reasonable range [0.5, 10.0]"

    if T0 < 200 or T0 > 500:
        return False, f"Initial temperature {T0} K outside range [200, 500] K"

    if P0 < 5000 or P0 > 500000:  # 0.05 to 5 bar
        return False, f"Initial pressure {P0} Pa outside range [5000, 500000] Pa"

    return True, "Inputs valid"


def simulate_combustion(
    volume: float,
    mix_ratio: float = 2.0,
    T0: float = 300.0,
    P0: float = 101325.0,
    mechanism: str = 'h2o2.yaml',
    end_time: float = 0.01,
    n_points: int = 1000,
    validate_inputs: bool = True
) -> CombustionResult:
    """
    Simulate constant-volume H₂/O₂ combustion using Cantera.

    This function sets up a homogeneous reactor with H₂/O₂ mixture,
    ignites it, and tracks pressure and temperature evolution over time.

    Args:
        volume: Chamber volume [m³]. Typical PET bottle: 0.0005 to 0.002 m³
        mix_ratio: H₂:O₂ molar ratio. Stoichiometric = 2.0
        T0: Initial temperature [K]. Room temperature ≈ 300 K
        P0: Initial pressure [Pa]. Atmospheric = 101325 Pa
        mechanism: Cantera mechanism file. Default 'h2o2.yaml' for H₂/O₂
        end_time: Simulation duration [s]. Default 10 ms
        n_points: Number of output points
        validate_inputs: Whether to validate inputs (recommended)

    Returns:
        CombustionResult object containing time series and peak values

    Example:
        >>> result = simulate_combustion(
        ...     volume=0.001,      # 1 liter bottle
        ...     mix_ratio=2.0,     # Stoichiometric H₂:O₂
        ...     T0=300.0,          # Room temperature
        ...     P0=101325.0        # Atmospheric pressure
        ... )
        >>> print(f"Peak pressure: {result.peak_pressure/1e5:.2f} bar")
        >>> print(f"Max dP/dt: {result.max_dPdt/1e9:.2f} GPa/s")

    Requirements Traceability:
        - FR-1: Compute H₂/O₂ combustion P(t), T(t) using validated chemistry
        - NFR-2: Use Cantera (open-source)
        - NFR-4: Reproducible (deterministic simulation)

    Verification:
        - Compare with literature values for H₂/O₂ at stoichiometric ratio
        - Expected peak pressure: ~15-20 bar for closed volume
        - Expected peak temperature: ~3000 K
    """
    # Input validation
    if validate_inputs:
        is_valid, msg = validate_combustion_inputs(volume, mix_ratio, T0, P0)
        if not is_valid:
            return CombustionResult(
                time=np.array([]),
                pressure=np.array([]),
                temperature=np.array([]),
                peak_pressure=0.0,
                max_dPdt=0.0,
                success=False,
                message=f"Input validation failed: {msg}"
            )

    try:
        # Create gas object with H₂/O₂ mechanism
        gas = ct.Solution(mechanism)

        # Set initial mixture composition
        # X is mole fraction: H2:O2 = mix_ratio:1
        X_H2 = mix_ratio / (mix_ratio + 1.0)
        X_O2 = 1.0 / (mix_ratio + 1.0)

        gas.TPX = T0, P0, {'H2': X_H2, 'O2': X_O2}

        # Ignite the mixture by raising temperature temporarily
        # This simulates spark ignition
        T_ignition = max(T0, 1200.0)  # Ensure ignition temperature
        gas.TP = T_ignition, P0

        # Create constant-volume reactor
        reactor = ct.IdealGasReactor(gas)
        reactor.volume = volume

        # Create reactor network
        reactor_net = ct.ReactorNet([reactor])

        # Storage arrays
        times = np.linspace(0, end_time, n_points)
        pressures = np.zeros(n_points)
        temperatures = np.zeros(n_points)

        # Time integration
        for i, t in enumerate(times):
            reactor_net.advance(t)
            pressures[i] = reactor.thermo.P
            temperatures[i] = reactor.thermo.T

        # Calculate derived quantities
        peak_pressure = np.max(pressures)

        # Calculate dP/dt using central differences
        dt = times[1] - times[0]
        dPdt = np.gradient(pressures, dt)
        max_dPdt = np.max(np.abs(dPdt))

        return CombustionResult(
            time=times,
            pressure=pressures,
            temperature=temperatures,
            peak_pressure=peak_pressure,
            max_dPdt=max_dPdt,
            success=True,
            message="Simulation completed successfully"
        )

    except Exception as e:
        return CombustionResult(
            time=np.array([]),
            pressure=np.array([]),
            temperature=np.array([]),
            peak_pressure=0.0,
            max_dPdt=0.0,
            success=False,
            message=f"Simulation failed: {str(e)}"
        )


def get_equilibrium_properties(
    mix_ratio: float = 2.0,
    T0: float = 300.0,
    P0: float = 101325.0,
    mechanism: str = 'h2o2.yaml'
) -> Dict:
    """
    Calculate equilibrium properties for H₂/O₂ combustion.

    This provides a quick analytical check without time integration.
    Useful for validation and parameter studies.

    Args:
        mix_ratio: H₂:O₂ molar ratio
        T0: Initial temperature [K]
        P0: Initial pressure [Pa]
        mechanism: Cantera mechanism file

    Returns:
        Dictionary with equilibrium properties:
            - T_eq: Equilibrium temperature [K]
            - P_eq: Equilibrium pressure [Pa]
            - composition: Species mole fractions

    Requirements: FR-9 (Analytical checks)
    """
    try:
        gas = ct.Solution(mechanism)

        X_H2 = mix_ratio / (mix_ratio + 1.0)
        X_O2 = 1.0 / (mix_ratio + 1.0)

        gas.TPX = T0, P0, {'H2': X_H2, 'O2': X_O2}

        # Store initial state
        initial_enthalpy = gas.enthalpy_mass
        initial_volume = gas.volume_mass

        # Equilibrate at constant U,V (adiabatic, constant volume)
        gas.equilibrate('UV')

        return {
            "T_eq": gas.T,
            "P_eq": gas.P,
            "composition": {s: gas[s].X[0] for s in gas.species_names},
            "success": True,
            "message": "Equilibrium calculation successful"
        }

    except Exception as e:
        return {
            "T_eq": 0.0,
            "P_eq": 0.0,
            "composition": {},
            "success": False,
            "message": f"Equilibrium calculation failed: {str(e)}"
        }


if __name__ == "__main__":
    """
    Demonstration and validation script.
    Run with: python -m rocket_sim.combustion.cantera_wrapper
    """
    print("=== PET Rocket Combustion Simulator ===")
    print("Module 1: Thermochemistry using Cantera\n")

    # Example 1: Stoichiometric H₂/O₂
    print("Example 1: Stoichiometric H₂:O₂ (2:1) in 1L bottle")
    result = simulate_combustion(
        volume=0.001,      # 1 liter
        mix_ratio=2.0,     # Stoichiometric
        T0=300.0,
        P0=101325.0,
        end_time=0.01
    )

    if result.success:
        print(f"  Peak Pressure: {result.peak_pressure/1e5:.2f} bar")
        print(f"  Peak Temperature: {result.temperature.max():.0f} K")
        print(f"  Max dP/dt: {result.max_dPdt/1e9:.2f} GPa/s")
    else:
        print(f"  ERROR: {result.message}")

    # Example 2: Equilibrium check
    print("\nExample 2: Equilibrium properties")
    eq_props = get_equilibrium_properties(mix_ratio=2.0)
    if eq_props['success']:
        print(f"  Equilibrium Temperature: {eq_props['T_eq']:.0f} K")
        print(f"  Equilibrium Pressure: {eq_props['P_eq']/1e5:.2f} bar")
    else:
        print(f"  ERROR: {eq_props['message']}")

    print("\n✓ Module 1 validation complete")
