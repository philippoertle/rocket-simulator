"""
Module 3: FEM Structural Analysis

This module provides finite element and advanced analytical methods
for detailed stress analysis of pressure vessels.

Features:
- Mesh generation for cylindrical geometries
- Thick-wall cylinder analysis (Lamé equations)
- Stress concentration factors
- Advanced failure prediction

ISO/IEC/IEEE 12207:2017 - Implementation Process
"""

__version__ = "0.1.0"

from .geometry import (
    VesselMesh,
    create_axisymmetric_mesh,
    create_1d_radial_mesh,
    calculate_mesh_quality,
    refine_mesh,
)

from .thick_wall_solver import (
    ThickWallResult,
    solve_lame_equations,
    compare_thick_vs_thin_wall,
    calculate_thick_wall_burst_pressure,
    validate_lame_solution,
)

from .stress_concentrations import (
    calculate_end_cap_stress_factor,
    calculate_thread_stress_factor,
    calculate_transition_radius_factor,
    calculate_maximum_stress,
    estimate_failure_location,
)

__all__ = [
    # Geometry
    "VesselMesh",
    "create_axisymmetric_mesh",
    "create_1d_radial_mesh",
    "calculate_mesh_quality",
    "refine_mesh",
    # Thick-wall solver
    "ThickWallResult",
    "solve_lame_equations",
    "compare_thick_vs_thin_wall",
    "calculate_thick_wall_burst_pressure",
    "validate_lame_solution",
    # Stress concentrations
    "calculate_end_cap_stress_factor",
    "calculate_thread_stress_factor",
    "calculate_transition_radius_factor",
    "calculate_maximum_stress",
    "estimate_failure_location",
]
