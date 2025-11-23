"""
Simulation and visualization tools for hydrogen generator models.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from integrated_model import HydrogenGeneratorModel
from generator_configs import get_config, list_configs


def voltage_sweep(model: HydrogenGeneratorModel, 
                 voltage_range: Tuple[float, float] = (6.0, 14.0),
                 num_points: int = 50) -> dict:
    """
    Sweep voltage and analyze performance.
    
    Args:
        model: Generator model to analyze
        voltage_range: (min, max) voltage in volts
        num_points: Number of points to sample
        
    Returns:
        Dictionary with arrays of results
    """
    voltages = np.linspace(voltage_range[0], voltage_range[1], num_points)
    current = model.config.current_amperes
    
    results = {
        'voltage': voltages,
        'efficiency': [],
        'production_lpm': [],
        'power': [],
        'current_density': [],
        'temperature': [],
    }
    
    for v in voltages:
        analysis = model.analyze_performance(voltage=v, current=current)
        results['efficiency'].append(analysis['efficiency']['efficiency_percentage'])
        results['production_lpm'].append(analysis['chemical']['h2_production_lpm'])
        results['power'].append(analysis['configuration']['power_w'])
        results['current_density'].append(analysis['physical']['current_density_ma_cm2'])
        results['temperature'].append(analysis['physical']['estimated_temp_celsius'])
    
    return results


def current_sweep(model: HydrogenGeneratorModel,
                 current_range: Tuple[float, float] = (1.0, 30.0),
                 num_points: int = 50) -> dict:
    """
    Sweep current and analyze performance.
    
    Args:
        model: Generator model to analyze
        current_range: (min, max) current in amperes
        num_points: Number of points to sample
        
    Returns:
        Dictionary with arrays of results
    """
    currents = np.linspace(current_range[0], current_range[1], num_points)
    voltage = model.config.voltage_volts
    
    results = {
        'current': currents,
        'efficiency': [],
        'production_lpm': [],
        'power': [],
        'current_density': [],
        'temperature': [],
    }
    
    for i in currents:
        analysis = model.analyze_performance(voltage=voltage, current=i)
        results['efficiency'].append(analysis['efficiency']['efficiency_percentage'])
        results['production_lpm'].append(analysis['chemical']['h2_production_lpm'])
        results['power'].append(analysis['configuration']['power_w'])
        results['current_density'].append(analysis['physical']['current_density_ma_cm2'])
        results['temperature'].append(analysis['physical']['estimated_temp_celsius'])
    
    return results


def plot_voltage_analysis(model: HydrogenGeneratorModel, 
                         voltage_range: Tuple[float, float] = (6.0, 14.0)):
    """
    Plot comprehensive voltage sweep analysis.
    
    Args:
        model: Generator model
        voltage_range: Range of voltages to analyze
    """
    results = voltage_sweep(model, voltage_range)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Voltage Analysis: {model.config.name}', fontsize=14, fontweight='bold')
    
    # Efficiency vs Voltage
    ax1 = axes[0, 0]
    ax1.plot(results['voltage'], results['efficiency'], 'b-', linewidth=2)
    ax1.axvline(model.config.voltage_volts, color='r', linestyle='--', 
                label='Configured voltage')
    ax1.set_xlabel('Voltage (V)')
    ax1.set_ylabel('Efficiency (%)')
    ax1.set_title('Efficiency vs Voltage')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Production vs Voltage
    ax2 = axes[0, 1]
    ax2.plot(results['voltage'], results['production_lpm'], 'g-', linewidth=2)
    ax2.axvline(model.config.voltage_volts, color='r', linestyle='--')
    ax2.set_xlabel('Voltage (V)')
    ax2.set_ylabel('H₂ Production (L/min)')
    ax2.set_title('Production Rate vs Voltage')
    ax2.grid(True, alpha=0.3)
    
    # Power vs Voltage
    ax3 = axes[1, 0]
    ax3.plot(results['voltage'], results['power'], 'orange', linewidth=2)
    ax3.axvline(model.config.voltage_volts, color='r', linestyle='--')
    ax3.set_xlabel('Voltage (V)')
    ax3.set_ylabel('Power (W)')
    ax3.set_title('Power Consumption vs Voltage')
    ax3.grid(True, alpha=0.3)
    
    # Temperature vs Voltage
    ax4 = axes[1, 1]
    ax4.plot(results['voltage'], results['temperature'], 'purple', linewidth=2)
    ax4.axvline(model.config.voltage_volts, color='r', linestyle='--')
    ax4.axhline(60, color='orange', linestyle=':', label='High temp warning')
    ax4.set_xlabel('Voltage (V)')
    ax4.set_ylabel('Temperature (°C)')
    ax4.set_title('Operating Temperature vs Voltage')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    return fig


def plot_current_analysis(model: HydrogenGeneratorModel,
                         current_range: Tuple[float, float] = (1.0, 30.0)):
    """
    Plot comprehensive current sweep analysis.
    
    Args:
        model: Generator model
        current_range: Range of currents to analyze
    """
    results = current_sweep(model, current_range)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'Current Analysis: {model.config.name}', fontsize=14, fontweight='bold')
    
    # Efficiency vs Current
    ax1 = axes[0, 0]
    ax1.plot(results['current'], results['efficiency'], 'b-', linewidth=2)
    ax1.axvline(model.config.current_amperes, color='r', linestyle='--',
                label='Configured current')
    ax1.set_xlabel('Current (A)')
    ax1.set_ylabel('Efficiency (%)')
    ax1.set_title('Efficiency vs Current')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Production vs Current
    ax2 = axes[0, 1]
    ax2.plot(results['current'], results['production_lpm'], 'g-', linewidth=2)
    ax2.axvline(model.config.current_amperes, color='r', linestyle='--')
    ax2.set_xlabel('Current (A)')
    ax2.set_ylabel('H₂ Production (L/min)')
    ax2.set_title('Production Rate vs Current')
    ax2.grid(True, alpha=0.3)
    
    # Current Density vs Current
    ax3 = axes[1, 0]
    ax3.plot(results['current'], results['current_density'], 'orange', linewidth=2)
    ax3.axvline(model.config.current_amperes, color='r', linestyle='--')
    ax3.axhspan(100, 500, alpha=0.2, color='green', label='Optimal range')
    ax3.set_xlabel('Current (A)')
    ax3.set_ylabel('Current Density (mA/cm²)')
    ax3.set_title('Current Density vs Current')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Temperature vs Current
    ax4 = axes[1, 1]
    ax4.plot(results['current'], results['temperature'], 'purple', linewidth=2)
    ax4.axvline(model.config.current_amperes, color='r', linestyle='--')
    ax4.axhline(60, color='orange', linestyle=':', label='High temp warning')
    ax4.set_xlabel('Current (A)')
    ax4.set_ylabel('Temperature (°C)')
    ax4.set_title('Operating Temperature vs Current')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    return fig


def compare_configurations(config_names: List[str] = None):
    """
    Compare multiple generator configurations.
    
    Args:
        config_names: List of configuration names to compare
    """
    if config_names is None:
        config_names = list_configs()[:4]  # Compare first 4
    
    models = [HydrogenGeneratorModel(get_config(name)) for name in config_names]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Configuration Comparison', fontsize=14, fontweight='bold')
    
    names = []
    efficiencies = []
    productions = []
    powers = []
    current_densities = []
    
    for model in models:
        analysis = model.analyze_performance()
        names.append(model.config.name[:20])  # Truncate long names
        efficiencies.append(analysis['efficiency']['efficiency_percentage'])
        productions.append(analysis['chemical']['h2_production_lpm'])
        powers.append(analysis['configuration']['power_w'])
        current_densities.append(analysis['physical']['current_density_ma_cm2'])
    
    x_pos = np.arange(len(names))
    
    # Efficiency comparison
    ax1 = axes[0, 0]
    bars1 = ax1.bar(x_pos, efficiencies, color='skyblue')
    ax1.set_ylabel('Efficiency (%)')
    ax1.set_title('System Efficiency')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Production comparison
    ax2 = axes[0, 1]
    bars2 = ax2.bar(x_pos, productions, color='lightgreen')
    ax2.set_ylabel('H₂ Production (L/min)')
    ax2.set_title('Hydrogen Production Rate')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Power comparison
    ax3 = axes[1, 0]
    bars3 = ax3.bar(x_pos, powers, color='orange')
    ax3.set_ylabel('Power (W)')
    ax3.set_title('Power Consumption')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Current density comparison
    ax4 = axes[1, 1]
    bars4 = ax4.bar(x_pos, current_densities, color='purple')
    ax4.axhspan(100, 500, alpha=0.2, color='green', label='Optimal')
    ax4.set_ylabel('Current Density (mA/cm²)')
    ax4.set_title('Current Density')
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.legend()
    
    plt.tight_layout()
    return fig


def efficiency_map(model: HydrogenGeneratorModel,
                  voltage_range: Tuple[float, float] = (6.0, 14.0),
                  current_range: Tuple[float, float] = (1.0, 30.0),
                  resolution: int = 30):
    """
    Create a 2D efficiency map varying both voltage and current.
    
    Args:
        model: Generator model
        voltage_range: (min, max) voltage
        current_range: (min, max) current
        resolution: Grid resolution
    """
    voltages = np.linspace(voltage_range[0], voltage_range[1], resolution)
    currents = np.linspace(current_range[0], current_range[1], resolution)
    
    efficiency_grid = np.zeros((resolution, resolution))
    production_grid = np.zeros((resolution, resolution))
    
    for i, v in enumerate(voltages):
        for j, c in enumerate(currents):
            analysis = model.analyze_performance(voltage=v, current=c)
            efficiency_grid[j, i] = analysis['efficiency']['efficiency_percentage']
            production_grid[j, i] = analysis['chemical']['h2_production_lpm']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Performance Map: {model.config.name}', fontsize=14, fontweight='bold')
    
    # Efficiency map
    ax1 = axes[0]
    im1 = ax1.contourf(voltages, currents, efficiency_grid, levels=20, cmap='RdYlGn')
    ax1.plot(model.config.voltage_volts, model.config.current_amperes, 
             'r*', markersize=15, label='Configured')
    ax1.set_xlabel('Voltage (V)')
    ax1.set_ylabel('Current (A)')
    ax1.set_title('Efficiency Map (%)')
    plt.colorbar(im1, ax=ax1)
    ax1.legend()
    
    # Production map
    ax2 = axes[1]
    im2 = ax2.contourf(voltages, currents, production_grid, levels=20, cmap='viridis')
    ax2.plot(model.config.voltage_volts, model.config.current_amperes,
             'r*', markersize=15, label='Configured')
    ax2.set_xlabel('Voltage (V)')
    ax2.set_ylabel('Current (A)')
    ax2.set_title('H₂ Production (L/min)')
    plt.colorbar(im2, ax=ax2)
    ax2.legend()
    
    plt.tight_layout()
    return fig


def main():
    """Example simulations."""
    # Load a configuration
    config = get_config("instructables_dry_cell")
    model = HydrogenGeneratorModel(config)
    
    print("Generating plots...")
    
    # Voltage analysis
    fig1 = plot_voltage_analysis(model)
    fig1.savefig('voltage_analysis.png', dpi=150, bbox_inches='tight')
    print("Saved: voltage_analysis.png")
    
    # Current analysis
    fig2 = plot_current_analysis(model)
    fig2.savefig('current_analysis.png', dpi=150, bbox_inches='tight')
    print("Saved: current_analysis.png")
    
    # Configuration comparison
    fig3 = compare_configurations([
        "instructables_basic",
        "instructables_adjustable",
        "instructables_dry_cell",
        "typical_small_scale"
    ])
    fig3.savefig('configuration_comparison.png', dpi=150, bbox_inches='tight')
    print("Saved: configuration_comparison.png")
    
    # Efficiency map
    fig4 = efficiency_map(model)
    fig4.savefig('efficiency_map.png', dpi=150, bbox_inches='tight')
    print("Saved: efficiency_map.png")
    
    print("\nAll plots generated successfully!")
    plt.show()


if __name__ == "__main__":
    main()
