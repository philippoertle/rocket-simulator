"""
Combustion Module - Module 1
ISO 12207:2017 §6.4.7 Implementation Process

Purpose:
    Compute constant-volume combustion of H₂/O₂ using Cantera and output:
    - Pressure vs time
    - Temperature vs time
    - Maximum pressure
    - Pressure rise rate
    - Heat release rate

Requirements Traceability:
    - FR-1: Compute H₂/O₂ combustion P(t), T(t) using validated chemistry
    - NFR-1: Python 3.11+
    - NFR-2: Open-source dependencies (Cantera)
"""

__version__ = "0.1.0"

from rocket_sim.combustion.cantera_wrapper import (
    simulate_combustion,
    CombustionResult,
    validate_combustion_inputs
)

__all__ = [
    "simulate_combustion",
    "CombustionResult",
    "validate_combustion_inputs"
]
