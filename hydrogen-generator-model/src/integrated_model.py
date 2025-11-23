"""
Integrated Hydrogen Generator Efficiency Model

This module combines chemical and physical models to simulate
complete hydrogen generator performance.
"""

from typing import Dict
from chemical_model import ChemicalModel
from physical_model import PhysicalModel, ElectrodeConfig
from generator_configs import GeneratorConfig


class HydrogenGeneratorModel:
    """Complete model integrating chemical and physical aspects."""
    
    def __init__(self, config: GeneratorConfig):
        """
        Initialize complete model from a generator configuration.
        
        Args:
            config: Generator configuration
        """
        self.config = config
        
        # Initialize chemical model
        self.chemical_model = ChemicalModel(
            temperature_celsius=config.operating_temperature_celsius,
            pressure_atm=1.0
        )
        
        # Initialize physical model
        electrode_config = ElectrodeConfig(
            material=config.electrode_material,
            number_of_plates=config.number_of_plates,
            plate_width_mm=config.plate_width_mm,
            plate_height_mm=config.plate_height_mm,
            plate_thickness_mm=config.plate_thickness_mm,
            plate_spacing_mm=config.plate_spacing_mm
        )
        
        self.physical_model = PhysicalModel(
            electrode_config=electrode_config,
            temperature_celsius=config.operating_temperature_celsius
        )
        
    def analyze_performance(self, voltage: float | None = None, 
                           current: float | None = None) -> Dict:
        """
        Complete performance analysis of the generator.
        
        Args:
            voltage: Applied voltage (uses config default if None)
            current: Operating current (uses config default if None)
            
        Returns:
            Dictionary with complete analysis
        """
        voltage = voltage or self.config.voltage_volts
        current = current or self.config.current_amperes
        
        # Chemical analysis
        theoretical_v = self.chemical_model.theoretical_voltage()
        thermoneutral_v = self.chemical_model.thermoneutral_voltage()
        thermo_efficiency = self.chemical_model.theoretical_efficiency(voltage)
        
        production = self.chemical_model.actual_production_rate(
            current, faradaic_efficiency=0.95
        )
        
        power = self.chemical_model.power_consumption(voltage, current)
        thermal = self.chemical_model.thermal_effects(voltage, current)
        
        electrolyte_conductivity = self.chemical_model.electrolyte_conductivity(
            self.config.naoh_concentration_molar
        )
        
        # Physical analysis
        area = self.physical_model.electrode_surface_area()
        current_density = self.physical_model.current_density(current)
        resistance = self.physical_model.ohmic_resistance(electrolyte_conductivity)
        voltage_analysis = self.physical_model.required_voltage(
            current, electrolyte_conductivity, theoretical_v
        )
        bubbles = self.physical_model.bubble_effects(current)
        temp_effects = self.physical_model.temperature_effects(
            current, voltage, ambient_temp_celsius=25.0
        )
        
        # Calculate overall efficiency
        voltage_efficiency = theoretical_v / voltage
        faradaic_efficiency = 0.95  # Assume 95% Faradaic efficiency
        overall_efficiency = voltage_efficiency * faradaic_efficiency
        
        # Energy metrics
        h2_energy_content_lhv = 33.33  # kWh/kg Lower Heating Value
        h2_production_kg_hr = production['grams_per_hour'] / 1000
        h2_energy_produced_kw = (h2_production_kg_hr * h2_energy_content_lhv) / 1.0  # per hour
        
        energy_efficiency = (h2_energy_produced_kw / (power['power_kw'] if power['power_kw'] > 0 else 1))
        
        return {
            'configuration': {
                'name': self.config.name,
                'voltage_v': voltage,
                'current_a': current,
                'power_w': voltage * current,
            },
            'chemical': {
                'theoretical_voltage_v': theoretical_v,
                'thermoneutral_voltage_v': thermoneutral_v,
                'thermodynamic_efficiency': thermo_efficiency,
                'h2_production_lpm': production['liters_per_minute_stp'],
                'h2_production_lph': production['liters_per_hour_stp'],
                'h2_production_g_hr': production['grams_per_hour'],
                'energy_per_liter_kwh': power['energy_kwh_per_liter_h2'],
                'electrolyte_conductivity_sm': electrolyte_conductivity,
            },
            'physical': {
                'electrode_area_cm2': area['total_active_area_cm2'],
                'current_density_ma_cm2': current_density['current_density_ma_cm2'],
                'current_density_status': current_density['status'],
                'is_optimal_current_density': current_density['is_optimal'],
                'total_resistance_ohms': resistance['total_ohmic_resistance_ohms'],
                'required_voltage_v': voltage_analysis['total_required_voltage_v'],
                'voltage_margin_v': voltage - voltage_analysis['total_required_voltage_v'],
                'ohmic_loss_percentage': voltage_analysis['ohmic_percentage'],
                'bubble_coverage_pct': bubbles['bubble_coverage_fraction'] * 100,
                'estimated_temp_celsius': temp_effects['estimated_operating_temp_celsius'],
            },
            'efficiency': {
                'voltage_efficiency': voltage_efficiency,
                'faradaic_efficiency': faradaic_efficiency,
                'overall_efficiency': overall_efficiency,
                'energy_efficiency': energy_efficiency,
                'efficiency_percentage': overall_efficiency * 100,
            },
            'thermal': {
                'heat_generation_w': thermal['heat_generation_watts'],
                'cooling_required_w': thermal['cooling_required_watts'],
                'temperature_rise_estimate_c': temp_effects['temp_rise_per_hour_celsius'],
            },
            'assessment': self._assess_performance(
                current_density['is_optimal'],
                overall_efficiency,
                voltage - voltage_analysis['total_required_voltage_v'],
                temp_effects['estimated_operating_temp_celsius']
            )
        }
    
    def _assess_performance(self, optimal_cd: bool, efficiency: float,
                           voltage_margin: float, temperature: float) -> Dict:
        """Assess overall performance and provide recommendations."""
        issues = []
        recommendations = []
        
        if not optimal_cd:
            issues.append("Current density outside optimal range")
            recommendations.append("Adjust current or electrode area")
        
        if efficiency < 0.4:
            issues.append("Low efficiency")
            recommendations.append("Reduce voltage or improve electrolyte")
        
        if voltage_margin < 0:
            issues.append("Insufficient voltage")
            recommendations.append("Increase applied voltage")
        elif voltage_margin > 5:
            issues.append("Excessive voltage")
            recommendations.append("Reduce voltage to improve efficiency")
        
        if temperature > 60:
            issues.append("High operating temperature")
            recommendations.append("Add cooling or reduce power")
        elif temperature < 30:
            issues.append("Low temperature")
            recommendations.append("Allow warmup for better efficiency")
        
        rating = "Excellent" if len(issues) == 0 else \
                 "Good" if len(issues) <= 1 else \
                 "Fair" if len(issues) <= 2 else "Poor"
        
        return {
            'rating': rating,
            'issues': issues,
            'recommendations': recommendations,
        }
    
    def optimize_for_efficiency(self) -> Dict:
        """
        Suggest optimal operating parameters for maximum efficiency.
        
        Returns:
            Dictionary with optimization suggestions
        """
        # Find minimum voltage needed
        electrolyte_conductivity = self.chemical_model.electrolyte_conductivity(
            self.config.naoh_concentration_molar
        )
        
        theoretical_v = self.chemical_model.theoretical_voltage()
        
        # Try different currents to find optimal current density
        optimal_current = None
        for test_current in range(1, 51):
            cd = self.physical_model.current_density(test_current)
            if cd['is_optimal']:
                optimal_current = test_current
                break
        
        if optimal_current is None:
            optimal_current = self.config.current_amperes
        
        voltage_analysis = self.physical_model.required_voltage(
            optimal_current, electrolyte_conductivity, theoretical_v
        )
        
        optimal_voltage = voltage_analysis['total_required_voltage_v'] + 0.5  # Add margin
        
        return {
            'optimal_voltage_v': optimal_voltage,
            'optimal_current_a': optimal_current,
            'expected_efficiency': theoretical_v / optimal_voltage,
            'reason': f"Voltage margin of 0.5V above minimum, current density in optimal range"
        }
    
    def compare_with_config(self) -> Dict:
        """Compare actual performance with configuration specifications."""
        actual = self.analyze_performance()
        
        comparison = {
            'configured_voltage': self.config.voltage_volts,
            'required_voltage': actual['physical']['required_voltage_v'],
            'configured_current': self.config.current_amperes,
            'configured_power': self.config.voltage_volts * self.config.current_amperes,
            'efficiency': actual['efficiency']['efficiency_percentage'],
            'production_rate_lpm': actual['chemical']['h2_production_lpm'],
        }
        
        if self.config.reported_production_lpm > 0:
            comparison['reported_production_lpm'] = self.config.reported_production_lpm
            comparison['production_match_percentage'] = (
                actual['chemical']['h2_production_lpm'] / 
                self.config.reported_production_lpm * 100
            )
        
        return comparison


