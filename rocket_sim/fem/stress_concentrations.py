"""
Stress Concentration Factors for Pressure Vessels

This module calculates stress concentration factors for geometric
discontinuities in pressure vessels (end caps, necks, threads, etc.)

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-4 (FEM stress analysis), NFR-9 (Safety warnings)
"""

import numpy as np
from typing import Dict, Optional
import warnings

from ..system_model.burst_calculator import VesselGeometry, calculate_stress_state
from ..system_model.materials import MaterialProperties


def calculate_end_cap_stress_factor(
    geometry: VesselGeometry,
    cap_type: str = "hemispherical"
) -> float:
    """
    Calculate stress concentration factor for end cap geometry.

    Stress concentration factor K_t relates local maximum stress to
    nominal stress: σ_max = K_t * σ_nominal

    Args:
        geometry: Vessel geometry
        cap_type: End cap type:
                  - "hemispherical": Ideal hemispherical cap (K ≈ 1.0)
                  - "elliptical": Elliptical cap with 2:1 ratio (K ≈ 1.5)
                  - "torispherical": Torispherical (ASME) cap (K ≈ 1.8)
                  - "flat": Flat end cap (K ≈ 2.0-3.0)
                  - "conical": Conical cap, 60° (K ≈ 1.5)

    Returns:
        Stress concentration factor K_t

    Reference:
        Roark's Formulas for Stress and Strain, 8th Ed.
        Peterson's Stress Concentration Factors

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        >>> K_hemi = calculate_end_cap_stress_factor(geom, "hemispherical")
        >>> K_flat = calculate_end_cap_stress_factor(geom, "flat")
        >>> print(f"Hemispherical: K={K_hemi:.2f}, Flat: K={K_flat:.2f}")
    """
    cap_factors = {
        "hemispherical": 1.0,    # Ideal - membrane stress only
        "elliptical": 1.5,       # 2:1 elliptical head
        "torispherical": 1.8,    # ASME F&D head
        "conical": 1.5,          # 60-degree cone
        "flat": 2.5,             # Flat plate - high bending stress
    }

    cap_type_lower = cap_type.lower()

    if cap_type_lower not in cap_factors:
        available = ", ".join(cap_factors.keys())
        raise ValueError(
            f"Unknown cap type '{cap_type}'. "
            f"Available: {available}"
        )

    K_t = cap_factors[cap_type_lower]

    # Add warning for flat caps
    if cap_type_lower == "flat":
        warnings.warn(
            "Flat end caps have high stress concentrations (K≈2.5). "
            "Consider hemispherical or elliptical caps for safety.",
            UserWarning
        )

    return K_t


def calculate_thread_stress_factor(
    geometry: VesselGeometry,
    thread_depth: Optional[float] = None,
    thread_radius: Optional[float] = None
) -> float:
    """
    Calculate stress concentration factor for threaded neck/closure.

    Threads create significant stress concentrations, especially
    in brittle materials like PET.

    Args:
        geometry: Vessel geometry
        thread_depth: Thread depth (m), default to wall_thickness/2
        thread_radius: Root radius (m), default to thread_depth/4

    Returns:
        Stress concentration factor K_t

    Reference:
        Peterson's Stress Concentration Factors, Fig. 4.72-4.74
        For threads in pressure vessels, K_t ≈ 2.5-4.0 typical

    Note:
        Actual K_t depends on thread geometry, pitch, root radius.
        This gives conservative estimate.
    """
    # Estimate thread geometry if not provided
    if thread_depth is None:
        thread_depth = geometry.wall_thickness / 2

    if thread_radius is None:
        thread_radius = thread_depth / 4  # Sharp threads

    # Normalized parameters
    t = geometry.wall_thickness
    h = thread_depth
    r = thread_radius

    # Peterson's formula (simplified)
    # K_t ≈ 1 + 2*sqrt(h/r) for sharp notches
    if r > 0:
        K_t = 1 + 2 * np.sqrt(h / r)
    else:
        K_t = 4.0  # Very sharp thread - conservative

    # Clamp to realistic range
    K_t = np.clip(K_t, 2.0, 4.5)

    return K_t


def calculate_transition_radius_factor(
    major_diameter: float,
    minor_diameter: float,
    fillet_radius: float
) -> float:
    """
    Calculate stress concentration for diameter transition with fillet.

    Common at bottle neck-to-body transition.

    Args:
        major_diameter: Larger diameter (m)
        minor_diameter: Smaller diameter (m)
        fillet_radius: Transition fillet radius (m)

    Returns:
        Stress concentration factor K_t

    Reference:
        Peterson's Stress Concentration Factors, Chart 2.2
    """
    # Diameter ratio
    d_ratio = minor_diameter / major_diameter

    # Fillet radius ratio
    r_ratio = fillet_radius / minor_diameter

    # Peterson's chart approximation (for tension)
    # K_t ≈ 1 + 0.5/(r_ratio) for step in diameter
    if r_ratio > 0:
        K_t = 1 + 0.5 / np.sqrt(r_ratio)
    else:
        K_t = 3.0  # Sharp corner

    # Adjust for diameter ratio
    K_t *= (1 + (1 - d_ratio))

    # Clamp to reasonable range
    K_t = np.clip(K_t, 1.0, 3.5)

    return K_t


