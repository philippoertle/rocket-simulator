"""
Full System Integration - Complete M1→M2→M3 Simulation

This module orchestrates end-to-end simulations combining:
- Module 1: Combustion (thermochemistry)
- Module 2: System dynamics (ODE + thin-wall)
- Module 3: FEM analysis (thick-wall + stress concentrations)

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-1 through FR-9 (complete system)
"""

import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Any
import time
import warnings

from ..combustion.cantera_wrapper import simulate_combustion, CombustionResult
from ..system_model import (
    SimulationConfig,
    run_full_simulation as run_system_simulation,
    VesselGeometry,
    get_material,
    MaterialProperties,
)
from ..fem import (
    solve_lame_equations,
    calculate_maximum_stress,
    estimate_failure_location,
    compare_thick_vs_thin_wall,
)


@dataclass
class FullSimulationConfig:
    """
    Complete end-to-end simulation configuration.

    This consolidates all parameters needed for M1→M2→M3 simulation.

    Attributes:
        # Combustion parameters (Module 1)
        volume: Vessel internal volume (m³)
        fuel_oxidizer_ratio: H₂:O₂ molar ratio
        initial_temperature: Initial gas temperature (K)
        initial_pressure: Initial pressure (Pa)
        combustion_time: Combustion simulation duration (s)

        # Vessel geometry (Modules 2 & 3)
        vessel_diameter: Inner diameter (m)
        vessel_thickness: Wall thickness (m)
        vessel_length: Cylindrical length (m)
        vessel_material: Material name (e.g., "PET")

        # Advanced features (Module 3)
        cap_type: End cap type ("hemispherical", "flat", etc.)
        include_threads: Include thread stress concentrations
        include_transition: Include neck transition stress

        # Analysis options
        failure_criterion: "yield" or "ultimate"
        max_step: Maximum ODE time step (s)
        n_points_fem: Number of points for FEM through-thickness
    """
    # Combustion
    volume: float
    fuel_oxidizer_ratio: float
    initial_temperature: float = 300.0
    initial_pressure: float = 101325.0
    combustion_time: float = 0.01

    # Vessel
    vessel_diameter: float = 0.095
    vessel_thickness: float = 0.0003
    vessel_length: float = 0.30
    vessel_material: str = "PET"

    # Advanced
    cap_type: str = "hemispherical"
    include_threads: bool = True
    include_transition: bool = False

    # Analysis
    failure_criterion: str = "yield"
    max_step: float = 1e-5
    n_points_fem: int = 50

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary."""
        return asdict(self)


@dataclass
class FullSimulationResult:
    """
    Complete simulation results from all three modules.

    Attributes:
        config: Input configuration
        combustion: Module 1 results
        system: Module 2 results
        fem_analysis: Module 3 results
        summary: Key summary statistics
        warnings: List of warnings generated
        execution_time: Total simulation time (s)
        failed: Whether vessel failed
        failure_location: Where failure occurred
        safety_margin: Minimum safety factor achieved
    """
    config: FullSimulationConfig
    combustion: CombustionResult
    system: Any  # SystemState from Module 2
    fem_analysis: Dict[str, Any]
    summary: Dict[str, float]
    warnings: list = field(default_factory=list)
    execution_time: float = 0.0
    failed: bool = False
    failure_location: Optional[str] = None
    safety_margin: float = float('inf')

    def to_dict(self) -> Dict[str, Any]:
        """Export full results to dictionary for JSON serialization."""
        return {
            'config': self.config.to_dict(),
            'combustion': self.combustion.to_dict(),
            'system': self.system.to_dict() if hasattr(self.system, 'to_dict') else {},
            'fem_analysis': self.fem_analysis,
            'summary': self.summary,
            'warnings': self.warnings,
            'execution_time': self.execution_time,
            'failed': self.failed,
            'failure_location': self.failure_location,
            'safety_margin': self.safety_margin,
        }


def run_complete_simulation(config: FullSimulationConfig, verbose: bool = True) -> FullSimulationResult:
    """
    Run complete end-to-end simulation: M1 → M2 → M3.

    This orchestrates the full simulation pipeline:
    1. Combustion simulation (Cantera)
    2. System dynamics (ODE + thin-wall analytical)
    3. FEM analysis (Lamé + stress concentrations)
    4. Summary statistics and failure prediction

    Args:
        config: Full simulation configuration
        verbose: Print progress messages

    Returns:
        FullSimulationResult with all data and analysis

    Example:
        >>> config = FullSimulationConfig(
        ...     volume=0.002,  # 2L bottle
        ...     fuel_oxidizer_ratio=2.0,
        ...     vessel_diameter=0.095,
        ...     vessel_thickness=0.0003,
        ...     vessel_material="PET",
        ...     cap_type="flat"
        ... )
        >>> result = run_complete_simulation(config)
        >>> print(f"Peak pressure: {result.summary['peak_pressure']/1e5:.1f} bar")
        >>> print(f"Failed: {result.failed}")
        >>> if result.failed:
        ...     print(f"Failure at: {result.failure_location}")
    """
    start_time = time.time()
    warnings_list = []

    if verbose:
        print("=" * 70)
        print("PET ROCKET SIMULATOR - Full System Analysis")
        print("=" * 70)
        print(f"Configuration: {config.volume*1000:.1f}L, MR={config.fuel_oxidizer_ratio:.1f}, "
              f"Material={config.vessel_material}")
        print()

    # Step 1: Module 1 - Combustion simulation
    if verbose:
        print("[1/3] Running combustion simulation (Cantera)...")

    combustion_result = simulate_combustion(
        volume=config.volume,
        mix_ratio=config.fuel_oxidizer_ratio,
        T0=config.initial_temperature,
        P0=config.initial_pressure,
        end_time=config.combustion_time,
        n_points=int(config.combustion_time / config.max_step)
    )

    if verbose:
        print(f"      Peak combustion pressure: {np.max(combustion_result.pressure)/1e5:.2f} bar")
        print(f"      Peak temperature: {np.max(combustion_result.temperature):.0f} K")
        print(f"      Max dP/dt: {combustion_result.max_dPdt/1e9:.2f} GPa/s")

    # Step 2: Module 2 - System dynamics
    if verbose:
        print("\n[2/3] Running system dynamics (ODE + thin-wall analysis)...")

    # Create system simulation config
    sys_config = SimulationConfig(
        vessel_volume=config.volume,
        fuel_oxidizer_ratio=config.fuel_oxidizer_ratio,
        initial_temperature=config.initial_temperature,
        initial_pressure=config.initial_pressure,
        vessel_diameter=config.vessel_diameter,
        vessel_thickness=config.vessel_thickness,
        vessel_length=config.vessel_length,
        vessel_material=config.vessel_material,
        combustion_time=config.combustion_time,
        max_step=config.max_step,
        failure_criterion=config.failure_criterion
    )

    # Run system simulation (M1→M2 integration)
    _, system_result = run_system_simulation(sys_config)

    if verbose:
        print(f"      Peak system pressure: {np.max(system_result.pressure)/1e5:.2f} bar")
        print(f"      Min safety factor: {np.min(system_result.safety_factor):.2f}")
        if system_result.failed:
            print(f"      ⚠️  VESSEL FAILED at t={system_result.failure_time:.6f} s")

    # Step 3: Module 3 - FEM analysis (thick-wall + stress concentrations)
    if verbose:
        print("\n[3/3] Running FEM analysis (Lamé + stress concentrations)...")

    # Set up geometry and material
    geometry = VesselGeometry(
        inner_diameter=config.vessel_diameter,
        wall_thickness=config.vessel_thickness,
        length=config.vessel_length
    )
    material = get_material(config.vessel_material)

    # Peak pressure for FEM analysis
    P_max = np.max(system_result.pressure)

    # Thick-wall analysis (Lamé equations)
    r_i = config.vessel_diameter / 2
    r_o = r_i + config.vessel_thickness

    lame_result = solve_lame_equations(
        inner_radius=r_i,
        outer_radius=r_o,
        internal_pressure=P_max,
        material=material,
        n_points=config.n_points_fem
    )

    # Thick vs thin-wall comparison
    comparison = compare_thick_vs_thin_wall(geometry, P_max, material)

    # Stress concentrations
    stress_concentration_result = calculate_maximum_stress(
        pressure=P_max,
        geometry=geometry,
        material=material,
        cap_type=config.cap_type,
        include_thread=config.include_threads,
        include_transition=config.include_transition
    )

    # Failure location prediction
    failure_loc = estimate_failure_location(P_max, geometry, config.cap_type)

    if verbose:
        print(f"      Max hoop stress (inner): {lame_result.sigma_theta[0]/1e6:.1f} MPa")
        print(f"      Max von Mises stress: {np.max(lame_result.sigma_vm)/1e6:.1f} MPa")
        print(f"      Stress concentration factor: {stress_concentration_result['K_total']:.2f}")
        print(f"      Critical location: {stress_concentration_result['location']}")
        print(f"      Thin-wall error: {comparison['error_percent']:.2f}%")

    # Compile FEM results
    fem_analysis = {
        'lame_solution': {
            'r': lame_result.r.tolist(),
            'sigma_hoop': lame_result.sigma_theta.tolist(),
            'sigma_radial': lame_result.sigma_r.tolist(),
            'sigma_axial': lame_result.sigma_z.tolist(),
            'sigma_vm': lame_result.sigma_vm.tolist(),
            'displacement': lame_result.u_r.tolist(),
        },
        'thick_vs_thin': comparison,
        'stress_concentrations': stress_concentration_result,
        'failure_location_predicted': failure_loc,
    }

    # Calculate summary statistics
    summary = {
        'peak_pressure': np.max(system_result.pressure),
        'peak_temperature': np.max(system_result.temperature),
        'max_dPdt': combustion_result.max_dPdt,
        'min_safety_factor': np.min(system_result.safety_factor),
        'max_hoop_stress': np.max(lame_result.sigma_theta),
        'max_von_mises_stress': np.max(lame_result.sigma_vm),
        'stress_concentration_factor': stress_concentration_result['K_total'],
        'max_stress_with_concentration': stress_concentration_result['sigma_max'],
        'safety_factor_with_concentration': material.yield_strength / stress_concentration_result['sigma_max'],
    }

    # Determine overall failure status
    failed = system_result.failed or (summary['safety_factor_with_concentration'] < 1.0)
    failure_location = stress_concentration_result['location'] if failed else None
    safety_margin = min(summary['min_safety_factor'], summary['safety_factor_with_concentration'])

    # Check for warnings
    if comparison['thickness_ratio'] > 0.05:
        warnings_list.append(f"Thick wall (t/D={comparison['thickness_ratio']:.3f}): "
                           f"thin-wall error {comparison['error_percent']:.1f}%")

    if config.cap_type == "flat":
        warnings_list.append("Flat end cap has high stress concentration (K=2.5)")

    if config.include_threads:
        warnings_list.append("Threads included: high stress concentration zone")

    if safety_margin < 2.0:
        warnings_list.append(f"Low safety margin: SF={safety_margin:.2f} < 2.0")

    execution_time = time.time() - start_time

    if verbose:
        print("\n" + "=" * 70)
        print("SIMULATION COMPLETE")
        print("=" * 70)
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"\nSUMMARY:")
        print(f"  Peak Pressure: {summary['peak_pressure']/1e5:.2f} bar")
        print(f"  Peak Temperature: {summary['peak_temperature']:.0f} K")
        print(f"  Min Safety Factor: {summary['min_safety_factor']:.2f}")
        print(f"  Safety Factor (w/ concentrations): {summary['safety_factor_with_concentration']:.2f}")
        print(f"  Vessel Status: {'❌ FAILED' if failed else '✅ Safe'}")
        if failed:
            print(f"  Failure Location: {failure_location}")
        print(f"\nWARNINGS: {len(warnings_list)}")
        for w in warnings_list:
            print(f"  - {w}")
        print("=" * 70)

    return FullSimulationResult(
        config=config,
        combustion=combustion_result,
        system=system_result,
        fem_analysis=fem_analysis,
        summary=summary,
        warnings=warnings_list,
        execution_time=execution_time,
        failed=failed,
        failure_location=failure_location,
        safety_margin=safety_margin
    )


# Demonstration
if __name__ == "__main__":
    print("\n=== Full System Integration Demo ===\n")

    # Example 1: Safe configuration (hemispherical cap)
    print("Example 1: 2L PET bottle with hemispherical cap (SAFE)")
    print("-" * 70)

    config_safe = FullSimulationConfig(
        volume=0.002,  # 2L
        fuel_oxidizer_ratio=2.0,
        vessel_diameter=0.095,
        vessel_thickness=0.0003,
        vessel_material="PET",
        cap_type="hemispherical",
        include_threads=False,
        combustion_time=0.001  # Short simulation for demo
    )

    result_safe = run_complete_simulation(config_safe, verbose=True)

    print("\n\n")

    # Example 2: Dangerous configuration (flat cap)
    print("Example 2: 2L PET bottle with flat cap (DANGEROUS)")
    print("-" * 70)

    config_dangerous = FullSimulationConfig(
        volume=0.002,
        fuel_oxidizer_ratio=2.0,
        vessel_diameter=0.095,
        vessel_thickness=0.0003,
        vessel_material="PET",
        cap_type="flat",
        include_threads=True,
        combustion_time=0.001
    )

    result_dangerous = run_complete_simulation(config_dangerous, verbose=True)
