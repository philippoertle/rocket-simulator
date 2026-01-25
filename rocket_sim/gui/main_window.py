"""
Main window for the rocket simulator GUI.

This module provides the top-level application window that integrates
all GUI components.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QMessageBox, QFileDialog, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
import json
from datetime import datetime

from rocket_sim.gui.widgets import (
    ConfigurationWidget,
    SimulationControlWidget,
    ResultsWidget
)
from rocket_sim.gui.plot_widgets import VisualizationWidget
from rocket_sim.gui.simulation_thread import SimulationThread


class MainWindow(QMainWindow):
    """Main application window for the rocket simulator GUI."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self.simulation_thread = None
        self.current_result = None

        self._init_ui()
        self._create_menus()
        self._create_status_bar()
        self._connect_signals()

        # Set window properties
        self.setWindowTitle("PET Rocket Simulator v0.1.0")
        self.resize(1400, 900)

    def _init_ui(self):
        """Initialize the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Configuration and Control
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.config_widget = ConfigurationWidget()
        left_layout.addWidget(self.config_widget)

        self.control_widget = SimulationControlWidget()
        left_layout.addWidget(self.control_widget)

        left_layout.addStretch()

        # Right panel: Results and Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.results_widget = ResultsWidget()
        right_layout.addWidget(self.results_widget)

        self.plot_widget = VisualizationWidget()
        right_layout.addWidget(self.plot_widget)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([400, 1000])

        main_layout.addWidget(splitter)

    def _create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        export_action = QAction("&Export Results...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_results)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _connect_signals(self):
        """Connect widget signals to slots."""
        self.control_widget.run_requested.connect(self._run_simulation)
        self.config_widget.config_changed.connect(self._on_config_changed)

    def _on_config_changed(self):
        """Handle configuration changes."""
        self.status_bar.showMessage("Configuration changed")

    def _run_simulation(self):
        """Run the simulation in a background thread."""
        # Validate configuration
        if not self.config_widget.is_valid():
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "Please check your configuration parameters."
            )
            return

        # Get configuration
        config_dict = self.config_widget.get_config_dict()

        # Update UI state
        self.control_widget.set_state_running()
        self.status_bar.showMessage("Running simulation...")

        # Create and start simulation thread
        self.simulation_thread = SimulationThread(config_dict)
        self.simulation_thread.progress_updated.connect(self._on_progress_updated)
        self.simulation_thread.simulation_complete.connect(self._on_simulation_complete)
        self.simulation_thread.simulation_failed.connect(self._on_simulation_failed)
        self.simulation_thread.start()

    def _on_progress_updated(self, percentage: int, message: str):
        """
        Handle simulation progress updates.

        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        self.control_widget.update_progress(percentage, message)
        self.status_bar.showMessage(message)

    def _on_simulation_complete(self, result, elapsed_time: float):
        """
        Handle simulation completion.

        Args:
            result: SimulationResult object
            elapsed_time: Elapsed time in seconds
        """
        self.current_result = result

        # Update UI state
        self.control_widget.set_state_complete(elapsed_time)
        self.status_bar.showMessage(f"Simulation complete in {elapsed_time:.2f} s")

        # Display results
        self.results_widget.display_results(result)
        self.plot_widget.display_results(result)

        # Show completion message
        if result.failed:
            QMessageBox.warning(
                self,
                "Simulation Complete - UNSAFE",
                f"⚠️ FAILURE PREDICTED\n\n"
                f"Peak Pressure: {result.summary['peak_pressure']/1e5:.2f} bar\n"
                f"Safety Factor: {result.summary['min_safety_factor']:.2f}\n"
                f"Failure Location: {result.failure_location}\n\n"
                f"See results panel for details."
            )
        else:
            QMessageBox.information(
                self,
                "Simulation Complete - SAFE",
                f"✅ SAFE CONFIGURATION\n\n"
                f"Peak Pressure: {result.summary['peak_pressure']/1e5:.2f} bar\n"
                f"Safety Factor: {result.summary['min_safety_factor']:.2f}\n"
                f"Max Stress: {result.summary['max_von_mises_stress']/1e6:.1f} MPa\n\n"
                f"Elapsed Time: {elapsed_time:.2f} s"
            )

    def _on_simulation_failed(self, error_msg: str):
        """
        Handle simulation failure.

        Args:
            error_msg: Error message
        """
        self.control_widget.set_state_error(error_msg)
        self.status_bar.showMessage(f"Simulation failed: {error_msg}")

        QMessageBox.critical(
            self,
            "Simulation Error",
            f"Simulation failed with error:\n\n{error_msg}\n\n"
            f"Please check your configuration and try again."
        )

    def _export_results(self):
        """Export simulation results to file."""
        if self.current_result is None:
            QMessageBox.information(
                self,
                "No Results",
                "No simulation results available. Run a simulation first."
            )
            return

        # Ask user for export format
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Export Results")
        msg_box.setText("Choose export format:")

        json_btn = msg_box.addButton("JSON", QMessageBox.ActionRole)
        text_btn = msg_box.addButton("Text Report", QMessageBox.ActionRole)
        cancel_btn = msg_box.addButton(QMessageBox.Cancel)

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == json_btn:
            self._export_json()
        elif clicked == text_btn:
            self._export_text()

    def _export_json(self):
        """Export results as JSON."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if filename:
            try:
                # Convert result to JSON-serializable dict
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "configuration": self.config_widget.get_config_dict(),
                    "summary": self.current_result.summary,
                    "failed": self.current_result.failed,
                    "failure_location": self.current_result.failure_location,
                    "safety_margin": self.current_result.safety_margin,
                    "warnings": self.current_result.warnings
                }

                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Results exported to:\n{filename}"
                )

            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Export Error",
                    f"Failed to export results:\n{str(e)}"
                )

    def _export_text(self):
        """Export results as text report."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Text Report",
            f"simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            try:
                text = self.results_widget.text()

                # Add configuration info
                config = self.config_widget.get_config_dict()
                header = "=" * 70 + "\n"
                header += "PET ROCKET SIMULATOR - SIMULATION REPORT\n"
                header += "=" * 70 + "\n\n"
                header += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                header += "CONFIGURATION:\n"
                header += f"  Volume:              {config['volume']*1000:.3f} L\n"
                header += f"  H2:O2 Ratio:         {config['fuel_oxidizer_ratio']:.2f}\n"
                header += f"  Vessel Diameter:     {config['vessel_diameter']*1000:.1f} mm\n"
                header += f"  Vessel Thickness:    {config['vessel_thickness']*1000:.2f} mm\n"
                header += f"  Vessel Material:     {config['vessel_material']}\n\n"

                full_text = header + text

                with open(filename, 'w') as f:
                    f.write(full_text)

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Report exported to:\n{filename}"
                )

            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Export Error",
                    f"Failed to export report:\n{str(e)}"
                )

    def _show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>PET Rocket Simulator</h2>
        <p><b>Version:</b> 0.1.0</p>
        <p><b>License:</b> MIT License</p>
        
        <p>A safety-focused simulation framework to predict and prevent 
        catastrophic structural failure in experimental PET bottle 
        hydrogen/oxygen rockets.</p>
        
        <p><b>⚠️ WARNING:</b> This is a simulation tool. PET bottle rockets 
        with H₂/O₂ combustion are extremely dangerous and can cause severe 
        injury or death. This software is for educational and research 
        purposes only.</p>
        
        <p><b>Development:</b> ISO/IEC/IEEE 12207:2017 Compliant</p>
        
        <p><b>GitHub:</b> 
        <a href="https://github.com/philippoertle/rocket-simulator">
        github.com/philippoertle/rocket-simulator
        </a></p>
        
        <p><b>Documentation:</b> See README.md and QUICKSTART.md</p>
        
        <p>© 2026 PET Rocket Simulator Team</p>
        """

        QMessageBox.about(self, "About PET Rocket Simulator", about_text)

    def _show_documentation(self):
        """Show documentation information."""
        doc_text = """
        <h3>Documentation</h3>
        
        <p><b>Getting Started:</b></p>
        <ul>
        <li>README.md - Project overview</li>
        <li>INSTALL.md - Installation instructions</li>
        <li>QUICKSTART.md - Quick start guide</li>
        </ul>
        
        <p><b>Using the GUI:</b></p>
        <ol>
        <li>Configure simulation parameters on the left panel</li>
        <li>Click "Run Simulation" to execute</li>
        <li>View results and plots on the right panel</li>
        <li>Export results using File > Export Results</li>
        </ol>
        
        <p><b>Configuration Parameters:</b></p>
        <ul>
        <li><b>Volume:</b> Bottle volume (0.5-5.0 L)</li>
        <li><b>H₂:O₂ Ratio:</b> Fuel/oxidizer molar ratio (2.0 = stoichiometric)</li>
        <li><b>Diameter:</b> Vessel diameter (50-150 mm)</li>
        <li><b>Thickness:</b> Wall thickness (0.1-1.0 mm)</li>
        <li><b>Material:</b> Vessel material (PET, HDPE, Polycarbonate)</li>
        </ul>
        
        <p><b>Presets:</b></p>
        <ul>
        <li><b>Default (Safe):</b> 2L PET bottle with safe parameters</li>
        <li><b>Dangerous:</b> High-pressure configuration for testing</li>
        </ul>
        
        <p><b>Online Documentation:</b><br>
        <a href="https://github.com/philippoertle/rocket-simulator/blob/main/README.md">
        View full documentation on GitHub
        </a></p>
        """

        QMessageBox.information(self, "Documentation", doc_text)

    def closeEvent(self, event):
        """Handle window close event."""
        # If simulation is running, ask for confirmation
        if self.simulation_thread is not None and self.simulation_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Simulation Running",
                "A simulation is currently running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Terminate the thread
                self.simulation_thread.terminate()
                self.simulation_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
