"""
Custom widgets for the rocket simulator GUI.

This module contains reusable widgets for configuration input,
simulation control, and results display.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QDoubleSpinBox, QComboBox, QPushButton, QTextEdit, QProgressBar,
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ConfigurationWidget(QWidget):
    """Widget for configuring simulation parameters."""

    # Signal emitted when configuration changes
    config_changed = Signal()

    def __init__(self, parent=None):
        """Initialize the configuration widget."""
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Create group box
        group = QGroupBox("Simulation Configuration")
        form_layout = QFormLayout()

        # Volume input
        self.volume_input = QDoubleSpinBox()
        self.volume_input.setRange(0.5, 5.0)
        self.volume_input.setValue(2.0)
        self.volume_input.setSuffix(" L")
        self.volume_input.setDecimals(3)
        self.volume_input.setSingleStep(0.1)
        self.volume_input.setToolTip("Bottle volume in liters (0.5 - 5.0 L)")
        form_layout.addRow("Volume:", self.volume_input)

        # Fuel/Oxidizer ratio input
        self.ratio_input = QDoubleSpinBox()
        self.ratio_input.setRange(1.0, 3.0)
        self.ratio_input.setValue(2.0)
        self.ratio_input.setDecimals(2)
        self.ratio_input.setSingleStep(0.1)
        self.ratio_input.setToolTip("H₂:O₂ molar ratio (2.0 = stoichiometric)")
        form_layout.addRow("H₂:O₂ Ratio:", self.ratio_input)

        # Vessel diameter input
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(50.0, 150.0)
        self.diameter_input.setValue(95.0)
        self.diameter_input.setSuffix(" mm")
        self.diameter_input.setDecimals(1)
        self.diameter_input.setSingleStep(1.0)
        self.diameter_input.setToolTip("Vessel diameter in millimeters (50 - 150 mm)")
        form_layout.addRow("Diameter:", self.diameter_input)

        # Vessel thickness input
        self.thickness_input = QDoubleSpinBox()
        self.thickness_input.setRange(0.1, 1.0)
        self.thickness_input.setValue(0.3)
        self.thickness_input.setSuffix(" mm")
        self.thickness_input.setDecimals(2)
        self.thickness_input.setSingleStep(0.05)
        self.thickness_input.setToolTip("Wall thickness in millimeters (0.1 - 1.0 mm)")
        form_layout.addRow("Thickness:", self.thickness_input)

        # Material selection
        self.material_combo = QComboBox()
        self.material_combo.addItems(["PET", "HDPE", "Polycarbonate"])
        self.material_combo.setToolTip("Vessel material type")
        form_layout.addRow("Material:", self.material_combo)

        group.setLayout(form_layout)
        layout.addWidget(group)

        # Add preset buttons
        preset_layout = QHBoxLayout()

        self.default_btn = QPushButton("Default (Safe)")
        self.default_btn.setToolTip("Load safe default configuration (2L PET bottle)")
        self.default_btn.clicked.connect(self._load_default_preset)
        preset_layout.addWidget(self.default_btn)

        self.dangerous_btn = QPushButton("Dangerous (High Pressure)")
        self.dangerous_btn.setToolTip("Load dangerous configuration for testing")
        self.dangerous_btn.clicked.connect(self._load_dangerous_preset)
        preset_layout.addWidget(self.dangerous_btn)

        layout.addLayout(preset_layout)
        layout.addStretch()

    def _connect_signals(self):
        """Connect widget signals."""
        # Use lambda to absorb the float argument from valueChanged
        self.volume_input.valueChanged.connect(lambda: self.config_changed.emit())
        self.ratio_input.valueChanged.connect(lambda: self.config_changed.emit())
        self.diameter_input.valueChanged.connect(lambda: self.config_changed.emit())
        self.thickness_input.valueChanged.connect(lambda: self.config_changed.emit())
        self.material_combo.currentTextChanged.connect(lambda: self.config_changed.emit())

    def _load_default_preset(self):
        """Load default safe configuration."""
        self.volume_input.setValue(2.0)
        self.ratio_input.setValue(2.0)
        self.diameter_input.setValue(95.0)
        self.thickness_input.setValue(0.3)
        self.material_combo.setCurrentText("PET")

    def _load_dangerous_preset(self):
        """Load dangerous high-pressure configuration."""
        self.volume_input.setValue(0.5)  # Smaller volume
        self.ratio_input.setValue(2.0)
        self.diameter_input.setValue(60.0)  # Smaller diameter
        self.thickness_input.setValue(0.15)  # Thinner walls
        self.material_combo.setCurrentText("PET")

    def get_config_dict(self):
        """
        Get configuration as dictionary.

        Returns:
            dict: Configuration parameters in format expected by FullSimulationConfig
        """
        return {
            "volume": self.volume_input.value() / 1000.0,  # Convert L to m³
            "fuel_oxidizer_ratio": self.ratio_input.value(),
            "vessel_diameter": self.diameter_input.value() / 1000.0,  # Convert mm to m
            "vessel_thickness": self.thickness_input.value() / 1000.0,  # Convert mm to m
            "vessel_material": self.material_combo.currentText()
        }

    def is_valid(self):
        """
        Check if current configuration is valid.

        Returns:
            bool: True if all inputs are valid
        """
        # All spinboxes enforce range validation, so just check they're in range
        return (
            self.volume_input.minimum() <= self.volume_input.value() <= self.volume_input.maximum() and
            self.ratio_input.minimum() <= self.ratio_input.value() <= self.ratio_input.maximum() and
            self.diameter_input.minimum() <= self.diameter_input.value() <= self.diameter_input.maximum() and
            self.thickness_input.minimum() <= self.thickness_input.value() <= self.thickness_input.maximum()
        )


class SimulationControlWidget(QWidget):
    """Widget for controlling simulation execution."""

    # Signals
    run_requested = Signal()
    cancel_requested = Signal()

    def __init__(self, parent=None):
        """Initialize the control widget."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Run button
        self.run_button = QPushButton("▶ Run Simulation")
        self.run_button.setMinimumHeight(40)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.run_button.setFont(font)
        self.run_button.clicked.connect(self.run_requested.emit)
        layout.addWidget(self.run_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Elapsed time label
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

    def set_state_ready(self):
        """Set widget to ready state."""
        self.run_button.setEnabled(True)
        self.run_button.setText("▶ Run Simulation")
        self.progress_bar.hide()
        self.status_label.setText("Ready")
        self.time_label.setText("")

    def set_state_running(self):
        """Set widget to running state."""
        self.run_button.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.show()
        self.status_label.setText("Running simulation...")

    def set_state_complete(self, elapsed_time: float):
        """
        Set widget to complete state.

        Args:
            elapsed_time: Simulation time in seconds
        """
        self.run_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText("✅ Complete")
        self.time_label.setText(f"Elapsed: {elapsed_time:.2f} s")

    def set_state_error(self, error_msg: str):
        """
        Set widget to error state.

        Args:
            error_msg: Error message to display
        """
        self.run_button.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"❌ Error: {error_msg}")

    def update_progress(self, percentage: int, message: str):
        """
        Update progress indicator.

        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        if self.progress_bar.maximum() == 0:
            self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)


class ResultsWidget(QWidget):
    """Widget for displaying simulation results."""

    def __init__(self, parent=None):
        """Initialize the results widget."""
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Results text display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)

        # Set monospace font for aligned text
        font = QFont("Courier New", 10)
        self.results_text.setFont(font)

        layout.addWidget(self.results_text)

        # Clear button
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear)
        layout.addWidget(clear_btn)

    def display_results(self, result):
        """
        Display simulation results.

        Args:
            result: SimulationResult object from run_complete_simulation
        """
        text = self._format_results(result)
        self.results_text.setHtml(text)

    def _format_results(self, result) -> str:
        """
        Format simulation results as HTML.

        Args:
            result: SimulationResult object

        Returns:
            str: Formatted HTML text
        """
        html = "<pre style='font-size: 11pt;'>"
        html += "=" * 70 + "\n"
        html += "<b>PET ROCKET SIMULATOR - SIMULATION RESULTS</b>\n"
        html += "=" * 70 + "\n\n"

        # Summary statistics
        summary = result.summary
        html += "<b>SUMMARY:</b>\n"
        html += f"  Peak Pressure:      {summary['peak_pressure']/1e5:.2f} bar\n"
        html += f"  Peak Temperature:   {summary['peak_temperature']:.0f} K\n"
        html += f"  Min Safety Factor:  {summary['min_safety_factor']:.2f}\n"
        html += f"  Max Stress:         {summary['max_von_mises_stress']/1e6:.1f} MPa\n\n"

        # Safety status
        if result.failed:
            html += f"<b style='color: red;'>STATUS: ⚠️ UNSAFE - FAILURE PREDICTED</b>\n"
            html += f"<span style='color: red;'>  Failure Location: {result.failure_location}</span>\n"
        else:
            html += f"<b style='color: green;'>STATUS: ✅ SAFE</b>\n"
            html += f"<span style='color: green;'>  Safety Margin: {result.safety_margin:.2f}</span>\n"

        # Warnings
        if result.warnings:
            html += "\n<b style='color: orange;'>WARNINGS:</b>\n"
            for warning in result.warnings:
                html += f"<span style='color: orange;'>  ⚠️ {warning}</span>\n"

        html += "\n" + "=" * 70 + "\n"
        html += "</pre>"

        return html

    def clear(self):
        """Clear results display."""
        self.results_text.clear()

    def text(self) -> str:
        """
        Get plain text of results.

        Returns:
            str: Plain text results
        """
        return self.results_text.toPlainText()
