"""
Plot widgets for visualization in the GUI.

This module integrates Matplotlib with Qt to display
simulation results as interactive plots.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QMessageBox, QPushButton,
    QHBoxLayout, QFileDialog
)
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from rocket_sim.visualization.plots import (
    plot_pressure_temperature_time,
    plot_stress_distribution,
    plot_safety_factor_evolution,
    create_comprehensive_dashboard
)


class PlotCanvas(QWidget):
    """Widget containing a single Matplotlib figure."""

    def __init__(self, parent=None):
        """Initialize the plot canvas."""
        super().__init__(parent)

        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def clear(self):
        """Clear the figure."""
        self.figure.clear()
        self.canvas.draw()


class VisualizationWidget(QWidget):
    """Widget for displaying simulation plots in tabs."""

    def __init__(self, parent=None):
        """Initialize the visualization widget."""
        super().__init__(parent)
        self._init_ui()
        self.current_result = None

    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Create tab widget for different plot types
        self.tabs = QTabWidget()

        # Tab 1: Pressure & Temperature vs Time
        self.pressure_temp_canvas = PlotCanvas()
        self.tabs.addTab(self.pressure_temp_canvas, "Pressure & Temperature")

        # Tab 2: Stress Distribution
        self.stress_canvas = PlotCanvas()
        self.tabs.addTab(self.stress_canvas, "Stress Distribution")

        # Tab 3: Safety Factor Evolution
        self.safety_canvas = PlotCanvas()
        self.tabs.addTab(self.safety_canvas, "Safety Factor")

        # Tab 4: Comprehensive Dashboard
        self.dashboard_canvas = PlotCanvas()
        self.tabs.addTab(self.dashboard_canvas, "Dashboard (All)")

        layout.addWidget(self.tabs)

        # Add control buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh Plots")
        self.refresh_btn.clicked.connect(self.refresh_plots)
        button_layout.addWidget(self.refresh_btn)

        self.save_btn = QPushButton("Save Current Plot...")
        self.save_btn.clicked.connect(self.save_current_plot)
        button_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def display_results(self, result):
        """
        Display simulation results as plots.

        Args:
            result: SimulationResult object from run_complete_simulation
        """
        self.current_result = result

        try:
            # Generate all plots
            self._plot_pressure_temperature(result)
            self._plot_stress_distribution(result)
            self._plot_safety_factor(result)
            self._plot_dashboard(result)

        except Exception as e:
            QMessageBox.warning(
                self,
                "Plot Error",
                f"Failed to generate plots:\n{str(e)}"
            )

    def _plot_pressure_temperature(self, result):
        """Generate pressure & temperature vs time plot."""
        self.pressure_temp_canvas.figure.clear()

        # Use the existing visualization function
        # We need to adapt it to work with our figure
        ax1 = self.pressure_temp_canvas.figure.add_subplot(111)
        ax2 = ax1.twinx()

        # Extract data from result
        time = result.combustion.time
        pressure = result.combustion.pressure / 1e5  # Convert to bar
        temperature = result.combustion.temperature

        # Plot pressure
        ax1.plot(time * 1000, pressure, 'b-', linewidth=2, label='Pressure')
        ax1.set_xlabel('Time (ms)', fontsize=12)
        ax1.set_ylabel('Pressure (bar)', color='b', fontsize=12)
        ax1.tick_params(axis='y', labelcolor='b')
        ax1.grid(True, alpha=0.3)

        # Plot temperature
        ax2.plot(time * 1000, temperature, 'r-', linewidth=2, label='Temperature')
        ax2.set_ylabel('Temperature (K)', color='r', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='r')

        # Title
        self.pressure_temp_canvas.figure.suptitle(
            'Pressure & Temperature Evolution',
            fontsize=14,
            fontweight='bold'
        )

        self.pressure_temp_canvas.figure.tight_layout()
        self.pressure_temp_canvas.canvas.draw()

    def _plot_stress_distribution(self, result):
        """Generate stress distribution plot."""
        self.stress_canvas.figure.clear()

        # Get stress data from FEM results
        if hasattr(result, 'fem_analysis') and result.fem_analysis is not None:
            ax = self.stress_canvas.figure.add_subplot(111)

            fem = result.fem_analysis

            # Extract stress data from lame_solution
            if 'lame_solution' in fem:
                lame = fem['lame_solution']

                # Get inner and outer surface stresses
                # Inner surface is at index 0, outer at index -1
                hoop_inner = lame['sigma_hoop'][0] / 1e6 if lame['sigma_hoop'] else 0
                hoop_outer = lame['sigma_hoop'][-1] / 1e6 if lame['sigma_hoop'] else 0
                axial_inner = lame['sigma_axial'][0] / 1e6 if lame['sigma_axial'] else 0

                locations = ['Inner\nSurface', 'Outer\nSurface']
                hoop_stresses = [hoop_inner, hoop_outer]
                axial_stresses = [axial_inner, axial_inner]  # Axial is constant through thickness

                x = range(len(locations))
                width = 0.35

                ax.bar([i - width/2 for i in x], hoop_stresses, width,
                       label='Hoop Stress', color='steelblue')
                ax.bar([i + width/2 for i in x], axial_stresses, width,
                       label='Axial Stress', color='coral')

                ax.set_ylabel('Stress (MPa)', fontsize=12)
                ax.set_title('Stress Distribution', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(locations)
                ax.legend()
                ax.grid(True, alpha=0.3, axis='y')

                self.stress_canvas.figure.tight_layout()
            else:
                ax.text(0.5, 0.5, 'No Lamé solution data available',
                       ha='center', va='center', fontsize=14)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
        else:
            # No FEM data available
            ax = self.stress_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No FEM data available',
                   ha='center', va='center', fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

        self.stress_canvas.canvas.draw()

    def _plot_safety_factor(self, result):
        """Generate safety factor evolution plot."""
        self.safety_canvas.figure.clear()

        if hasattr(result, 'system') and result.system is not None:
            ax = self.safety_canvas.figure.add_subplot(111)

            dynamics = result.system
            time = dynamics.time * 1000  # Convert to ms
            safety_factor = dynamics.safety_factor

            # Plot safety factor
            ax.plot(time, safety_factor, 'g-', linewidth=2, label='Safety Factor')

            # Add critical safety factor line (SF = 1.0)
            ax.axhline(y=1.0, color='r', linestyle='--', linewidth=2,
                      label='Critical (SF=1.0)', alpha=0.7)

            # Add recommended safety factor line (SF = 2.0)
            ax.axhline(y=2.0, color='orange', linestyle='--', linewidth=1.5,
                      label='Recommended (SF=2.0)', alpha=0.7)

            ax.set_xlabel('Time (ms)', fontsize=12)
            ax.set_ylabel('Safety Factor', fontsize=12)
            ax.set_title('Safety Factor Evolution', fontsize=14, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)

            # Set y-axis to start at 0
            ax.set_ylim(bottom=0)

            self.safety_canvas.figure.tight_layout()
        else:
            # No dynamics data available
            ax = self.safety_canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No dynamics data available',
                   ha='center', va='center', fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

        self.safety_canvas.canvas.draw()

    def _plot_dashboard(self, result):
        """Generate comprehensive dashboard with all plots."""
        self.dashboard_canvas.figure.clear()

        # Create 2x2 subplot grid
        axes = self.dashboard_canvas.figure.subplots(2, 2)

        # Plot 1: Pressure vs Time
        if hasattr(result, 'combustion'):
            time = result.combustion.time * 1000
            pressure = result.combustion.pressure / 1e5
            axes[0, 0].plot(time, pressure, 'b-', linewidth=2)
            axes[0, 0].set_xlabel('Time (ms)')
            axes[0, 0].set_ylabel('Pressure (bar)', color='b')
            axes[0, 0].set_title('Pressure Evolution')
            axes[0, 0].grid(True, alpha=0.3)

        # Plot 2: Temperature vs Time
        if hasattr(result, 'combustion'):
            temperature = result.combustion.temperature
            axes[0, 1].plot(time, temperature, 'r-', linewidth=2)
            axes[0, 1].set_xlabel('Time (ms)')
            axes[0, 1].set_ylabel('Temperature (K)', color='r')
            axes[0, 1].set_title('Temperature Evolution')
            axes[0, 1].grid(True, alpha=0.3)

        # Plot 3: Safety Factor
        if hasattr(result, 'system') and result.system is not None:
            dyn_time = result.system.time * 1000
            sf = result.system.safety_factor
            axes[1, 0].plot(dyn_time, sf, 'g-', linewidth=2)
            axes[1, 0].axhline(y=1.0, color='r', linestyle='--', alpha=0.7)
            axes[1, 0].axhline(y=2.0, color='orange', linestyle='--', alpha=0.7)
            axes[1, 0].set_xlabel('Time (ms)')
            axes[1, 0].set_ylabel('Safety Factor')
            axes[1, 0].set_title('Safety Factor')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].set_ylim(bottom=0)

        # Plot 4: Stress Summary
        if hasattr(result, 'fem_analysis') and result.fem_analysis is not None:
            fem = result.fem_analysis
            if 'lame_solution' in fem:
                lame = fem['lame_solution']
                locations = ['Inner', 'Outer']
                stresses = [
                    lame['sigma_hoop'][0] / 1e6 if lame['sigma_hoop'] else 0,
                    lame['sigma_hoop'][-1] / 1e6 if lame['sigma_hoop'] else 0
                ]
                axes[1, 1].bar(locations, stresses, color=['steelblue', 'coral'])
                axes[1, 1].set_ylabel('Hoop Stress (MPa)')
                axes[1, 1].set_title('Stress Distribution')
                axes[1, 1].grid(True, alpha=0.3, axis='y')

        self.dashboard_canvas.figure.suptitle(
            'Comprehensive Simulation Dashboard',
            fontsize=14,
            fontweight='bold'
        )

        self.dashboard_canvas.figure.tight_layout()
        self.dashboard_canvas.canvas.draw()

    def refresh_plots(self):
        """Refresh all plots with current result."""
        if self.current_result is not None:
            self.display_results(self.current_result)
        else:
            QMessageBox.information(
                self,
                "No Data",
                "No simulation results available. Run a simulation first."
            )

    def save_current_plot(self):
        """Save the currently displayed plot."""
        current_index = self.tabs.currentIndex()
        canvases = [
            self.pressure_temp_canvas,
            self.stress_canvas,
            self.safety_canvas,
            self.dashboard_canvas
        ]
        tab_names = [
            "pressure_temperature",
            "stress_distribution",
            "safety_factor",
            "dashboard"
        ]

        canvas = canvases[current_index]
        default_name = f"simulation_{tab_names[current_index]}.png"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot",
            default_name,
            "PNG Images (*.png);;PDF Files (*.pdf);;All Files (*)"
        )

        if filename:
            try:
                canvas.figure.savefig(filename, dpi=300, bbox_inches='tight')
                QMessageBox.information(
                    self,
                    "Success",
                    f"Plot saved to:\n{filename}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Save Error",
                    f"Failed to save plot:\n{str(e)}"
                )

    def clear_all(self):
        """Clear all plots."""
        self.pressure_temp_canvas.clear()
        self.stress_canvas.clear()
        self.safety_canvas.clear()
        self.dashboard_canvas.clear()
        self.current_result = None
