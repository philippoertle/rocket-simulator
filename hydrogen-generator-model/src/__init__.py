"""
Hydrogen Generator Efficiency Model

A comprehensive chemical and physical model for analyzing hydrogen production
efficiency in DIY electrolysis-based hydrogen generators.
"""

__version__ = "1.0.0"
__author__ = "philippoertle"

from .chemical_model import ChemicalModel
from .physical_model import PhysicalModel, ElectrodeConfig
from .integrated_model import HydrogenGeneratorModel
from .generator_configs import (
    GeneratorConfig,
    get_config,
    list_configs,
    print_config_summary,
    GENERATOR_CONFIGS,
    PARAMETER_RANGES,
    ELECTRODE_MATERIALS
)

__all__ = [
    'ChemicalModel',
    'PhysicalModel',
    'ElectrodeConfig',
    'HydrogenGeneratorModel',
    'GeneratorConfig',
    'get_config',
    'list_configs',
    'print_config_summary',
    'GENERATOR_CONFIGS',
    'PARAMETER_RANGES',
    'ELECTRODE_MATERIALS',
]
