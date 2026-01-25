"""
Unit tests for GUI widgets.

Tests the ConfigurationWidget, SimulationControlWidget, and ResultsWidget.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from rocket_sim.gui.widgets import (
    ConfigurationWidget,
    SimulationControlWidget,
    ResultsWidget
)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestConfigurationWidget:
    """Tests for ConfigurationWidget."""

    def test_default_values(self, qapp):
        """Test widget initializes with correct default values."""
        widget = ConfigurationWidget()

        assert widget.volume_input.value() == 2.0
        assert widget.ratio_input.value() == 2.0
        assert widget.diameter_input.value() == 95.0
        assert widget.thickness_input.value() == 0.3
        assert widget.material_combo.currentText() == "PET"

    def test_validation_valid_input(self, qapp):
        """Test validation accepts valid input."""
        widget = ConfigurationWidget()

        widget.volume_input.setValue(2.0)
        widget.ratio_input.setValue(2.0)
        widget.diameter_input.setValue(95.0)
        widget.thickness_input.setValue(0.3)

        assert widget.is_valid()

    def test_get_config_dict(self, qapp):
        """Test configuration dictionary generation."""
        widget = ConfigurationWidget()

        config = widget.get_config_dict()

        assert "volume" in config
        assert "fuel_oxidizer_ratio" in config
        assert "vessel_diameter" in config
        assert "vessel_thickness" in config
        assert "vessel_material" in config

        # Check unit conversions
        assert config["volume"] == 0.002  # 2L -> 0.002 m³
        assert config["vessel_diameter"] == 0.095  # 95mm -> 0.095 m
        assert config["vessel_thickness"] == 0.0003  # 0.3mm -> 0.0003 m

    def test_default_preset(self, qapp):
        """Test default preset button."""
        widget = ConfigurationWidget()

        # Change values
        widget.volume_input.setValue(1.0)
        widget.ratio_input.setValue(1.5)

        # Load default preset
        widget._load_default_preset()

        assert widget.volume_input.value() == 2.0
        assert widget.ratio_input.value() == 2.0
        assert widget.diameter_input.value() == 95.0
        assert widget.thickness_input.value() == 0.3
        assert widget.material_combo.currentText() == "PET"

    def test_dangerous_preset(self, qapp):
        """Test dangerous preset button."""
        widget = ConfigurationWidget()

        widget._load_dangerous_preset()

        assert widget.volume_input.value() == 0.5
        assert widget.diameter_input.value() == 60.0
        assert widget.thickness_input.value() == 0.15

    def test_config_changed_signal(self, qapp, qtbot):
        """Test that config_changed signal is emitted on changes."""
        widget = ConfigurationWidget()

        with qtbot.waitSignal(widget.config_changed, timeout=1000):
            widget.volume_input.setValue(3.0)


class TestSimulationControlWidget:
    """Tests for SimulationControlWidget."""

    def test_initial_state(self, qapp):
        """Test widget initializes in ready state."""
        widget = SimulationControlWidget()

        assert widget.run_button.isEnabled()
        assert not widget.progress_bar.isVisible()
        assert widget.status_label.text() == "Ready"

    def test_set_state_running(self, qapp, qtbot):
        """Test running state configuration."""
        widget = SimulationControlWidget()
        widget.show()
        qtbot.addWidget(widget)

        widget.set_state_running()
        qapp.processEvents()  # Process pending events

        assert not widget.run_button.isEnabled()
        assert not widget.progress_bar.isHidden()  # Check isHidden() instead
        assert "Running" in widget.status_label.text()

    def test_set_state_complete(self, qapp):
        """Test complete state configuration."""
        widget = SimulationControlWidget()

        widget.set_state_complete(elapsed_time=3.5)

        assert widget.run_button.isEnabled()
        assert not widget.progress_bar.isVisible()
        assert "Complete" in widget.status_label.text()
        assert "3.50" in widget.time_label.text()

    def test_set_state_error(self, qapp):
        """Test error state configuration."""
        widget = SimulationControlWidget()

        widget.set_state_error("Test error message")

        assert widget.run_button.isEnabled()
        assert not widget.progress_bar.isVisible()
        assert "Error" in widget.status_label.text()
        assert "Test error message" in widget.status_label.text()

    def test_run_requested_signal(self, qapp, qtbot):
        """Test that run_requested signal is emitted on button click."""
        widget = SimulationControlWidget()

        with qtbot.waitSignal(widget.run_requested, timeout=1000):
            qtbot.mouseClick(widget.run_button, Qt.LeftButton)


class TestResultsWidget:
    """Tests for ResultsWidget."""

    def test_initial_state(self, qapp):
        """Test widget initializes empty."""
        widget = ResultsWidget()

        assert widget.results_text.toPlainText() == ""

    def test_clear(self, qapp):
        """Test clear functionality."""
        widget = ResultsWidget()

        widget.results_text.setPlainText("Some text")
        widget.clear()

        assert widget.results_text.toPlainText() == ""

    def test_text_method(self, qapp):
        """Test text() method returns plain text."""
        widget = ResultsWidget()

        widget.results_text.setPlainText("Test results")

        assert "Test results" in widget.text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
