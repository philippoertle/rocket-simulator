"""
Visualization Tools for Simulation Results

Provides plotting and visualization capabilities for:
- Time series data (P, T, SF)
- Stress distributions
- Comprehensive dashboards

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-8 (Visualization tools)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional, Tuple
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


def plot_pressure_temperature_time(result, save_path: Optional[str] = None, show: bool = True) -> Figure:
    """
    Plot pressure and temperature vs time on dual y-axis.

    Args:
        result: FullSimulationResult object
        save_path: Optional path to save figure
        show: Whether to display plot

    Returns:
        matplotlib Figure object

    Example:
        >>> fig = plot_pressure_temperature_time(result)
        >>> plt.show()
    """
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Pressure on left axis
    color = 'tab:blue'
    ax1.set_xlabel('Time (ms)', fontsize=12)
    ax1.set_ylabel('Pressure (bar)', color=color, fontsize=12)
    ax1.plot(result.system.time * 1000, result.system.pressure / 1e5,
             color=color, linewidth=2, label='Pressure')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # Temperature on right axis
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Temperature (K)', color=color, fontsize=12)
    ax2.plot(result.system.time * 1000, result.system.temperature,
             color=color, linewidth=2, linestyle='--', label='Temperature')
    ax2.tick_params(axis='y', labelcolor=color)

    # Title and legend
    plt.title(f'Pressure and Temperature Evolution\n'
              f'{result.config.volume*1000:.1f}L, MR={result.config.fuel_oxidizer_ratio:.1f}, '
              f'{result.config.vessel_material}',
              fontsize=14, fontweight='bold')

    # Add failure marker if applicable
    if result.failed and result.system.failure_time:
        ax1.axvline(result.system.failure_time * 1000, color='red',
                   linestyle=':', linewidth=2, label='Failure')
        ax1.text(result.system.failure_time * 1000, ax1.get_ylim()[1] * 0.9,
                'FAILURE', rotation=90, va='top', color='red', fontweight='bold')

    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig


def plot_stress_distribution(result, save_path: Optional[str] = None, show: bool = True) -> Figure:
    """
    Plot stress distribution through wall thickness.

    Shows hoop, radial, axial, and von Mises stresses from inner to outer surface.

    Args:
        result: FullSimulationResult object
        save_path: Optional path to save figure
        show: Whether to display plot

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Get FEM data
    r = np.array(result.fem_analysis['lame_solution']['r'])
    sigma_hoop = np.array(result.fem_analysis['lame_solution']['sigma_hoop']) / 1e6  # MPa
    sigma_radial = np.array(result.fem_analysis['lame_solution']['sigma_radial']) / 1e6
    sigma_axial = np.array(result.fem_analysis['lame_solution']['sigma_axial']) / 1e6
    sigma_vm = np.array(result.fem_analysis['lame_solution']['sigma_vm']) / 1e6

    # Convert radius to position through thickness
    r_inner = r[0]
    r_outer = r[-1]
    thickness = r_outer - r_inner
    position = (r - r_inner) / thickness  # 0 = inner, 1 = outer

    # Plot stresses
    ax.plot(position, sigma_hoop, 'b-', linewidth=2, label='Hoop (σ_θ)')
    ax.plot(position, sigma_radial, 'g--', linewidth=2, label='Radial (σ_r)')
    ax.plot(position, sigma_axial, 'r:', linewidth=2, label='Axial (σ_z)')
    ax.plot(position, sigma_vm, 'k-', linewidth=2.5, label='Von Mises (σ_vm)', alpha=0.7)

    # Yield strength line
    material_name = result.config.vessel_material
    from ..system_model import get_material
    material = get_material(material_name)
    ax.axhline(material.yield_strength / 1e6, color='red', linestyle='--',
               linewidth=1.5, alpha=0.7, label=f'Yield Strength ({material_name})')

    # Labels and formatting
    ax.set_xlabel('Position Through Thickness (0=inner, 1=outer)', fontsize=12)
    ax.set_ylabel('Stress (MPa)', fontsize=12)
    ax.set_title(f'Stress Distribution Through Wall\n'
                f'Peak Pressure: {result.summary["peak_pressure"]/1e5:.2f} bar, '
                f'Thickness: {thickness*1000:.3f} mm',
                fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig


def plot_safety_factor_evolution(result, save_path: Optional[str] = None, show: bool = True) -> Figure:
    """
    Plot safety factor evolution over time.

    Shows how close the vessel comes to failure.

    Args:
        result: FullSimulationResult object
        save_path: Optional path to save figure
        show: Whether to display plot

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot safety factor
    ax.plot(result.system.time * 1000, result.system.safety_factor,
            'b-', linewidth=2, label='Safety Factor (thin-wall)')

    # Failure threshold
    ax.axhline(1.0, color='red', linestyle='--', linewidth=2, label='Failure Threshold (SF=1)')

    # Recommended minimum
    ax.axhline(2.0, color='orange', linestyle=':', linewidth=1.5, label='Recommended Min (SF=2)')

    # Add safety factor with stress concentrations
    SF_conc = result.summary['safety_factor_with_concentration']
    ax.axhline(SF_conc, color='purple', linestyle='-.', linewidth=1.5,
              label=f'With Stress Concentrations (SF={SF_conc:.2f})')

    # Shaded regions
    ax.fill_between(result.system.time * 1000, 0, 1, alpha=0.2, color='red', label='Failure Zone')
    ax.fill_between(result.system.time * 1000, 1, 2, alpha=0.1, color='orange', label='Danger Zone')

    # Labels and formatting
    ax.set_xlabel('Time (ms)', fontsize=12)
    ax.set_ylabel('Safety Factor', fontsize=12)
    ax.set_title(f'Safety Factor Evolution\n'
                f'Min SF: {result.summary["min_safety_factor"]:.2f}, '
                f'Status: {"❌ FAILED" if result.failed else "✅ Safe"}',
                fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)

    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig


def create_comprehensive_dashboard(result, save_path: Optional[str] = None, show: bool = True) -> Figure:
    """
    Create comprehensive multi-panel dashboard with all key visualizations.

    Args:
        result: FullSimulationResult object
        save_path: Optional path to save figure
        show: Whether to display plot

    Returns:
        matplotlib Figure object with 4 subplots
    """
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # Panel 1: Pressure vs Time
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(result.system.time * 1000, result.system.pressure / 1e5, 'b-', linewidth=2)
    ax1.set_xlabel('Time (ms)')
    ax1.set_ylabel('Pressure (bar)')
    ax1.set_title('Pressure Evolution')
    ax1.grid(True, alpha=0.3)
    if result.failed and result.system.failure_time:
        ax1.axvline(result.system.failure_time * 1000, color='red', linestyle=':', linewidth=2)

    # Panel 2: Temperature vs Time
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(result.system.time * 1000, result.system.temperature, 'r-', linewidth=2)
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel('Temperature (K)')
    ax2.set_title('Temperature Evolution')
    ax2.grid(True, alpha=0.3)

    # Panel 3: Stress Distribution
    ax3 = fig.add_subplot(gs[1, 0])
    r = np.array(result.fem_analysis['lame_solution']['r'])
    sigma_vm = np.array(result.fem_analysis['lame_solution']['sigma_vm']) / 1e6
    position = (r - r[0]) / (r[-1] - r[0])
    ax3.plot(position, sigma_vm, 'k-', linewidth=2.5)
    ax3.set_xlabel('Position (0=inner, 1=outer)')
    ax3.set_ylabel('Von Mises Stress (MPa)')
    ax3.set_title('Stress Distribution')
    ax3.grid(True, alpha=0.3)

    # Panel 4: Safety Factor
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(result.system.time * 1000, result.system.safety_factor, 'b-', linewidth=2)
    ax4.axhline(1.0, color='red', linestyle='--', linewidth=2)
    ax4.axhline(2.0, color='orange', linestyle=':', linewidth=1.5)
    ax4.fill_between(result.system.time * 1000, 0, 1, alpha=0.2, color='red')
    ax4.set_xlabel('Time (ms)')
    ax4.set_ylabel('Safety Factor')
    ax4.set_title('Safety Factor Evolution')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(bottom=0)

    # Overall title
    fig.suptitle(f'PET Rocket Simulation Dashboard\n'
                f'{result.config.volume*1000:.1f}L, MR={result.config.fuel_oxidizer_ratio:.1f}, '
                f'{result.config.vessel_material}, Cap: {result.config.cap_type}\n'
                f'Status: {"❌ FAILED" if result.failed else "✅ Safe"} | '
                f'Min SF: {result.summary["min_safety_factor"]:.2f} | '
                f'Peak P: {result.summary["peak_pressure"]/1e5:.2f} bar',
                fontsize=16, fontweight='bold')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig


# Demonstration
if __name__ == "__main__":
    print("Visualization module loaded successfully.")
    print("Use with FullSimulationResult objects from integration module.")
