"""
Analytical Burst Pressure Calculator for Cylindrical Pressure Vessels

This module implements thin-wall pressure vessel theory to calculate:
- Burst pressure (Barlow's formula)
- Hoop and axial stresses
- Von Mises equivalent stress
- Safety factors

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-3 (Analytical burst calculator), NFR-9 (Safety warnings)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import warnings

from .materials import MaterialProperties, get_material


@dataclass
class VesselGeometry:
    """
    Cylindrical pressure vessel geometry.

    Attributes:
        inner_diameter: Inner diameter (m)
        wall_thickness: Wall thickness (m)
        length: Cylindrical length (m), optional for stress calculations
    """
    inner_diameter: float  # m
    wall_thickness: float  # m
    length: Optional[float] = None  # m


@dataclass
class StressState:
    """
    Stress state in a pressure vessel.

    Attributes:
        hoop_stress: Circumferential stress (Pa)
        axial_stress: Longitudinal stress (Pa)
        radial_stress: Radial stress (Pa), usually ~0 for thin walls
        von_mises_stress: Von Mises equivalent stress (Pa)
    """
    hoop_stress: float      # Pa
    axial_stress: float     # Pa
    radial_stress: float    # Pa
    von_mises_stress: float # Pa


def validate_thin_wall_assumption(geometry: VesselGeometry,
                                   threshold: float = 0.1) -> None:
    """
    Validate that thin-wall theory is applicable.

    Thin-wall assumption valid when: t/D < 0.1

    Args:
        geometry: Vessel geometry
        threshold: Maximum thickness/diameter ratio (default 0.1)

    Raises:
        ValueError: If thin-wall assumption violated

    Warning:
        Issues warning if ratio > 0.05 (marginal)
    """
    ratio = geometry.wall_thickness / geometry.inner_diameter

    if ratio > threshold:
        raise ValueError(
            f"Thin-wall assumption violated: t/D = {ratio:.3f} > {threshold}. "
            f"Use thick-wall theory (Lamé equations) instead."
        )

    if ratio > 0.05:
        warnings.warn(
            f"Thin-wall assumption marginal: t/D = {ratio:.3f}. "
            f"Results may have ~{(ratio-0.05)*100:.1f}% error.",
            UserWarning
        )


def calculate_hoop_stress(pressure: float, geometry: VesselGeometry) -> float:
    """
    Calculate circumferential (hoop) stress in a thin-wall cylinder.

    Formula: σ_hoop = P * D / (2 * t)

    This is the maximum principal stress in a cylindrical pressure vessel.

    Args:
        pressure: Internal pressure (Pa)
        geometry: Vessel geometry

    Returns:
        Hoop stress (Pa)

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.085, wall_thickness=0.0003)
        >>> stress = calculate_hoop_stress(500e3, geom)  # 500 kPa
        >>> print(f"{stress/1e6:.1f} MPa")
        70.8 MPa
    """
    validate_thin_wall_assumption(geometry)

    D = geometry.inner_diameter
    t = geometry.wall_thickness

    sigma_hoop = pressure * D / (2 * t)
    return sigma_hoop


def calculate_axial_stress(pressure: float, geometry: VesselGeometry) -> float:
    """
    Calculate longitudinal (axial) stress in a thin-wall cylinder with closed ends.

    Formula: σ_axial = P * D / (4 * t)

    Note: This is exactly half the hoop stress for a capped cylinder.

    Args:
        pressure: Internal pressure (Pa)
        geometry: Vessel geometry

    Returns:
        Axial stress (Pa)

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.085, wall_thickness=0.0003)
        >>> stress = calculate_axial_stress(500e3, geom)
        >>> print(f"{stress/1e6:.1f} MPa")
        35.4 MPa
    """
    validate_thin_wall_assumption(geometry)

    D = geometry.inner_diameter
    t = geometry.wall_thickness

    sigma_axial = pressure * D / (4 * t)
    return sigma_axial


def calculate_von_mises_stress(hoop_stress: float,
                                 axial_stress: float,
                                 radial_stress: float = 0.0) -> float:
    """
    Calculate von Mises equivalent stress for 3D stress state.

    Formula: σ_vm = √[(σ₁-σ₂)² + (σ₂-σ₃)² + (σ₃-σ₁)²] / √2

    For thin-wall vessels: σ_vm ≈ √(σ_hoop² - σ_hoop*σ_axial + σ_axial²)

    Von Mises stress is used for ductile material failure prediction.

    Args:
        hoop_stress: Hoop stress (Pa)
        axial_stress: Axial stress (Pa)
        radial_stress: Radial stress (Pa), ~0 for thin walls

    Returns:
        Von Mises equivalent stress (Pa)
    """
    # Principal stresses
    sigma_1 = hoop_stress
    sigma_2 = axial_stress
    sigma_3 = radial_stress

    # Von Mises formula
    sigma_vm = np.sqrt(
        ((sigma_1 - sigma_2)**2 +
         (sigma_2 - sigma_3)**2 +
         (sigma_3 - sigma_1)**2) / 2
    )

    return sigma_vm


def calculate_stress_state(pressure: float,
                           geometry: VesselGeometry) -> StressState:
    """
    Calculate complete stress state in a pressure vessel.

    Args:
        pressure: Internal pressure (Pa)
        geometry: Vessel geometry

    Returns:
        StressState object with all stress components

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.085, wall_thickness=0.0003)
        >>> state = calculate_stress_state(500e3, geom)
        >>> print(f"Hoop: {state.hoop_stress/1e6:.1f} MPa")
        >>> print(f"Von Mises: {state.von_mises_stress/1e6:.1f} MPa")
    """
    sigma_hoop = calculate_hoop_stress(pressure, geometry)
    sigma_axial = calculate_axial_stress(pressure, geometry)
    sigma_radial = 0.0  # Thin-wall assumption
    sigma_vm = calculate_von_mises_stress(sigma_hoop, sigma_axial, sigma_radial)

    return StressState(
        hoop_stress=sigma_hoop,
        axial_stress=sigma_axial,
        radial_stress=sigma_radial,
        von_mises_stress=sigma_vm
    )


def calculate_burst_pressure(geometry: VesselGeometry,
                             material: MaterialProperties,
                             use_yield: bool = True,
                             safety_factor: float = 1.0) -> float:
    """
    Calculate theoretical burst pressure using Barlow's formula.

    Formula: P_burst = 2 * σ_allow * t / D

    where σ_allow is either yield strength (conservative) or
    tensile strength (ultimate failure).

    Args:
        geometry: Vessel geometry
        material: Material properties
        use_yield: If True, use yield strength (conservative).
                  If False, use tensile strength (ultimate).
        safety_factor: Safety factor to apply (default 1.0)
                      P_burst_safe = P_burst / safety_factor

    Returns:
        Burst pressure (Pa)

    Example:
        >>> from materials import get_material
        >>> geom = VesselGeometry(inner_diameter=0.085, wall_thickness=0.0003)
        >>> pet = get_material("PET")
        >>> P_burst = calculate_burst_pressure(geom, pet)
        >>> print(f"Burst pressure: {P_burst/1e5:.1f} bar")
        Burst pressure: 7.8 bar
    """
    validate_thin_wall_assumption(geometry)

    D = geometry.inner_diameter
    t = geometry.wall_thickness

    # Choose allowable stress
    if use_yield:
        sigma_allow = material.yield_strength
    else:
        sigma_allow = material.tensile_strength

    # Barlow's formula
    P_burst = 2 * sigma_allow * t / D

    # Apply safety factor
    P_burst_safe = P_burst / safety_factor

    return P_burst_safe


def calculate_safety_factor(pressure: float,
                            geometry: VesselGeometry,
                            material: MaterialProperties,
                            criterion: str = "yield") -> float:
    """
    Calculate safety factor against failure.

    SF = σ_allowable / σ_actual

    Args:
        pressure: Current internal pressure (Pa)
        geometry: Vessel geometry
        material: Material properties
        criterion: "yield" or "ultimate" failure criterion

    Returns:
        Safety factor (dimensionless)
        SF > 1: Safe
        SF = 1: At failure threshold
        SF < 1: Failed

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.085, wall_thickness=0.0003)
        >>> pet = get_material("PET")
        >>> SF = calculate_safety_factor(400e3, geom, pet)  # 400 kPa
        >>> print(f"Safety factor: {SF:.2f}")
        Safety factor: 1.94
    """
    # Calculate actual stress state
    stress_state = calculate_stress_state(pressure, geometry)
    sigma_actual = stress_state.von_mises_stress

    # Get allowable stress
    if criterion.lower() == "yield":
        sigma_allow = material.yield_strength
    elif criterion.lower() == "ultimate":
        sigma_allow = material.tensile_strength
    else:
        raise ValueError(f"Unknown criterion '{criterion}'. Use 'yield' or 'ultimate'.")

    # Safety factor
    if sigma_actual > 0:
        SF = sigma_allow / sigma_actual
    else:
        SF = np.inf

    return SF


def check_failure(pressure: float,
                 geometry: VesselGeometry,
                 material: MaterialProperties,
                 criterion: str = "yield") -> Tuple[bool, float]:
    """
    Check if vessel has failed under given pressure.

    Args:
        pressure: Internal pressure (Pa)
        geometry: Vessel geometry
        material: Material properties
        criterion: "yield" (conservative) or "ultimate" (catastrophic)

    Returns:
        (failed: bool, safety_factor: float)

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.085, wall_thickness=0.0003)
        >>> pet = get_material("PET")
        >>> failed, SF = check_failure(800e3, geom, pet)
        >>> if failed:
        ...     print("FAILURE!")
    """
    SF = calculate_safety_factor(pressure, geometry, material, criterion)
    failed = (SF < 1.0)

    return failed, SF


def predict_failure_pressure(geometry: VesselGeometry,
                             material: MaterialProperties,
                             criterion: str = "yield") -> float:
    """
    Predict the pressure at which vessel will fail.

    This is equivalent to calculate_burst_pressure with safety_factor=1.0.

    Args:
        geometry: Vessel geometry
        material: Material properties
        criterion: "yield" or "ultimate"

    Returns:
        Failure pressure (Pa)
    """
    use_yield = (criterion.lower() == "yield")
    return calculate_burst_pressure(geometry, material, use_yield, safety_factor=1.0)


# Demonstration code
if __name__ == "__main__":
    from .materials import get_material

    print("=== Pressure Vessel Burst Calculator ===\n")

    # Example: 2L soda bottle (typical PET)
    print("Example: 2-liter PET soda bottle")
    print("-" * 50)

    # Geometry (typical 2L bottle)
    bottle = VesselGeometry(
        inner_diameter=0.095,    # 95 mm
        wall_thickness=0.0003,   # 0.3 mm
        length=0.30              # 30 cm
    )

    pet = get_material("PET")

    print(f"Diameter: {bottle.inner_diameter*1000:.1f} mm")
    print(f"Wall thickness: {bottle.wall_thickness*1000:.2f} mm")
    print(f"Material: {pet.name}")
    print(f"Yield strength: {pet.yield_strength/1e6:.1f} MPa\n")

    # Calculate burst pressure
    P_burst_yield = calculate_burst_pressure(bottle, pet, use_yield=True)
    P_burst_ultimate = calculate_burst_pressure(bottle, pet, use_yield=False)

    print(f"Burst pressure (yield): {P_burst_yield/1e5:.1f} bar ({P_burst_yield/1e3:.0f} kPa)")
    print(f"Burst pressure (ultimate): {P_burst_ultimate/1e5:.1f} bar ({P_burst_ultimate/1e3:.0f} kPa)")
    print()

    # Test at various pressures
    test_pressures = [100e3, 300e3, 500e3, 800e3]  # kPa

    print("Safety factors at different pressures:")
    print("-" * 50)
    for P in test_pressures:
        SF = calculate_safety_factor(P, bottle, pet, criterion="yield")
        stress_state = calculate_stress_state(P, bottle)
        failed, _ = check_failure(P, bottle, pet, criterion="yield")

        status = "❌ FAILED" if failed else "✅ Safe"
        print(f"P = {P/1e3:4.0f} kPa: SF = {SF:.2f} | "
              f"σ_vm = {stress_state.von_mises_stress/1e6:5.1f} MPa | {status}")

    print("\n" + "=" * 50)
    print("\n⚠️  WARNING: This is a simplified analytical model.")
    print("Real PET bottles have complex geometry (neck, base)")
    print("and may fail at stress concentrations.")
    print("Literature: PET bottles burst at 800-1200 kPa typically.\n")
