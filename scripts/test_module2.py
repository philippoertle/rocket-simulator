"""Quick test of Module 2 functionality"""

import sys
sys.path.insert(0, '.')

from rocket_sim.system_model.materials import get_material, list_available_materials
from rocket_sim.system_model.burst_calculator import (
    VesselGeometry, calculate_burst_pressure, calculate_safety_factor
)

print("=== Testing Module 2 ===\n")

# Test materials
print("Available materials:", list_available_materials())
pet = get_material("PET")
print(f"\nPET yield strength: {pet.yield_strength/1e6:.1f} MPa")

# Test burst calculator
bottle = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
P_burst = calculate_burst_pressure(bottle, pet)
print(f"Burst pressure: {P_burst/1e5:.1f} bar")

SF = calculate_safety_factor(500e3, bottle, pet)
print(f"Safety factor at 500 kPa: {SF:.2f}")

print("\n✅ Module 2 working!")
