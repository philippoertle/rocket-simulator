"""
PET Rocket Simulator Package
ISO/IEC/IEEE 12207:2017 Compliant Development

A safety-focused simulation framework to predict and prevent catastrophic
structural failure in experimental PET bottle hydrogen/oxygen rockets.

Modules:
    - combustion: Thermochemistry calculations using Cantera
    - system_model: System dynamics and ODE modeling
    - fem: Structural FEM analysis using CalculiX
    - utils: Shared utilities and helpers
"""

__version__ = "0.1.0"
__author__ = "PET Rocket Safety Project"
__license__ = "MIT"

from rocket_sim import combustion, system_model, fem, utils

__all__ = ["combustion", "system_model", "fem", "utils"]
