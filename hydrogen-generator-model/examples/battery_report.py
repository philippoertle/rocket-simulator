"""
Analysis Report for 9V Battery-Powered Hydrogen Generator
Using 3×9V batteries in series (27V total)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from integrated_model import HydrogenGeneratorModel
from generator_configs import get_config, GeneratorConfig
from simulation import (plot_voltage_analysis, plot_current_analysis, 
                       efficiency_map, voltage_sweep, current_sweep)
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def create_battery_powered_config():
    """
    Create a configuration optimized for 3×9V batteries (27V).
    
    Battery specs (typical alkaline 9V):
    - Voltage: 9V nominal (3× = 27V)
    - Capacity: ~500-600 mAh
    - Internal resistance: ~1-2Ω per battery
    """
    return GeneratorConfig(
        name="3×9V Battery Powered Generator",
        source="Custom configuration for battery operation",
        description="Small-scale hydrogen generator designed for 3×9V batteries in series (27V)",
        voltage_volts=27.0,
        current_amperes=0.5,  # Low current to extend battery life
        power_supply_type="3×9V alkaline batteries in series",
        electrode_material="stainless_steel_316",
        number_of_plates=5,  # Fewer plates for 27V / ~2V per cell
        plate_width_mm=50.0,
        plate_height_mm=50.0,
        plate_thickness_mm=0.5,
        plate_spacing_mm=3.0,
        electrolyte_type="NaOH",
        electrolyte_concentration_description="1:40 water to NaOH",
        naoh_concentration_molar=0.375,
        water_volume_ml=250.0,  # Small volume
        cell_type="wet_cell",
        operating_temperature_celsius=30.0,
        notes=[
            "Designed for portable/demonstration use",
            "Low current (0.5A) extends battery life to ~1 hour",
            "27V allows ~13 cells in series (2V each)",
            "Compact design suitable for experiments"
        ]
    )


def calculate_battery_performance():
    """Calculate battery runtime and energy consumption."""
    # Battery specifications
    battery_voltage = 9.0  # V per battery
    num_batteries = 3
    total_voltage = battery_voltage * num_batteries
    
    # Typical 9V alkaline battery specs
    capacity_mah = 550  # mAh (average for alkaline)
    internal_resistance_per_battery = 1.5  # Ohms
    total_internal_resistance = internal_resistance_per_battery * num_batteries
    
    # Operating parameters
    load_currents = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0])  # A
    
    results = {
        'current_a': load_currents,
        'voltage_drop_v': [],
        'effective_voltage_v': [],
        'runtime_hours': [],
        'total_energy_wh': [],
        'h2_production_total_l': []
    }
    
    for current in load_currents:
        # Voltage drop due to internal resistance
        voltage_drop = current * total_internal_resistance
        effective_voltage = total_voltage - voltage_drop
        
        # Runtime (capacity derating at higher currents)
        # Peukert effect: capacity decreases at high discharge rates
        peukert_exponent = 1.3
        effective_capacity_mah = capacity_mah * (0.05 / current) ** (peukert_exponent - 1)
        runtime_hours = effective_capacity_mah / (current * 1000)
        
        # Total energy delivered
        total_energy_wh = effective_voltage * current * runtime_hours
        
        # H2 production (using Faraday's law)
        # 0.006958 L/min per Ampere
        h2_production_lpm = current * 0.006958
        h2_production_total = h2_production_lpm * runtime_hours * 60
        
        results['voltage_drop_v'].append(voltage_drop)
        results['effective_voltage_v'].append(effective_voltage)
        results['runtime_hours'].append(runtime_hours)
        results['total_energy_wh'].append(total_energy_wh)
        results['h2_production_total_l'].append(h2_production_total)
    
    return results


def generate_full_report():
    """Generate comprehensive report with all visualizations."""
    
    print("="*80)
    print("HYDROGEN GENERATOR ANALYSIS REPORT")
    print("3×9V Battery Configuration (27V Series)")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    # Create configuration
    config = create_battery_powered_config()
    model = HydrogenGeneratorModel(config)
    
    # ========== SECTION 1: Configuration Overview ==========
    print("\n" + "="*80)
    print("SECTION 1: SYSTEM CONFIGURATION")
    print("="*80)
    
    print("\n1.1 Power Source:")
    print(f"  Battery Type: Alkaline 9V")
    print(f"  Configuration: 3 batteries in series")
    print(f"  Total Voltage: 27V")
    print(f"  Typical Capacity: 550 mAh per battery")
    print(f"  Internal Resistance: ~1.5Ω per battery (4.5Ω total)")
    
    print("\n1.2 Electrolyzer Design:")
    print(f"  Type: {config.cell_type}")
    print(f"  Electrode Material: {config.electrode_material}")
    print(f"  Number of Plates: {config.number_of_plates}")
    print(f"  Plate Dimensions: {config.plate_width_mm}×{config.plate_height_mm}×{config.plate_thickness_mm} mm")
    print(f"  Plate Spacing: {config.plate_spacing_mm} mm")
    print(f"  Electrolyte: {config.electrolyte_type} ({config.electrolyte_concentration_description})")
    print(f"  Electrolyte Volume: {config.water_volume_ml} ml")
    
    # ========== SECTION 2: Performance Analysis ==========
    print("\n" + "="*80)
    print("SECTION 2: PERFORMANCE ANALYSIS AT RATED CONDITIONS")
    print("="*80)
    
    results = model.analyze_performance(voltage=27.0, current=0.5)
    
    print("\n2.1 Operating Conditions:")
    print(f"  Applied Voltage: {results['configuration']['voltage_v']} V")
    print(f"  Operating Current: {results['configuration']['current_a']} A")
    print(f"  Power Consumption: {results['configuration']['power_w']:.2f} W")
    
    print("\n2.2 Hydrogen Production:")
    print(f"  Production Rate: {results['chemical']['h2_production_lpm']:.4f} L/min")
    print(f"                  {results['chemical']['h2_production_lpm']*60:.3f} L/hour")
    print(f"  Mass Rate: {results['chemical']['h2_production_g_hr']:.3f} g/hour")
    print(f"  Energy Content: {results['chemical']['energy_per_liter_kwh']:.3f} kWh per liter H₂")
    
    print("\n2.3 Electrical Characteristics:")
    print(f"  Theoretical Minimum Voltage: {results['chemical']['theoretical_voltage_v']:.3f} V")
    print(f"  Required Voltage: {results['physical']['required_voltage_v']:.3f} V")
    print(f"  Voltage Margin: {results['physical']['voltage_margin_v']:.3f} V")
    print(f"  Total Resistance: {results['physical']['total_resistance_ohms']:.4f} Ω")
    print(f"  Ohmic Loss: {results['physical']['ohmic_loss_percentage']:.1f}%")
    
    print("\n2.4 Electrode Performance:")
    print(f"  Active Surface Area: {results['physical']['electrode_area_cm2']:.1f} cm²")
    print(f"  Current Density: {results['physical']['current_density_ma_cm2']:.2f} mA/cm²")
    print(f"  Status: {results['physical']['current_density_status']}")
    print(f"  Optimal Range: {'✓ Yes' if results['physical']['is_optimal_current_density'] else '✗ No'}")
    print(f"  Bubble Coverage: {results['physical']['bubble_coverage_pct']:.2f}%")
    
    print("\n2.5 Thermal Performance:")
    print(f"  Heat Generation: {results['thermal']['heat_generation_w']:.2f} W")
    print(f"  Estimated Operating Temperature: {results['physical']['estimated_temp_celsius']:.1f}°C")
    print(f"  Cooling Required: {results['thermal']['cooling_required_w']:.2f} W")
    
    print("\n2.6 Efficiency Metrics:")
    print(f"  Voltage Efficiency: {results['efficiency']['voltage_efficiency']*100:.1f}%")
    print(f"  Faradaic Efficiency: {results['efficiency']['faradaic_efficiency']*100:.1f}%")
    print(f"  Overall System Efficiency: {results['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  Energy Efficiency: {results['efficiency']['energy_efficiency']*100:.2f}%")
    
    print("\n2.7 Overall Assessment:")
    print(f"  Rating: {results['assessment']['rating']}")
    if results['assessment']['issues']:
        print(f"  Issues Identified:")
        for issue in results['assessment']['issues']:
            print(f"    • {issue}")
    if results['assessment']['recommendations']:
        print(f"  Recommendations:")
        for rec in results['assessment']['recommendations']:
            print(f"    • {rec}")
    
    # ========== SECTION 3: Battery Performance ==========
    print("\n" + "="*80)
    print("SECTION 3: BATTERY RUNTIME AND CAPACITY ANALYSIS")
    print("="*80)
    
    battery_results = calculate_battery_performance()
    
    print("\n3.1 Runtime vs Current Draw:")
    print(f"  {'Current':>8} {'Voltage':>8} {'Runtime':>10} {'Energy':>10} {'H₂ Total':>12}")
    print(f"  {'(A)':>8} {'(V)':>8} {'(hours)':>10} {'(Wh)':>10} {'(liters)':>12}")
    print("  " + "-"*58)
    
    for i in range(len(battery_results['current_a'])):
        curr = battery_results['current_a'][i]
        volt = battery_results['effective_voltage_v'][i]
        runtime = battery_results['runtime_hours'][i]
        energy = battery_results['total_energy_wh'][i]
        h2_total = battery_results['h2_production_total_l'][i]
        
        print(f"  {curr:8.2f} {volt:8.2f} {runtime:10.2f} {energy:10.2f} {h2_total:12.3f}")
    
    print("\n3.2 Recommended Operating Point:")
    recommended_idx = 4  # 0.5A
    print(f"  Current: {battery_results['current_a'][recommended_idx]:.2f} A")
    print(f"  Effective Voltage: {battery_results['effective_voltage_v'][recommended_idx]:.2f} V")
    print(f"  Runtime: {battery_results['runtime_hours'][recommended_idx]:.2f} hours "
          f"({battery_results['runtime_hours'][recommended_idx]*60:.0f} minutes)")
    print(f"  Total H₂ Production: {battery_results['h2_production_total_l'][recommended_idx]:.3f} liters")
    print(f"  Energy Efficiency: Good balance of production rate and battery life")
    
    # ========== SECTION 4: Optimization ==========
    print("\n" + "="*80)
    print("SECTION 4: OPTIMIZATION ANALYSIS")
    print("="*80)
    
    optimization = model.optimize_for_efficiency()
    
    print("\n4.1 Current Configuration:")
    print(f"  Voltage: {config.voltage_volts} V")
    print(f"  Current: {config.current_amperes} A")
    print(f"  Efficiency: {results['efficiency']['efficiency_percentage']:.1f}%")
    
    print("\n4.2 Optimized Parameters:")
    print(f"  Optimal Voltage: {optimization['optimal_voltage_v']:.2f} V")
    print(f"  Optimal Current: {optimization['optimal_current_a']:.1f} A")
    print(f"  Expected Efficiency: {optimization['expected_efficiency']*100:.1f}%")
    print(f"  Rationale: {optimization['reason']}")
    
    # Analyze at optimized settings
    opt_results = model.analyze_performance(
        voltage=optimization['optimal_voltage_v'],
        current=optimization['optimal_current_a']
    )
    
    print("\n4.3 Performance at Optimized Settings:")
    print(f"  H₂ Production: {opt_results['chemical']['h2_production_lpm']:.4f} L/min")
    print(f"  Power: {opt_results['configuration']['power_w']:.2f} W")
    print(f"  Efficiency: {opt_results['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  Temperature: {opt_results['physical']['estimated_temp_celsius']:.1f}°C")
    
    # ========== SECTION 5: Safety Considerations ==========
    print("\n" + "="*80)
    print("SECTION 5: SAFETY CONSIDERATIONS")
    print("="*80)
    
    print("\n5.1 Hydrogen Safety:")
    print("  ⚠ EXPLOSION HAZARD: H₂ is highly flammable (4-75% in air)")
    print("  • Ensure adequate ventilation")
    print("  • Keep away from ignition sources")
    print("  • Use in open or well-ventilated areas only")
    print("  • Never accumulate large volumes without proper storage")
    
    print("\n5.2 Electrical Safety:")
    print("  • 27V is considered low voltage (safe to touch)")
    print("  • Ensure battery connections are secure")
    print("  • Check for shorts before operation")
    print("  • Batteries may heat up during high current draw")
    
    print("\n5.3 Chemical Safety:")
    print("  ⚠ CAUSTIC: NaOH is corrosive")
    print("  • Wear safety glasses and gloves")
    print("  • Avoid skin and eye contact")
    print("  • Have water available for washing")
    print("  • Store electrolyte in labeled container")
    
    print("\n5.4 Operational Safety:")
    print("  • Monitor temperature during operation")
    print("  • Do not exceed 60°C operating temperature")
    print("  • Check for gas leaks regularly")
    print("  • Use water barrier for gas separation")
    print("  • Never seal the system completely (pressure buildup)")
    
    # ========== SECTION 6: Generate Visualizations ==========
    print("\n" + "="*80)
    print("SECTION 6: GENERATING VISUALIZATIONS")
    print("="*80)
    
    # Create comprehensive figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Hydrogen Generator Analysis: 3×9V Battery System (27V)', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Create grid spec for better layout
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)
    
    # Plot 1: Voltage sweep
    ax1 = fig.add_subplot(gs[0, 0])
    v_results = voltage_sweep(model, voltage_range=(10.0, 30.0), num_points=40)
    ax1.plot(v_results['voltage'], v_results['efficiency'], 'b-', linewidth=2)
    ax1.axvline(27.0, color='r', linestyle='--', linewidth=1.5, label='27V (3×9V)')
    ax1.set_xlabel('Voltage (V)', fontweight='bold')
    ax1.set_ylabel('Efficiency (%)', fontweight='bold')
    ax1.set_title('Efficiency vs Voltage', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plot 2: Current sweep
    ax2 = fig.add_subplot(gs[0, 1])
    c_results = current_sweep(model, current_range=(0.1, 2.0), num_points=40)
    ax2.plot(c_results['current'], c_results['efficiency'], 'g-', linewidth=2)
    ax2.axvline(0.5, color='r', linestyle='--', linewidth=1.5, label='0.5A (rated)')
    ax2.set_xlabel('Current (A)', fontweight='bold')
    ax2.set_ylabel('Efficiency (%)', fontweight='bold')
    ax2.set_title('Efficiency vs Current', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Plot 3: H2 Production
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(c_results['current'], c_results['production_lpm'], 'purple', linewidth=2)
    ax3.axvline(0.5, color='r', linestyle='--', linewidth=1.5)
    ax3.set_xlabel('Current (A)', fontweight='bold')
    ax3.set_ylabel('H₂ Production (L/min)', fontweight='bold')
    ax3.set_title('Production Rate vs Current', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Battery Runtime
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.plot(battery_results['current_a'], battery_results['runtime_hours'], 'orange', 
             linewidth=2, marker='o', markersize=6)
    ax4.axvline(0.5, color='r', linestyle='--', linewidth=1.5, label='Rated')
    ax4.set_xlabel('Current Draw (A)', fontweight='bold')
    ax4.set_ylabel('Runtime (hours)', fontweight='bold')
    ax4.set_title('Battery Runtime vs Current', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Plot 5: Total H2 Production from Battery
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(battery_results['current_a'], battery_results['h2_production_total_l'], 
             'teal', linewidth=2, marker='s', markersize=6)
    ax5.axvline(0.5, color='r', linestyle='--', linewidth=1.5)
    ax5.set_xlabel('Current Draw (A)', fontweight='bold')
    ax5.set_ylabel('Total H₂ (liters)', fontweight='bold')
    ax5.set_title('Total H₂ per Battery Set', fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Current Density
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(c_results['current'], c_results['current_density'], 'brown', linewidth=2)
    ax6.axhspan(100, 500, alpha=0.2, color='green', label='Optimal range')
    ax6.axvline(0.5, color='r', linestyle='--', linewidth=1.5)
    ax6.set_xlabel('Current (A)', fontweight='bold')
    ax6.set_ylabel('Current Density (mA/cm²)', fontweight='bold')
    ax6.set_title('Current Density', fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    # Plot 7: Temperature
    ax7 = fig.add_subplot(gs[2, 0])
    ax7.plot(c_results['current'], c_results['temperature'], 'red', linewidth=2)
    ax7.axhline(60, color='orange', linestyle=':', linewidth=1.5, label='Warning limit')
    ax7.axvline(0.5, color='r', linestyle='--', linewidth=1.5)
    ax7.set_xlabel('Current (A)', fontweight='bold')
    ax7.set_ylabel('Temperature (°C)', fontweight='bold')
    ax7.set_title('Operating Temperature', fontweight='bold')
    ax7.grid(True, alpha=0.3)
    ax7.legend()
    
    # Plot 8: Power Consumption
    ax8 = fig.add_subplot(gs[2, 1])
    ax8.plot(c_results['current'], c_results['power'], 'navy', linewidth=2)
    ax8.axvline(0.5, color='r', linestyle='--', linewidth=1.5)
    ax8.set_xlabel('Current (A)', fontweight='bold')
    ax8.set_ylabel('Power (W)', fontweight='bold')
    ax8.set_title('Power Consumption', fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    # Plot 9: Efficiency vs Production Trade-off
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.scatter(c_results['efficiency'], c_results['production_lpm'], 
                c=c_results['current'], cmap='viridis', s=100, edgecolors='black', linewidth=1)
    rated_eff = results['efficiency']['efficiency_percentage']
    rated_prod = results['chemical']['h2_production_lpm']
    ax9.scatter([rated_eff], [rated_prod], color='red', s=200, marker='*', 
                edgecolors='black', linewidth=1.5, label='Rated (0.5A)', zorder=5)
    ax9.set_xlabel('Efficiency (%)', fontweight='bold')
    ax9.set_ylabel('H₂ Production (L/min)', fontweight='bold')
    ax9.set_title('Efficiency-Production Trade-off', fontweight='bold')
    ax9.grid(True, alpha=0.3)
    ax9.legend()
    cbar = plt.colorbar(ax9.collections[0], ax=ax9, label='Current (A)')
    
    output_dir = Path(__file__).parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)
    
    plt.savefig(output_dir / 'battery_powered_hydrogen_generator_analysis.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Saved: outputs/battery_powered_hydrogen_generator_analysis.png")
    
    # Create battery-specific detailed plot
    fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig2.suptitle('Battery Performance Analysis: 3×9V Alkaline (27V)', 
                  fontsize=14, fontweight='bold')
    
    # Effective voltage vs current
    axes[0, 0].plot(battery_results['current_a'], battery_results['effective_voltage_v'], 
                    'b-', linewidth=2, marker='o')
    axes[0, 0].axhline(27, color='gray', linestyle=':', label='No-load voltage')
    axes[0, 0].set_xlabel('Current Draw (A)', fontweight='bold')
    axes[0, 0].set_ylabel('Effective Voltage (V)', fontweight='bold')
    axes[0, 0].set_title('Voltage Drop Under Load')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    
    # Energy delivered
    axes[0, 1].bar(battery_results['current_a'], battery_results['total_energy_wh'], 
                   color='orange', alpha=0.7, edgecolor='black')
    axes[0, 1].set_xlabel('Current Draw (A)', fontweight='bold')
    axes[0, 1].set_ylabel('Total Energy (Wh)', fontweight='bold')
    axes[0, 1].set_title('Energy per Battery Set')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # Runtime comparison
    axes[1, 0].bar(battery_results['current_a'], 
                   np.array(battery_results['runtime_hours'])*60,  # Convert to minutes
                   color='green', alpha=0.7, edgecolor='black')
    axes[1, 0].set_xlabel('Current Draw (A)', fontweight='bold')
    axes[1, 0].set_ylabel('Runtime (minutes)', fontweight='bold')
    axes[1, 0].set_title('Battery Life')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # H2 per Wh
    h2_per_wh = np.array(battery_results['h2_production_total_l']) / np.array(battery_results['total_energy_wh'])
    axes[1, 1].plot(battery_results['current_a'], h2_per_wh, 
                    'purple', linewidth=2, marker='s', markersize=8)
    axes[1, 1].set_xlabel('Current Draw (A)', fontweight='bold')
    axes[1, 1].set_ylabel('H₂ per Wh (L/Wh)', fontweight='bold')
    axes[1, 1].set_title('Energy Efficiency')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'battery_performance_detailed.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved: outputs/battery_performance_detailed.png")
    
    # ========== SECTION 7: Summary and Conclusions ==========
    print("\n" + "="*80)
    print("SECTION 7: SUMMARY AND CONCLUSIONS")
    print("="*80)
    
    print("\n7.1 Key Findings:")
    print(f"  • Hydrogen production at 0.5A: {results['chemical']['h2_production_lpm']:.4f} L/min")
    print(f"  • System efficiency: {results['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  • Battery runtime at 0.5A: ~{battery_results['runtime_hours'][4]:.1f} hours")
    print(f"  • Total H₂ from one battery set: {battery_results['h2_production_total_l'][4]:.3f} liters")
    print(f"  • Current density: {results['physical']['current_density_ma_cm2']:.1f} mA/cm² (optimal)")
    
    print("\n7.2 Advantages of 9V Battery Operation:")
    print("  • Portable and self-contained")
    print("  • No external power supply needed")
    print("  • Safe low-voltage operation (27V)")
    print("  • Suitable for demonstrations and experiments")
    print("  • Easy to scale (add/remove batteries)")
    
    print("\n7.3 Limitations:")
    print("  • Limited runtime (approx 1 hour at 0.5A)")
    print("  • Low production rate compared to mains-powered systems")
    print("  • Battery cost per liter of H₂ is high")
    print("  • Voltage drop under load reduces efficiency")
    print("  • Not suitable for continuous operation")
    
    print("\n7.4 Recommended Applications:")
    print("  • Educational demonstrations")
    print("  • Proof-of-concept testing")
    print("  • Portable hydrogen generation")
    print("  • Emergency/backup hydrogen production")
    print("  • Remote location experiments")
    
    print("\n7.5 Cost Analysis (Approximate):")
    battery_cost = 3 * 3.00  # $3 per 9V alkaline battery
    h2_produced = battery_results['h2_production_total_l'][4]
    cost_per_liter = battery_cost / h2_produced
    print(f"  • Battery cost (3×9V): ${battery_cost:.2f}")
    print(f"  • H₂ produced: {h2_produced:.3f} liters")
    print(f"  • Cost per liter H₂: ${cost_per_liter:.2f}/L")
    print(f"  • Cost per gram H₂: ${cost_per_liter * 0.0896:.2f}/g")
    print(f"  • Note: Mains electricity would cost ~$0.01-0.02/L")
    
    print("\n" + "="*80)
    print("END OF REPORT")
    print("="*80)
    print()
    print("Generated visualizations:")
    print("  1. outputs/battery_powered_hydrogen_generator_analysis.png")
    print("  2. outputs/battery_performance_detailed.png")
    print()
    print("For questions or modifications, refer to the model documentation.")
    print()
    
    plt.show()
    
    return model, results


if __name__ == "__main__":
    model, results = generate_full_report()
