"""
Material Properties Database for Pressure Vessel Analysis

This module provides material property data for common pressure vessel materials
used in amateur rocketry, including PET bottles, HDPE containers, and metals.

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-3 (Analytical burst calculator), NFR-9 (Safety warnings)
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class MaterialProperties:
    """
    Material properties for structural analysis.

    Attributes:
        name: Material name/identifier
        yield_strength: Yield strength (Pa) - stress at permanent deformation
        tensile_strength: Ultimate tensile strength (Pa) - stress at failure
        elastic_modulus: Young's modulus (Pa) - stiffness
        poisson_ratio: Poisson's ratio (dimensionless) - lateral strain ratio
        density: Material density (kg/m³)
        max_temperature: Maximum service temperature (K)
        source: Reference for material properties
    """
    name: str
    yield_strength: float      # Pa
    tensile_strength: float    # Pa
    elastic_modulus: float     # Pa
    poisson_ratio: float       # dimensionless
    density: float             # kg/m³
    max_temperature: float     # K
    source: str


# Material database
# Values are conservative estimates from literature
MATERIALS: Dict[str, MaterialProperties] = {
    "PET": MaterialProperties(
        name="Polyethylene Terephthalate (PET)",
        yield_strength=55e6,        # 55 MPa (conservative)
        tensile_strength=70e6,      # 70 MPa
        elastic_modulus=2.8e9,      # 2.8 GPa
        poisson_ratio=0.38,
        density=1380.0,             # kg/m³
        max_temperature=343.15,     # 70°C (glass transition ~80°C)
        source="Osswald et al., Materials Science of Polymers (2012)"
    ),

    "HDPE": MaterialProperties(
        name="High-Density Polyethylene (HDPE)",
        yield_strength=26e6,        # 26 MPa (conservative)
        tensile_strength=37e6,      # 37 MPa
        elastic_modulus=1.1e9,      # 1.1 GPa
        poisson_ratio=0.42,
        density=960.0,              # kg/m³
        max_temperature=353.15,     # 80°C (melting ~130°C)
        source="ASTM D638 standard testing data"
    ),

    "PP": MaterialProperties(
        name="Polypropylene (PP)",
        yield_strength=32e6,        # 32 MPa
        tensile_strength=38e6,      # 38 MPa
        elastic_modulus=1.6e9,      # 1.6 GPa
        poisson_ratio=0.40,
        density=905.0,              # kg/m³
        max_temperature=373.15,     # 100°C (melting ~165°C)
        source="MatWeb polymer database"
    ),

    "Aluminum_6061_T6": MaterialProperties(
        name="Aluminum 6061-T6",
        yield_strength=276e6,       # 276 MPa
        tensile_strength=310e6,     # 310 MPa
        elastic_modulus=68.9e9,     # 68.9 GPa
        poisson_ratio=0.33,
        density=2700.0,             # kg/m³
        max_temperature=473.15,     # 200°C (before annealing)
        source="ASM Metals Handbook"
    ),

    "Steel_304": MaterialProperties(
        name="Stainless Steel 304",
        yield_strength=215e6,       # 215 MPa (annealed)
        tensile_strength=505e6,     # 505 MPa
        elastic_modulus=193e9,      # 193 GPa
        poisson_ratio=0.29,
        density=8000.0,             # kg/m³
        max_temperature=923.15,     # 650°C (continuous service)
        source="ASTM A240 specification"
    ),
}


def get_material(name: str) -> MaterialProperties:
    """
    Retrieve material properties by name.

    Args:
        name: Material identifier (case-insensitive)
              Available: "PET", "HDPE", "PP", "Aluminum_6061_T6", "Steel_304"

    Returns:
        MaterialProperties object

    Raises:
        ValueError: If material not found in database

    Example:
        >>> pet = get_material("PET")
        >>> print(f"Yield strength: {pet.yield_strength/1e6:.1f} MPa")
        Yield strength: 55.0 MPa
    """
    # Normalize material name
    normalized = name.strip().replace(" ", "_").replace("-", "_")

    # Try exact match first
    if normalized in MATERIALS:
        return MATERIALS[normalized]

    # Try case-insensitive match
    for key in MATERIALS:
        if key.lower() == normalized.lower():
            return MATERIALS[key]

    # Material not found
    available = ", ".join(MATERIALS.keys())
    raise ValueError(
        f"Material '{name}' not found in database. "
        f"Available materials: {available}"
    )


def list_available_materials() -> list[str]:
    """
    List all available materials in the database.

    Returns:
        List of material names

    Example:
        >>> materials = list_available_materials()
        >>> print(materials)
        ['PET', 'HDPE', 'PP', 'Aluminum_6061_T6', 'Steel_304']
    """
    return list(MATERIALS.keys())


def get_material_summary(name: str) -> str:
    """
    Get a human-readable summary of material properties.

    Args:
        name: Material identifier

    Returns:
        Formatted string with key properties

    Example:
        >>> print(get_material_summary("PET"))
        Material: Polyethylene Terephthalate (PET)
        Yield Strength: 55.0 MPa
        ...
    """
    mat = get_material(name)

    return f"""Material: {mat.name}
Yield Strength: {mat.yield_strength/1e6:.1f} MPa
Tensile Strength: {mat.tensile_strength/1e6:.1f} MPa
Elastic Modulus: {mat.elastic_modulus/1e9:.1f} GPa
Poisson Ratio: {mat.poisson_ratio:.2f}
Density: {mat.density:.1f} kg/m³
Max Temperature: {mat.max_temperature:.1f} K ({mat.max_temperature-273.15:.1f} °C)
Source: {mat.source}"""


# Convenience function for common bottle materials
def get_bottle_material(bottle_type: str = "soda") -> MaterialProperties:
    """
    Get material properties for common bottle types.

    Args:
        bottle_type: "soda" (PET), "milk" (HDPE), or "detergent" (HDPE)

    Returns:
        MaterialProperties for the bottle material

    Example:
        >>> soda_bottle = get_bottle_material("soda")
        >>> print(soda_bottle.name)
        Polyethylene Terephthalate (PET)
    """
    bottle_map = {
        "soda": "PET",
        "water": "PET",
        "cola": "PET",
        "milk": "HDPE",
        "detergent": "HDPE",
        "shampoo": "HDPE",
    }

    material_name = bottle_map.get(bottle_type.lower())
    if material_name is None:
        available = ", ".join(bottle_map.keys())
        raise ValueError(
            f"Unknown bottle type '{bottle_type}'. "
            f"Available: {available}"
        )

    return get_material(material_name)


if __name__ == "__main__":
    # Demonstration
    print("=== Material Properties Database ===\n")

    print("Available materials:")
    for mat_name in list_available_materials():
        print(f"  - {mat_name}")

    print("\n" + "="*50 + "\n")

    print(get_material_summary("PET"))
    print("\n" + "="*50 + "\n")

    print(get_material_summary("Aluminum_6061_T6"))
    print("\n" + "="*50 + "\n")

    # Common bottle example
    soda = get_bottle_material("soda")
    print(f"Soda bottle material: {soda.name}")
    print(f"Yield strength: {soda.yield_strength/1e6:.1f} MPa")