def calculate_maximum_stress(
    pressure: float,
    geometry: VesselGeometry,
    material: MaterialProperties,
    cap_type: str = "hemispherical",
    include_thread: bool = False,
    include_transition: bool = False
) -> Dict[str, float]:
    """
    Calculate maximum stress including all stress concentrations.

    Args:
        pressure: Internal pressure (Pa)
        geometry: Vessel geometry
        material: Material properties
        cap_type: End cap type
        include_thread: Include thread stress concentration
        include_transition: Include neck transition stress concentration

    Returns:
        Dictionary with stresses:
        - sigma_nominal: Nominal hoop stress (Pa)
        - K_cap: End cap stress factor
        - K_thread: Thread stress factor (if included)
        - K_transition: Transition stress factor (if included)
        - K_total: Combined stress factor
        - sigma_max: Maximum stress (Pa)
        - location: Critical location

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        >>> pet = get_material("PET")
        >>> result = calculate_maximum_stress(
        ...     pressure=500e3,
        ...     geometry=geom,
        ...     material=pet,
        ...     cap_type="flat",
        ...     include_thread=True
        ... )
        >>> print(f"Max stress: {result['sigma_max']/1e6:.1f} MPa at {result['location']}")
    """
    # Nominal stress (thin-wall hoop stress)
    stress_state = calculate_stress_state(pressure, geometry)
    sigma_nominal = stress_state.hoop_stress

    # Calculate individual stress concentration factors
    K_cap = calculate_end_cap_stress_factor(geometry, cap_type)

    K_thread = 1.0
    if include_thread:
        K_thread = calculate_thread_stress_factor(geometry)

    K_transition = 1.0
    if include_transition:
        # Assume typical bottle: 28mm neck, 95mm body, 5mm radius
        K_transition = calculate_transition_radius_factor(
            major_diameter=geometry.inner_diameter,
            minor_diameter=0.028,  # Typical bottle neck
            fillet_radius=0.005    # 5mm radius
        )

    # Combined stress concentration factor
    # Note: Factors don't simply multiply - we take maximum
    # since different features are at different locations
    stress_concentrations = {
        'cap': (K_cap, "End cap"),
        'thread': (K_thread, "Thread root"),
        'transition': (K_transition, "Neck transition")
    }

    # Find maximum stress concentration
    max_K = max(K_cap, K_thread, K_transition)
    location = stress_concentrations[
        max(['cap', 'thread', 'transition'],
            key=lambda x: stress_concentrations[x][0])
    ][1]

    # Maximum stress
    sigma_max = max_K * sigma_nominal

    return {
        'sigma_nominal': sigma_nominal,
        'K_cap': K_cap,
        'K_thread': K_thread if include_thread else None,
        'K_transition': K_transition if include_transition else None,
        'K_total': max_K,
        'sigma_max': sigma_max,
        'location': location
    }


def estimate_failure_location(
    pressure: float,
    geometry: VesselGeometry,
    cap_type: str = "hemispherical"
) -> str:
    """
    Estimate most likely failure location based on stress concentrations.

    Args:
        pressure: Internal pressure (Pa)
        geometry: Vessel geometry
        cap_type: End cap type

    Returns:
        String describing likely failure location

    Example:
        >>> geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        >>> location = estimate_failure_location(800e3, geom, "flat")
        >>> print(f"Expected failure: {location}")
    """
    K_cap = calculate_end_cap_stress_factor(geometry, cap_type)
    K_thread = calculate_thread_stress_factor(geometry)
    K_body = 1.0  # Cylindrical section (baseline)

    # Find maximum
    max_K = max(K_cap, K_thread, K_body)

    if max_K == K_thread:
        return "Thread root (thread stress concentration)"
    elif max_K == K_cap and K_cap > 1.5:
        return f"End cap ({cap_type}, stress concentration)"
    else:
        return "Cylindrical body (uniform stress)"


# Demonstration
if __name__ == "__main__":
    from ..system_model.materials import get_material
    from ..system_model.burst_calculator import VesselGeometry

    print("=== Stress Concentration Factors ===\n")

    # Example: PET bottle
    print("Example: 2L PET bottle at 600 kPa")
    print("-" * 60)

    geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
    pet = get_material("PET")
    P = 600e3  # 600 kPa

    print(f"Stress Concentration Factors:")
    print(f"  Hemispherical cap: K = {calculate_end_cap_stress_factor(geom, 'hemispherical'):.2f}")
    print(f"  Elliptical cap: K = {calculate_end_cap_stress_factor(geom, 'elliptical'):.2f}")
    print(f"  Flat cap: K = {calculate_end_cap_stress_factor(geom, 'flat'):.2f}")
    print(f"  Threads: K = {calculate_thread_stress_factor(geom):.2f}")
    print()

    # Maximum stress analysis
    print("Maximum Stress Analysis:")
    print()

    for cap in ["hemispherical", "flat"]:
        result = calculate_maximum_stress(P, geom, pet, cap_type=cap, include_thread=True)
        print(f"{cap.capitalize()} cap:")
        print(f"  Nominal stress: {result['sigma_nominal']/1e6:.1f} MPa")
        print(f"  Stress factor (cap): {result['K_cap']:.2f}")
        print(f"  Stress factor (thread): {result['K_thread']:.2f}")
        print(f"  Total stress factor: {result['K_total']:.2f}")
        print(f"  Maximum stress: {result['sigma_max']/1e6:.1f} MPa")
        print(f"  Critical location: {result['location']}")
        print(f"  Safety factor: {pet.yield_strength / result['sigma_max']:.2f}")
        print()

    # Failure prediction
    print("Failure Location Prediction:")
    for cap in ["hemispherical", "elliptical", "flat"]:
        location = estimate_failure_location(P, geom, cap)
        print(f"  {cap.capitalize()} cap: {location}")
