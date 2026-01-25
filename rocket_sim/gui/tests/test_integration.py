"""
Integration tests for GUI.

Tests the complete GUI workflow including simulation execution.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from unittest.mock import MagicMock, patch

from rocket_sim.gui.main_window import MainWindow
from rocket_sim.integration.full_simulation import FullSimulationResult


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_window(qapp):
    """Create MainWindow instance for testing."""
    window = MainWindow()
    return window


class TestMainWindow:
    """Tests for MainWindow."""

    def test_window_creation(self, main_window):
        """Test that main window is created successfully."""
        assert main_window is not None
        assert "PET Rocket Simulator" in main_window.windowTitle()

    def test_has_required_widgets(self, main_window):
        """Test that all required widgets are present."""
        assert main_window.config_widget is not None
        assert main_window.control_widget is not None
        assert main_window.results_widget is not None
        assert main_window.plot_widget is not None

    def test_menu_bar_exists(self, main_window):
        """Test that menu bar is created."""
        menubar = main_window.menuBar()
        assert menubar is not None

        # Check for File and Help menus
        actions = menubar.actions()
        menu_texts = [action.text() for action in actions]
        assert any("File" in text for text in menu_texts)
        assert any("Help" in text for text in menu_texts)

    def test_status_bar_exists(self, main_window):
        """Test that status bar is created."""
        assert main_window.status_bar is not None

    def test_config_widget_integration(self, main_window):
        """Test configuration widget is properly integrated."""
        # Set configuration values
        main_window.config_widget.volume_input.setValue(1.5)
        main_window.config_widget.ratio_input.setValue(2.5)

        config = main_window.config_widget.get_config_dict()
        assert config["volume"] == 0.0015  # 1.5L in m³
        assert config["fuel_oxidizer_ratio"] == 2.5


class TestSimulationWorkflow:
    """Tests for the complete simulation workflow."""

    @pytest.mark.slow
    def test_run_simulation_with_mock(self, main_window, qtbot):
        """Test simulation execution with mocked backend."""
        # Create a mock result
        mock_result = MagicMock(spec=FullSimulationResult)
        mock_result.summary = {
            'peak_pressure': 244000,  # 2.44 bar in Pa
            'peak_temperature': 3369,
            'min_safety_factor': 1.92,
            'max_von_mises_stress': 38.7e6  # MPa in Pa
        }
        mock_result.failed = False
        mock_result.failure_location = None
        mock_result.safety_margin = 1.92
        mock_result.warnings = []

        # Mock the simulation function
        with patch('rocket_sim.gui.simulation_thread.run_complete_simulation',
                   return_value=mock_result):

            # Set configuration
            main_window.config_widget.volume_input.setValue(2.0)

            # Trigger simulation
            main_window._run_simulation()

            # Wait for thread to complete (with timeout)
            if main_window.simulation_thread:
                main_window.simulation_thread.wait(5000)  # 5 second timeout

            # Check that results were displayed
            assert main_window.current_result is not None

    def test_export_without_results(self, main_window, qtbot):
        """Test export when no results are available."""
        main_window.current_result = None

        # Try to export (should show info message)
        main_window._export_results()
        # Note: This will show a message box, which is hard to test
        # In a real test, we'd mock QMessageBox


class TestMenuActions:
    """Tests for menu actions."""

    def test_about_dialog(self, main_window, qtbot):
        """Test about dialog can be shown."""
        # Call the about dialog method
        # Note: This will show a message box, which is hard to test
        # We're just checking it doesn't crash
        try:
            main_window._show_about()
        except Exception as e:
            pytest.fail(f"About dialog raised exception: {e}")

    def test_documentation_dialog(self, main_window, qtbot):
        """Test documentation dialog can be shown."""
        try:
            main_window._show_documentation()
        except Exception as e:
            pytest.fail(f"Documentation dialog raised exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
