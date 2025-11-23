"""
Example usage scripts for the hydrogen generator model.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from integrated_model import HydrogenGeneratorModel
from generator_configs import get_config, list_configs, print_config_summary


def example_1_basic_analysis():
    """Example 1: Basic performance analysis of a configuration."""
    print("="*70)
    print("EXAMPLE 1: Basic Performance Analysis")
    print("="*70 + "\n")
    
    # Load and analyze a dry cell configuration
    config = get_config("instructables_dry_cell")
    model = HydrogenGeneratorModel(config)
    
    # Run analysis at configured parameters
    results = model.analyze_performance()
    
    # Print key results
    print(f"Generator: {config.name}")
    print(f"Operating: {results['configuration']['voltage_v']}V, {results['configuration']['current_a']}A\n")
    
    print("Production:")
    print(f"  {results['chemical']['h2_production_lpm']:.3f} L/min")
    print(f"  {results['chemical']['h2_production_lph']:.2f} L/hr")
    print(f"  {results['chemical']['h2_production_g_hr']:.2f} g/hr\n")
    
    print("Efficiency:")
    print(f"  Overall: {results['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  Energy: {results['chemical']['energy_per_liter_kwh']:.3f} kWh/L H₂\n")
    
    print("Assessment:")
    print(f"  Rating: {results['assessment']['rating']}")
    if results['assessment']['recommendations']:
        print("  Recommendations:")
        for rec in results['assessment']['recommendations']:
            print(f"    - {rec}")
    print()


def example_2_parameter_variation():
    """Example 2: Analyze effect of varying voltage."""
    print("="*70)
    print("EXAMPLE 2: Voltage Variation Analysis")
    print("="*70 + "\n")
    
    config = get_config("typical_small_scale")
    model = HydrogenGeneratorModel(config)
    
    print(f"Generator: {config.name}")
    print(f"Testing voltages from 6V to 14V at {config.current_amperes}A\n")
    
    print(f"{'Voltage':>8} {'Efficiency':>10} {'Production':>12} {'Temperature':>12}")
    print(f"{'(V)':>8} {'(%)':>10} {'(L/min)':>12} {'(°C)':>12}")
    print("-" * 46)
    
    for voltage in range(6, 15, 2):
        results = model.analyze_performance(voltage=float(voltage))
        eff = results['efficiency']['efficiency_percentage']
        prod = results['chemical']['h2_production_lpm']
        temp = results['physical']['estimated_temp_celsius']
        print(f"{voltage:8.1f} {eff:10.1f} {prod:12.3f} {temp:12.1f}")
    print()


def example_3_optimization():
    """Example 3: Find optimal operating parameters."""
    print("="*70)
    print("EXAMPLE 3: Parameter Optimization")
    print("="*70 + "\n")
    
    config = get_config("instructables_adjustable")
    model = HydrogenGeneratorModel(config)
    
    print(f"Generator: {config.name}")
    print(f"Current configuration: {config.voltage_volts}V, {config.current_amperes}A\n")
    
    # Get current performance
    current_perf = model.analyze_performance()
    print("Current Performance:")
    print(f"  Efficiency: {current_perf['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  Production: {current_perf['chemical']['h2_production_lpm']:.3f} L/min")
    print(f"  Rating: {current_perf['assessment']['rating']}\n")
    
    # Get optimization suggestions
    optimization = model.optimize_for_efficiency()
    print("Optimized Parameters:")
    print(f"  Voltage: {optimization['optimal_voltage_v']:.2f} V")
    print(f"  Current: {optimization['optimal_current_a']:.1f} A")
    print(f"  Expected efficiency: {optimization['expected_efficiency']*100:.1f}%")
    print(f"  Reason: {optimization['reason']}\n")
    
    # Analyze optimized performance
    opt_perf = model.analyze_performance(
        voltage=optimization['optimal_voltage_v'],
        current=optimization['optimal_current_a']
    )
    print("Optimized Performance:")
    print(f"  Efficiency: {opt_perf['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  Production: {opt_perf['chemical']['h2_production_lpm']:.3f} L/min")
    print(f"  Rating: {opt_perf['assessment']['rating']}")
    print()


def example_4_configuration_comparison():
    """Example 4: Compare different generator designs."""
    print("="*70)
    print("EXAMPLE 4: Design Comparison")
    print("="*70 + "\n")
    
    configs_to_compare = [
        "instructables_basic",
        "typical_small_scale",
        "instructables_dry_cell",
        "instructables_razor_blade"
    ]
    
    print(f"{'Configuration':<30} {'Power':>8} {'Prod.':>8} {'Eff.':>8} {'Rating':>10}")
    print(f"{'':30} {'(W)':>8} {'(L/m)':>8} {'(%)':>8} {'':>10}")
    print("-" * 74)
    
    for config_name in configs_to_compare:
        config = get_config(config_name)
        model = HydrogenGeneratorModel(config)
        results = model.analyze_performance()
        
        name_short = config.name[:28]
        power = results['configuration']['power_w']
        prod = results['chemical']['h2_production_lpm']
        eff = results['efficiency']['efficiency_percentage']
        rating = results['assessment']['rating']
        
        print(f"{name_short:<30} {power:8.1f} {prod:8.3f} {eff:8.1f} {rating:>10}")
    print()


def example_5_material_comparison():
    """Example 5: Compare electrode materials (simplified)."""
    print("="*70)
    print("EXAMPLE 5: Electrode Material Properties")
    print("="*70 + "\n")
    
    from generator_configs import ELECTRODE_MATERIALS
    
    print(f"{'Material':<25} {'Cost':>8} {'Corrosion':>15} {'Lifetime':>10}")
    print(f"{'':25} {'(rel)':>8} {'Resistance':>15} {'(hours)':>10}")
    print("-" * 60)
    
    for material, props in ELECTRODE_MATERIALS.items():
        print(f"{material:<25} {props['cost_relative']:8.1f} "
              f"{props['corrosion_resistance']:>15} {props['lifetime_hours']:10d}")
        print(f"  Note: {props['notes']}")
    print()


def example_6_detailed_breakdown():
    """Example 6: Detailed voltage loss breakdown."""
    print("="*70)
    print("EXAMPLE 6: Detailed Voltage Loss Analysis")
    print("="*70 + "\n")
    
    config = get_config("instructables_dry_cell")
    model = HydrogenGeneratorModel(config)
    
    voltage = config.voltage_volts
    current = config.current_amperes
    
    print(f"Generator: {config.name}")
    print(f"Operating: {voltage}V, {current}A\n")
    
    # Get detailed analysis
    electrolyte_conductivity = model.chemical_model.electrolyte_conductivity(
        config.naoh_concentration_molar
    )
    
    voltage_breakdown = model.physical_model.required_voltage(
        current, electrolyte_conductivity
    )
    
    losses = model.physical_model.voltage_losses(current, electrolyte_conductivity)
    
    print("Voltage Breakdown:")
    print(f"  Theoretical minimum:    {voltage_breakdown['theoretical_voltage_v']:6.3f} V")
    print(f"  Activation losses:      {losses['activation_overpotential_v']:6.3f} V "
          f"({voltage_breakdown['activation_percentage']:.1f}%)")
    print(f"    - Cathode:           {losses['activation_cathode_v']:6.3f} V")
    print(f"    - Anode:             {losses['activation_anode_v']:6.3f} V")
    print(f"  Ohmic losses:           {losses['ohmic_loss_v']:6.3f} V "
          f"({voltage_breakdown['ohmic_percentage']:.1f}%)")
    print(f"  Concentration losses:   {losses['concentration_overpotential_v']:6.3f} V "
          f"({voltage_breakdown['concentration_percentage']:.1f}%)")
    print(f"  {'─' * 40}")
    print(f"  Required voltage:       {voltage_breakdown['total_required_voltage_v']:6.3f} V")
    print(f"  Applied voltage:        {voltage:6.3f} V")
    print(f"  Margin:                 {voltage - voltage_breakdown['total_required_voltage_v']:6.3f} V")
    print()


def example_7_all_configs():
    """Example 7: List all available configurations."""
    print("="*70)
    print("EXAMPLE 7: Available Generator Configurations")
    print("="*70 + "\n")
    
    configs = list_configs()
    
    print(f"Total configurations available: {len(configs)}\n")
    
    for i, config_name in enumerate(configs, 1):
        config = get_config(config_name)
        print(f"{i}. {config.name}")
        print(f"   Source: {config.source}")
        print(f"   Type: {config.cell_type}, {config.electrode_material}")
        print(f"   Power: {config.voltage_volts}V × {config.current_amperes}A = "
              f"{config.voltage_volts * config.current_amperes}W")
        print()


def main():
    """Run all examples."""
    examples = [
        example_1_basic_analysis,
        example_2_parameter_variation,
        example_3_optimization,
        example_4_configuration_comparison,
        example_5_material_comparison,
        example_6_detailed_breakdown,
        example_7_all_configs,
    ]
    
    for example_func in examples:
        example_func()
        input("Press Enter to continue to next example...")
        print("\n\n")


if __name__ == "__main__":
    main()
