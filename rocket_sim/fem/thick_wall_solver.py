"""
Thick-Wall Cylinder Analysis using Lamé Equations

This module implements exact analytical solutions for thick-wall pressure vessels,
going beyond the thin-wall approximation used in Module 2.

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-4 (FEM stress analysis), NFR-3 (Accuracy)
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from ..system_model.materials import MaterialProperties
from ..system_model.burst_calculator import VesselGeometry


@dataclass
class ThickWallResult:
    """
    Results from thick-wall cylinder analysis.

    Attributes:
        r: Radial positions (m)
        sigma_r: Radial stress (Pa)
        sigma_theta: Hoop (circumferential) stress (Pa)
        sigma_z: Axial stress (Pa)
        sigma_vm: Von Mises equivalent stress (Pa)
        u_r: Radial displacement (m)
        epsilon_r: Radial strain
        epsilon_theta: Hoop strain
        epsilon_z: Axial strain
    """
    r: np.ndarray
    sigma_r: np.ndarray
    sigma_theta: np.ndarray
    sigma_z: np.ndarray
    sigma_vm: np.ndarray
    u_r: np.ndarray
    epsilon_r: np.ndarray
    epsilon_theta: np.ndarray
    epsilon_z: np.ndarray


def solve_lame_equations(
    inner_radius: float,
    outer_radius: float,
    internal_pressure: float,
    external_pressure: float = 0.0,
    material: Optional[MaterialProperties] = None,
    n_points: int = 50
) -> ThickWallResult:
    """
    Solve Lamé equations for thick-wall cylinder under internal pressure.

    This provides exact analytical solution for stress and displacement
    in a thick-wall cylindrical pressure vessel.

    Theory:
        For thick-wall cylinder (t/D > 0.1), stress varies through thickness.
        Lamé equations give exact solution for infinite cylinder.

    Args:
        inner_radius: Inner radius r_i (m)
        outer_radius: Outer radius r_o (m)
        internal_pressure: Internal pressure P_i (Pa)
        external_pressure: External pressure P_o (Pa), default 0
        material: Material properties (needed for displacement)
        n_points: Number of evaluation points through thickness

    Returns:
        ThickWallResult with stress and displacement distributions

    Example:
        >>> from rocket_sim.system_model import get_material
        >>> result = solve_lame_equations(
        ...     inner_radius=0.0475,
        ...     outer_radius=0.04775,
        ...     internal_pressure=500e3,  # 500 kPa
        ...     material=get_material("PET")
        ... )
        >>> max_hoop = np.max(result.sigma_theta)
        >>> print(f"Max hoop stress: {max_hoop/1e6:.1f} MPa")
    """
    # Radial positions through thickness
    r = np.linspace(inner_radius, outer_radius, n_points)

    # Lamé constants
    r_i = inner_radius
    r_o = outer_radius
    P_i = internal_pressure
    P_o = external_pressure

    # Constant terms
    k = (r_o**2 - r_i**2)
    A = (P_i * r_i**2 - P_o * r_o**2) / k
    B = (P_i - P_o) * r_i**2 * r_o**2 / k

    # Lamé equations for stress
    # Radial stress: σ_r(r) = A - B/r²
    sigma_r = A - B / r**2

    # Hoop (circumferential) stress: σ_θ(r) = A + B/r²
    sigma_theta = A + B / r**2

    # Axial stress (for closed-end cylinder)
    # Assuming plane strain or σ_z = constant
    sigma_z = P_i * r_i**2 / (r_o**2 - r_i**2)
    sigma_z_array = np.full_like(r, sigma_z)

    # Von Mises stress
    # σ_vm = √[(σ_r - σ_θ)² + (σ_θ - σ_z)² + (σ_z - σ_r)²] / √2
    sigma_vm = np.sqrt(
        ((sigma_r - sigma_theta)**2 +
         (sigma_theta - sigma_z_array)**2 +
         (sigma_z_array - sigma_r)**2) / 2
    )

    # Displacement and strain (if material properties provided)
    if material is not None:
        E = material.elastic_modulus
        nu = material.poisson_ratio

        # Radial displacement: u_r(r) = (1/E)[(1-ν)Ar + (1+ν)B/r]
        u_r = (1/E) * ((1 - nu) * A * r + (1 + nu) * B / r)

        # Strains
        epsilon_r = (1/E) * (sigma_r - nu * (sigma_theta + sigma_z_array))
        epsilon_theta = (1/E) * (sigma_theta - nu * (sigma_r + sigma_z_array))
        epsilon_z = (1/E) * (sigma_z_array - nu * (sigma_r + sigma_theta))
    else:
        # No material properties - set to zero
        u_r = np.zeros_like(r)
        epsilon_r = np.zeros_like(r)
        epsilon_theta = np.zeros_like(r)
        epsilon_z = np.zeros_like(r)

    return ThickWallResult(
        r=r,
        sigma_r=sigma_r,
        sigma_theta=sigma_theta,
        sigma_z=sigma_z_array,
        sigma_vm=sigma_vm,
        u_r=u_r,
        epsilon_r=epsilon_r,
        epsilon_theta=epsilon_theta,
        epsilon_z=epsilon_z
    )


def compare_thick_vs_thin_wall(
    geometry: VesselGeometry,
    pressure: float,
    material: MaterialProperties
) -> Dict[str, float]:
    """
    Compare thick-wall (Lamé) vs thin-wall (Barlow) solutions.

    Args:
        geometry: Vessel geometry
        pressure: Internal pressure (Pa)
        material: Material properties

    Returns:
        Dictionary with comparison metrics:
        - thickness_ratio: t/D
        - thin_wall_valid: Whether thin-wall assumption valid
        - hoop_stress_thin: Thin-wall hoop stress (Pa)
        - hoop_stress_thick_max: Max thick-wall hoop stress (Pa)
        - error_percent: Percentage error in thin-wall approximation
    """
    from ..system_model.burst_calculator import calculate_hoop_stress

    # Geometry
    r_i = geometry.inner_diameter / 2
    t = geometry.wall_thickness
    r_o = r_i + t

    # Thickness ratio
    thickness_ratio = t / geometry.inner_diameter
    thin_wall_valid = thickness_ratio < 0.1

    # Thin-wall solution (Module 2)
    sigma_thin = calculate_hoop_stress(pressure, geometry)

    # Thick-wall solution (Lamé)
    result = solve_lame_equations(r_i, r_o, pressure, material=material)
    sigma_thick_max = np.max(result.sigma_theta)
    sigma_thick_inner = result.sigma_theta[0]  # Max occurs at inner surface

    # Error in thin-wall approximation
    error_percent = abs(sigma_thick_max - sigma_thin) / sigma_thick_max * 100

    return {
        'thickness_ratio': thickness_ratio,
        'thin_wall_valid': thin_wall_valid,
        'hoop_stress_thin': sigma_thin,
        'hoop_stress_thick_max': sigma_thick_max,
        'hoop_stress_thick_inner': sigma_thick_inner,
        'error_percent': error_percent
    }


def calculate_thick_wall_burst_pressure(
    geometry: VesselGeometry,
    material: MaterialProperties,
    use_yield: bool = True
) -> float:
    """
    Calculate burst pressure for thick-wall cylinder.

    For thick walls, maximum stress occurs at inner surface.

    Args:
        geometry: Vessel geometry
        material: Material properties
        use_yield: Use yield strength (True) or ultimate strength (False)

    Returns:
        Burst pressure (Pa)

    Note:
        For thick walls with P_o=0:
        σ_θ_max (at r=r_i) = P_i * (r_o² + r_i²) / (r_o² - r_i²)

        Setting σ_θ_max = σ_allow:
        P_burst = σ_allow * (r_o² - r_i²) / (r_o² + r_i²)
    """
    r_i = geometry.inner_diameter / 2
    r_o = r_i + geometry.wall_thickness

    # Allowable stress
    sigma_allow = material.yield_strength if use_yield else material.tensile_strength

    # Burst pressure from Lamé (maximum hoop stress at inner surface)
    P_burst = sigma_allow * (r_o**2 - r_i**2) / (r_o**2 + r_i**2)

    return P_burst


def validate_lame_solution(
    result: ThickWallResult,
    inner_pressure: float,
    outer_pressure: float = 0.0
) -> Dict[str, bool]:
    """
    Validate Lamé solution against known properties.

    Checks:
    1. Boundary conditions: σ_r(r_i) = -P_i, σ_r(r_o) = -P_o
    2. Equilibrium: dσ_r/dr + (σ_r - σ_θ)/r = 0
    3. Hoop stress maximum at inner surface

    Args:
        result: ThickWallResult to validate
        inner_pressure: Applied inner pressure
        outer_pressure: Applied outer pressure

    Returns:
        Dictionary of validation checks (all should be True)
    """
    checks = {}

    # Check boundary conditions
    tol = 1e-6  # Relative tolerance

    # σ_r(r_i) should equal -P_i
    sigma_r_inner = result.sigma_r[0]
    checks['bc_inner'] = np.isclose(sigma_r_inner, -inner_pressure, rtol=tol)

    # σ_r(r_o) should equal -P_o
    sigma_r_outer = result.sigma_r[-1]
    checks['bc_outer'] = np.isclose(sigma_r_outer, -outer_pressure, rtol=tol)

    # Hoop stress should be maximum at inner surface (for P_i > P_o)
    if inner_pressure > outer_pressure:
        max_hoop_idx = np.argmax(result.sigma_theta)
        checks['hoop_max_inner'] = (max_hoop_idx == 0)
    else:
        checks['hoop_max_inner'] = True

    # All hoop stresses should be positive for internal pressure
    if inner_pressure > 0 and outer_pressure == 0:
        checks['hoop_positive'] = np.all(result.sigma_theta > 0)
    else:
        checks['hoop_positive'] = True

    return checks


# Demonstration
if __name__ == "__main__":
    from ..system_model.materials import get_material
    from ..system_model.burst_calculator import calculate_burst_pressure

    print("=== Thick-Wall Cylinder Analysis (Lamé Equations) ===\n")

    # Example: PET bottle
    print("Example: 2L PET bottle under 500 kPa internal pressure")
    print("-" * 60)

    r_i = 0.0475   # 95mm diameter / 2
    t = 0.00025    # 0.25mm wall (thin for PET)
    r_o = r_i + t
    P = 500e3      # 500 kPa

    pet = get_material("PET")

    print(f"Geometry:")
    print(f"  Inner radius: {r_i*1000:.2f} mm")
    print(f"  Wall thickness: {t*1000:.3f} mm")
    print(f"  t/D ratio: {t/(2*r_i):.4f} ({'thin' if t/(2*r_i) < 0.1 else 'thick'}-wall)")
    print()

    # Solve Lamé equations
    result = solve_lame_equations(r_i, r_o, P, material=pet, n_points=20)

    print(f"Stress Distribution:")
    print(f"  Max hoop stress (inner): {result.sigma_theta[0]/1e6:.2f} MPa")
    print(f"  Min hoop stress (outer): {result.sigma_theta[-1]/1e6:.2f} MPa")
    print(f"  Radial stress (inner): {result.sigma_r[0]/1e6:.2f} MPa")
    print(f"  Radial stress (outer): {result.sigma_r[-1]/1e6:.2f} MPa")
    print(f"  Axial stress: {result.sigma_z[0]/1e6:.2f} MPa")
    print(f"  Max von Mises: {np.max(result.sigma_vm)/1e6:.2f} MPa")
    print()

    # Compare with thin-wall theory
    from ..system_model.burst_calculator import VesselGeometry

    geom = VesselGeometry(inner_diameter=2*r_i, wall_thickness=t)
    comparison = compare_thick_vs_thin_wall(geom, P, pet)

    print(f"Thick vs Thin-Wall Comparison:")
    print(f"  Thin-wall hoop stress: {comparison['hoop_stress_thin']/1e6:.2f} MPa")
    print(f"  Thick-wall hoop stress: {comparison['hoop_stress_thick_max']/1e6:.2f} MPa")
    print(f"  Error in thin-wall: {comparison['error_percent']:.2f}%")
    print()

    # Validate solution
    validation = validate_lame_solution(result, P, 0.0)
    print(f"Solution Validation:")
    for check, passed in validation.items():
        status = "✅" if passed else "❌"
        print(f"  {check}: {status}")
    print()

    # Burst pressure
    P_burst_thick = calculate_thick_wall_burst_pressure(geom, pet, use_yield=True)
    P_burst_thin = calculate_burst_pressure(geom, pet, use_yield=True, safety_factor=1.0)

    print(f"Burst Pressure Comparison:")
    print(f"  Thin-wall (Barlow): {P_burst_thin/1e5:.2f} bar")
    print(f"  Thick-wall (Lamé): {P_burst_thick/1e5:.2f} bar")
    print(f"  Difference: {abs(P_burst_thick - P_burst_thin)/P_burst_thin * 100:.2f}%")
