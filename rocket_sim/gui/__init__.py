"""
GUI Module for PET Rocket Simulator

This module provides a graphical user interface for the rocket simulator,
allowing non-programmers to run simulations without writing code.

Features:
- Configuration through form fields
- One-click simulation execution
- Integrated visualization
- Export results and plots

Usage:
    python -m rocket_sim.gui

    Or if installed with entry point:
    rocket-sim-gui
"""

__version__ = "0.1.0"
__author__ = "PET Rocket Simulator Team"

from rocket_sim.gui.main_window import MainWindow

__all__ = ["MainWindow"]
