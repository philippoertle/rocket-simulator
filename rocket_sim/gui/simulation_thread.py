"""
Background simulation thread for GUI.

This module provides a QThread subclass to run simulations
in the background without freezing the GUI.
"""

from PySide6.QtCore import QThread, Signal
import time
from rocket_sim.integration.full_simulation import (
    FullSimulationConfig,
    run_complete_simulation
)


class SimulationThread(QThread):
    """Background thread for running simulations."""

    # Signals
    progress_updated = Signal(int, str)  # percentage, message
    simulation_complete = Signal(object, float)  # result, elapsed_time
    simulation_failed = Signal(str)  # error message

    def __init__(self, config_dict: dict, parent=None):
        """
        Initialize simulation thread.

        Args:
            config_dict: Configuration dictionary from ConfigurationWidget
            parent: Parent QObject
        """
        super().__init__(parent)
        self.config_dict = config_dict
        self._is_cancelled = False

    def run(self):
        """Run the simulation (executed in background thread)."""
        try:
            start_time = time.time()

            # Create configuration
            self.progress_updated.emit(5, "Creating configuration...")
            config = FullSimulationConfig(**self.config_dict)

            # Run simulation with progress updates
            self.progress_updated.emit(10, "Starting combustion simulation...")

            # Note: We can't easily get progress from run_complete_simulation
            # since it's not designed for callbacks. For now, we'll just show
            # indeterminate progress and emit updates at logical points.

            # Run the complete simulation
            result = run_complete_simulation(config, verbose=False)

            self.progress_updated.emit(100, "Complete")

            elapsed_time = time.time() - start_time
            self.simulation_complete.emit(result, elapsed_time)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.simulation_failed.emit(error_msg)

    def cancel(self):
        """Request cancellation of the simulation."""
        self._is_cancelled = True
        # Note: Actual cancellation is not implemented in v1
        # Would require modifying simulation code to check cancellation flag