def main():
    """Example usage of integrated model."""
    from generator_configs import get_config
    
    # Analyze a specific configuration
    config = get_config("instructables_dry_cell")
    
    print(f"=== Analysis of {config.name} ===\n")
    
    model = HydrogenGeneratorModel(config)
    results = model.analyze_performance()
    
    print("Configuration:")
    print(f"  Voltage: {results['configuration']['voltage_v']} V")
    print(f"  Current: {results['configuration']['current_a']} A")
    print(f"  Power: {results['configuration']['power_w']} W\n")
    
    print("Chemical Performance:")
    print(f"  H₂ Production: {results['chemical']['h2_production_lpm']:.3f} L/min")
    print(f"  H₂ Production: {results['chemical']['h2_production_lph']:.2f} L/hr")
    print(f"  Energy consumption: {results['chemical']['energy_per_liter_kwh']:.3f} kWh/L\n")
    
    print("Physical Performance:")
    print(f"  Electrode area: {results['physical']['electrode_area_cm2']:.1f} cm²")
    print(f"  Current density: {results['physical']['current_density_ma_cm2']:.1f} mA/cm²")
    print(f"  Status: {results['physical']['current_density_status']}")
    print(f"  Resistance: {results['physical']['total_resistance_ohms']:.4f} Ω")
    print(f"  Required voltage: {results['physical']['required_voltage_v']:.2f} V")
    print(f"  Voltage margin: {results['physical']['voltage_margin_v']:.2f} V\n")
    
    print("Efficiency:")
    print(f"  Overall: {results['efficiency']['efficiency_percentage']:.1f}%")
    print(f"  Voltage efficiency: {results['efficiency']['voltage_efficiency']*100:.1f}%")
    print(f"  Energy efficiency: {results['efficiency']['energy_efficiency']*100:.1f}%\n")
    
    print("Thermal:")
    print(f"  Heat generation: {results['thermal']['heat_generation_w']:.1f} W")
    print(f"  Operating temperature: {results['physical']['estimated_temp_celsius']:.1f}°C\n")
    
    print("Assessment:")
    print(f"  Rating: {results['assessment']['rating']}")
    if results['assessment']['issues']:
        print(f"  Issues:")
        for issue in results['assessment']['issues']:
            print(f"    - {issue}")
    if results['assessment']['recommendations']:
        print(f"  Recommendations:")
        for rec in results['assessment']['recommendations']:
            print(f"    - {rec}")
    
    print("\n" + "="*60)
    print("Optimization Suggestions:\n")
    
    optimization = model.optimize_for_efficiency()
    print(f"  Optimal voltage: {optimization['optimal_voltage_v']:.2f} V")
    print(f"  Optimal current: {optimization['optimal_current_a']:.1f} A")
    print(f"  Expected efficiency: {optimization['expected_efficiency']*100:.1f}%")
    print(f"  Reason: {optimization['reason']}")


if __name__ == "__main__":
    main()
