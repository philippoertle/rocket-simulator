"""
System Integrator - Connects Module 1 (Combustion) with Module 2 (System Dynamics)

This module provides end-to-end simulation capability.

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-1, FR-2, FR-3, FR-6 (Parametric studies)
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

from ..combustion.cantera_wrapper import (
    simulate_combustion,
    CombustionResult,
    validate_combustion_inputs
)
from .materials import MaterialProperties, get_material, get_bottle_material
from .burst_calculator import (
    VesselGeometry,
    calculate_burst_pressure,
    predict_failure_pressure
)
from .ode_solver import simulate_system_dynamics, SystemState


@dataclass
class SimulationConfig:
    """
    Complete configuration for end-to-end simulation.

    Attributes:
        # Combustion parameters
        vessel_volume: Internal volume (m³)
        fuel_oxidizer_ratio: H₂:O₂ molar ratio
        initial_temperature: Initial gas temperature (K)
        initial_pressure: Initial pressure (Pa)

        # Vessel geometry
        vessel_diameter: Inner diameter (m)
        vessel_thickness: Wall thickness (m)
        vessel_length: Cylindrical length (m)
        vessel_material: Material name or MaterialProperties

        # Simulation parameters
        combustion_time: Combustion simulation time (s)
        system_time: System dynamics time (s), if different
        max_step: Maximum ODE step size (s)
        failure_criterion: "yield" or "ultimate"
    """
    # Combustion
    vessel_volume: float
    fuel_oxidizer_ratio: float
    initial_temperature: float = 300.0
    initial_pressure: float = 101325.0

    # Geometry
    vessel_diameter: float = 0.095
    vessel_thickness: float = 0.0003
    vessel_length: float = 0.30
    vessel_material: str = "PET"

    # Simulation
    combustion_time: float = 0.01
    system_time: Optional[float] = None
    max_step: float = 1e-4
    failure_criterion: str = "yield"


def run_full_simulation(config: SimulationConfig) -> Tuple[CombustionResult, SystemState]:
    """
    Run complete end-to-end simulation: combustion → system dynamics → failure.

    Args:
        config: Simulation configuration

    Returns:
        (combustion_result, system_state) tuple

    Example:
        >>> config = SimulationConfig(
        ...     vessel_volume=0.001,  # 1L
        ...     fuel_oxidizer_ratio=2.0,
        ...     vessel_diameter=0.095,
        ...     vessel_thickness=0.0003,
        ...     vessel_material="PET"
        ... )
        >>> comb, sys = run_full_simulation(config)
        >>> print(f"Peak pressure: {np.max(sys.pressure)/1e5:.1f} bar")
        >>> if sys.failed:
        ...     print(f"FAILED at t={sys.failure_time:.4f} s")
    """
    # Step 1: Run combustion simulation (Module 1)
    print(f"Running combustion simulation (V={config.vessel_volume*1e3:.1f} L, MR={config.fuel_oxidizer_ratio})...")

    combustion_result = simulate_combustion(
        volume=config.vessel_volume,
        mix_ratio=config.fuel_oxidizer_ratio,
        T0=config.initial_temperature,
        P0=config.initial_pressure,
        end_time=config.combustion_time,
        n_points=int(config.combustion_time / config.max_step)
    )

    print(f"  Peak combustion pressure: {np.max(combustion_result.pressure)/1e5:.2f} bar")
    print(f"  Peak temperature: {np.max(combustion_result.temperature):.0f} K")

    # Step 2: Set up vessel geometry and material
    geometry = VesselGeometry(
        inner_diameter=config.vessel_diameter,
        wall_thickness=config.vessel_thickness,
        length=config.vessel_length
    )

    if isinstance(config.vessel_material, str):
        material = get_material(config.vessel_material)
    else:
        material = config.vessel_material

    # Calculate theoretical burst pressure
    P_burst = predict_failure_pressure(geometry, material, criterion=config.failure_criterion)
    print(f"  Theoretical burst pressure: {P_burst/1e5:.2f} bar ({config.failure_criterion} criterion)")

    # Step 3: Run system dynamics (Module 2)
    print(f"Running system dynamics simulation...")

    system_time = config.system_time if config.system_time is not None else config.combustion_time

    system_state = simulate_system_dynamics(
        combustion_result=combustion_result,
        geometry=geometry,
        material=material,
        end_time=system_time,
        max_step=config.max_step,
        failure_criterion=config.failure_criterion,
        include_deformation=False  # Simplified for now
    )

    print(f"  Peak system pressure: {np.max(system_state.pressure)/1e5:.2f} bar")
    print(f"  Min safety factor: {np.min(system_state.safety_factor):.2f}")

    if system_state.failed:
        print(f"  ⚠️ VESSEL FAILED at t={system_state.failure_time:.6f} s")
        print(f"  Failure mode: {system_state.failure_mode}")
    else:
        print(f"  ✅ Vessel intact (SF > 1.0)")

    return combustion_result, system_state


def run_parametric_study(
    base_config: SimulationConfig,
    parameter_name: str,
    parameter_values: List[float]
) -> List[Tuple[float, CombustionResult, SystemState]]:
    """
    Run parametric study varying one parameter.

    Args:
        base_config: Base configuration
        parameter_name: Name of parameter to vary (e.g., "fuel_oxidizer_ratio")
        parameter_values: List of values to test

    Returns:
        List of (parameter_value, combustion_result, system_state) tuples

    Example:
        >>> config = SimulationConfig(vessel_volume=0.001, fuel_oxidizer_ratio=2.0)
        >>> results = run_parametric_study(config, "fuel_oxidizer_ratio", [1.5, 2.0, 2.5, 3.0])
        >>> for val, comb, sys in results:
        ...     print(f"MR={val}: P_max={np.max(sys.pressure)/1e5:.1f} bar, Failed={sys.failed}")
    """
    results = []

    print(f"=== Parametric Study: {parameter_name} ===")
    print(f"Testing {len(parameter_values)} values...\n")

    for i, value in enumerate(parameter_values):
        print(f"[{i+1}/{len(parameter_values)}] {parameter_name} = {value}")

        # Create modified config
        config = SimulationConfig(**vars(base_config))
        setattr(config, parameter_name, value)

        # Run simulation
        comb, sys = run_full_simulation(config)

        results.append((value, comb, sys))
        print()

    return results


def estimate_safe_operating_pressure(
    geometry: VesselGeometry,
    material: MaterialProperties,
    target_safety_factor: float = 4.0,
    criterion: str = "yield"
) -> float:
    """
    Estimate safe operating pressure for a given safety factor.

    Args:
        geometry: Vessel geometry
        material: Material properties
        target_safety_factor: Desired safety factor (default 4.0)
        criterion: "yield" or "ultimate"

    Returns:
        Safe operating pressure (Pa)

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        >>> pet = get_material("PET")
        >>> P_safe = estimate_safe_operating_pressure(geom, pet, target_safety_factor=4.0)
        >>> print(f"Safe pressure (SF=4): {P_safe/1e5:.1f} bar")
    """
    P_burst = predict_failure_pressure(geometry, material, criterion=criterion)
    P_safe = P_burst / target_safety_factor
    return P_safe


# Demonstration
if __name__ == "__main__":
    print("=== System Integrator Module ===\n")

    # Example 1: Single simulation
    print("Example 1: 2L PET bottle with stoichiometric H₂/O₂")
    print("-" * 60)

    config = SimulationConfig(
        vessel_volume=0.002,         # 2L
        fuel_oxidizer_ratio=2.0,     # Stoichiometric
        vessel_diameter=0.095,       # 95 mm
        vessel_thickness=0.0003,     # 0.3 mm
        vessel_length=0.30,          # 30 cm
        vessel_material="PET",
        combustion_time=0.01,        # 10 ms
        max_step=1e-5
    )

    try:
        comb_result, sys_result = run_full_simulation(config)

        print("\n" + "="*60)
        print("RESULTS SUMMARY:")
        print(f"  Peak Pressure: {np.max(sys_result.pressure)/1e5:.2f} bar")
        print(f"  Peak Temperature: {np.max(sys_result.temperature):.0f} K")
        print(f"  Peak Hoop Stress: {np.max(sys_result.hoop_stress)/1e6:.1f} MPa")
        print(f"  Min Safety Factor: {np.min(sys_result.safety_factor):.2f}")
        print(f"  Vessel Status: {'❌ FAILED' if sys_result.failed else '✅ Safe'}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*60)
    print("\n⚠️ This is for educational purposes only!")
    print("Real rocket experiments are dangerous and potentially illegal.\n")
