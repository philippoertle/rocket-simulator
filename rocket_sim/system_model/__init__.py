"""
Module 2: System Model - ODE-based dynamics and structural analysis

This module provides:
- Material properties database
- Analytical burst pressure calculations
- System dynamics ODE solver
- Integration with combustion module

ISO/IEC/IEEE 12207:2017 - Implementation Process
"""

__version__ = "0.1.0"

from .materials import (
    MaterialProperties,
    get_material,
    list_available_materials,
    get_bottle_material,
)

from .burst_calculator import (
    VesselGeometry,
    StressState,
    calculate_hoop_stress,
    calculate_axial_stress,
    calculate_von_mises_stress,
    calculate_stress_state,
    calculate_burst_pressure,
    calculate_safety_factor,
    check_failure,
    predict_failure_pressure,
)

from .ode_solver import (
    SystemState,
    simulate_system_dynamics,
)

from .system_integrator import (
    SimulationConfig,
    run_full_simulation,
    run_parametric_study,
    estimate_safe_operating_pressure,
)

__all__ = [
    # Materials
    "MaterialProperties",
    "get_material",
    "list_available_materials",
    "get_bottle_material",
    # Burst calculator
    "VesselGeometry",
    "StressState",
    "calculate_hoop_stress",
    "calculate_axial_stress",
    "calculate_von_mises_stress",
    "calculate_stress_state",
    "calculate_burst_pressure",
    "calculate_safety_factor",
    "check_failure",
    "predict_failure_pressure",
    # ODE solver
    "SystemState",
    "simulate_system_dynamics",
    # System integrator
    "SimulationConfig",
    "run_full_simulation",
    "run_parametric_study",
    "estimate_safe_operating_pressure",
]
