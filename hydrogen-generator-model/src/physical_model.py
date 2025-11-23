"""
Physical Model for Hydrogen Generator Design

This module implements physical aspects of electrolyzer design including:
- Electrode geometry and surface area
- Current density calculations
- Ohmic resistance and voltage losses
- Temperature effects on performance
- Gas bubble dynamics

Based on DIY designs from multiple sources including dry cell and wet cell configurations.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ElectrodeConfig:
    """Configuration for electrode geometry."""
    material: str  # "stainless_steel_316", "graphite", "platinum", "razor_blade"
    number_of_plates: int
    plate_width_mm: float
    plate_height_mm: float
    plate_thickness_mm: float
    plate_spacing_mm: float
    active_area_percentage: float = 0.85  # Account for edge effects


class PhysicalModel:
    """Physical model for electrolyzer design and performance."""
    
    # Material resistivities (Ω·m at 20°C)
    MATERIAL_RESISTIVITY = {
        'stainless_steel_316': 7.4e-7,
        'stainless_steel_304': 7.2e-7,
        'graphite': 8.0e-6,
        'platinum': 1.06e-7,
        'razor_blade': 7.5e-7,  # Similar to stainless steel
    }
    
    # Temperature coefficients for resistivity (per °C)
    TEMP_COEFFICIENT = {
        'stainless_steel_316': 0.00094,
        'stainless_steel_304': 0.00095,
        'graphite': -0.0005,  # Negative coefficient
        'platinum': 0.00392,
        'razor_blade': 0.00094,
    }
    
    def __init__(self, electrode_config: ElectrodeConfig, 
                 temperature_celsius: float = 25.0):
        """
        Initialize physical model.
        
        Args:
            electrode_config: Electrode configuration
            temperature_celsius: Operating temperature in Celsius
        """
        self.config = electrode_config
        self.temperature_celsius = temperature_celsius
        
    def electrode_surface_area(self) -> Dict[str, float]:
        """
        Calculate total active electrode surface area.
        
        Returns:
            Dictionary with area measurements
        """
        # Area per plate (both sides)
        area_per_plate_cm2 = (self.config.plate_width_mm / 10) * \
                             (self.config.plate_height_mm / 10) * 2
        
        # Account for edge effects and inactive areas
        active_area_per_plate = area_per_plate_cm2 * self.config.active_area_percentage
        
        # Total active area (subtract end plates that only have one active side)
        num_active_sides = self.config.number_of_plates * 2 - 2
        total_active_area_cm2 = active_area_per_plate * (num_active_sides / 2)
        
        return {
            'area_per_plate_cm2': area_per_plate_cm2,
            'active_area_per_plate_cm2': active_area_per_plate,
            'total_active_area_cm2': total_active_area_cm2,
            'total_active_area_m2': total_active_area_cm2 / 10000,
        }
    
    def current_density(self, current_amperes: float) -> Dict:
        """
        Calculate current density on electrodes.
        
        Optimal current density for alkaline electrolysis: 100-500 mA/cm²
        
        Args:
            current_amperes: Total current in amperes
            
        Returns:
            Dictionary with current density values
        """
        area = self.electrode_surface_area()
        total_area_cm2 = area['total_active_area_cm2']
        
        current_density_ma_cm2 = (current_amperes * 1000) / total_area_cm2
        current_density_a_m2 = current_amperes / area['total_active_area_m2']
        
        # Assess if current density is in optimal range
        optimal = 100 <= current_density_ma_cm2 <= 500
        
        return {
            'current_density_ma_cm2': current_density_ma_cm2,
            'current_density_a_cm2': current_amperes / total_area_cm2,
            'current_density_a_m2': current_density_a_m2,
            'is_optimal': optimal,
            'status': self._assess_current_density(current_density_ma_cm2),
        }
    
    def _assess_current_density(self, cd_ma_cm2: float) -> str:
        """Assess current density value."""
        if cd_ma_cm2 < 50:
            return "Too low - inefficient"
        elif cd_ma_cm2 < 100:
            return "Low - acceptable"
        elif cd_ma_cm2 <= 500:
            return "Optimal range"
        elif cd_ma_cm2 <= 1000:
            return "High - increased heat"
        else:
            return "Very high - potential damage"
    
    def ohmic_resistance(self, electrolyte_conductivity: float) -> Dict[str, float]:
        """
        Calculate ohmic resistance in the electrolyzer.
        
        R = ρL/A where:
        - ρ is resistivity (1/conductivity)
        - L is electrode spacing
        - A is cross-sectional area
        
        Args:
            electrolyte_conductivity: Conductivity in S/m
            
        Returns:
            Dictionary with resistance values
        """
        # Electrolyte resistance (main contributor)
        spacing_m = self.config.plate_spacing_mm / 1000
        area_m2 = (self.config.plate_width_mm / 1000) * (self.config.plate_height_mm / 1000)
        
        resistivity = 1 / electrolyte_conductivity if electrolyte_conductivity > 0 else float('inf')
        
        # Number of gaps between plates
        num_gaps = self.config.number_of_plates - 1
        
        # Resistance per gap
        resistance_per_gap = (resistivity * spacing_m) / area_m2
        
        # For series configuration (typical in dry cell)
        # Total resistance is sum of all gaps
        total_electrolyte_resistance = resistance_per_gap * num_gaps
        
        # Electrode resistance (usually negligible compared to electrolyte)
        electrode_resistivity = self.MATERIAL_RESISTIVITY.get(
            self.config.material, 7.5e-7
        )
        
        # Temperature correction for electrode
        temp_coeff = self.TEMP_COEFFICIENT.get(self.config.material, 0.001)
        electrode_resistivity_corrected = electrode_resistivity * \
            (1 + temp_coeff * (self.temperature_celsius - 20))
        
        # Path length through electrodes (rough estimate)
        path_length_m = (self.config.plate_thickness_mm / 1000) * self.config.number_of_plates
        electrode_cross_section_m2 = (self.config.plate_height_mm / 1000) * \
                                      (self.config.plate_thickness_mm / 1000)
        
        electrode_resistance = (electrode_resistivity_corrected * path_length_m) / \
                              electrode_cross_section_m2
        
        total_resistance = total_electrolyte_resistance + electrode_resistance
        
        return {
            'electrolyte_resistance_ohms': total_electrolyte_resistance,
            'electrode_resistance_ohms': electrode_resistance,
            'total_ohmic_resistance_ohms': total_resistance,
            'resistance_per_gap_ohms': resistance_per_gap,
            'num_gaps': num_gaps,
        }
    
    def voltage_losses(self, current_amperes: float, 
                      electrolyte_conductivity: float) -> Dict[str, float]:
        """
        Calculate various voltage losses in the electrolyzer.
        
        Total voltage = Theoretical + Activation + Ohmic + Concentration overpotentials
        
        Args:
            current_amperes: Operating current in amperes
            electrolyte_conductivity: Electrolyte conductivity in S/m
            
        Returns:
            Dictionary with voltage components
        """
        # Ohmic losses (V = IR)
        resistance = self.ohmic_resistance(electrolyte_conductivity)
        ohmic_loss = current_amperes * resistance['total_ohmic_resistance_ohms']
        
        # Activation overpotential (Tafel equation approximation)
        # η_act ≈ a + b*log(j/j₀)
        # For stainless steel in alkaline solution
        cd = self.current_density(current_amperes)
        j = cd['current_density_ma_cm2']
        
        # Exchange current density (j₀) - material dependent
        j0_cathode = 0.1  # mA/cm² for H2 evolution on stainless steel
        j0_anode = 1.0    # mA/cm² for O2 evolution on stainless steel
        
        # Tafel slopes (mV/decade)
        b_cathode = 120  # mV
        b_anode = 60     # mV
        
        activation_cathode = (b_cathode / 1000) * np.log10(max(j / j0_cathode, 1))
        activation_anode = (b_anode / 1000) * np.log10(max(j / j0_anode, 1))
        activation_loss = activation_cathode + activation_anode
        
        # Concentration overpotential (simplified)
        # Becomes significant at high current densities
        # η_conc ≈ (RT/nF) * ln(1/(1-j/j_lim))
        j_limiting = 2000  # mA/cm² approximate limiting current density
        
        if j < 0.8 * j_limiting:
            concentration_loss = 0.026 * np.log(1 / (1 - j / j_limiting))
        else:
            concentration_loss = 0.05  # Approximate for high current
        
        return {
            'ohmic_loss_v': ohmic_loss,
            'activation_overpotential_v': activation_loss,
            'activation_cathode_v': activation_cathode,
            'activation_anode_v': activation_anode,
            'concentration_overpotential_v': concentration_loss,
            'total_overpotential_v': ohmic_loss + activation_loss + concentration_loss,
        }
    
    def required_voltage(self, current_amperes: float, 
                        electrolyte_conductivity: float,
                        theoretical_voltage: float = 1.23) -> Dict[str, float]:
        """
        Calculate required voltage for operation.
        
        Args:
            current_amperes: Operating current
            electrolyte_conductivity: Conductivity in S/m
            theoretical_voltage: Minimum thermodynamic voltage
            
        Returns:
            Dictionary with voltage breakdown
        """
        losses = self.voltage_losses(current_amperes, electrolyte_conductivity)
        
        total_required = theoretical_voltage + losses['total_overpotential_v']
        
        return {
            'theoretical_voltage_v': theoretical_voltage,
            'overpotential_v': losses['total_overpotential_v'],
            'total_required_voltage_v': total_required,
            'ohmic_percentage': (losses['ohmic_loss_v'] / total_required * 100),
            'activation_percentage': (losses['activation_overpotential_v'] / total_required * 100),
            'concentration_percentage': (losses['concentration_overpotential_v'] / total_required * 100),
        }
    
    def bubble_effects(self, current_amperes: float) -> Dict:
        """
        Estimate effects of gas bubble formation on efficiency.
        
        Bubbles on electrode surface reduce effective area and increase resistance.
        
        Args:
            current_amperes: Operating current
            
        Returns:
            Dictionary with bubble effect estimates
        """
        cd = self.current_density(current_amperes)
        j = cd['current_density_ma_cm2']
        
        # Bubble coverage increases with current density
        # Empirical relationship (approximate)
        bubble_coverage_fraction = min(0.3, 0.0001 * j ** 1.2)
        
        # Effective area reduction
        area_reduction_percentage = bubble_coverage_fraction * 100
        
        # Resistance increase due to bubbles
        resistance_increase_percentage = area_reduction_percentage * 1.5
        
        return {
            'bubble_coverage_fraction': bubble_coverage_fraction,
            'area_reduction_percentage': area_reduction_percentage,
            'resistance_increase_percentage': resistance_increase_percentage,
            'recommendation': self._bubble_recommendation(bubble_coverage_fraction),
        }
    
    def _bubble_recommendation(self, coverage: float) -> str:
        """Provide recommendation based on bubble coverage."""
        if coverage < 0.05:
            return "Minimal bubble interference"
        elif coverage < 0.15:
            return "Moderate bubble formation - consider agitation"
        else:
            return "Significant bubble coverage - add agitation or reduce current"
    
    def temperature_effects(self, current_amperes: float, voltage: float,
                           ambient_temp_celsius: float = 25.0) -> Dict:
        """
        Estimate temperature rise and thermal effects.
        
        Args:
            current_amperes: Operating current
            voltage: Applied voltage
            ambient_temp_celsius: Ambient temperature
            
        Returns:
            Dictionary with temperature data
        """
        # Heat generation (electrical power - hydrogen energy content)
        electrical_power = voltage * current_amperes
        
        # Approximate heat generation (depends on efficiency)
        # About 20-40% of electrical power becomes heat in typical systems
        heat_generation_watts = electrical_power * 0.3
        
        # Estimate temperature rise
        # Simplified: ΔT ≈ Q / (m * c_p)
        # For 1 liter of water solution
        water_mass_kg = 1.0
        specific_heat = 4186  # J/(kg·K) for water
        
        # Temperature rise per hour (steady state approximation)
        temp_rise_per_hour = (heat_generation_watts * 3600) / (water_mass_kg * specific_heat)
        
        # Estimated operating temperature (with natural cooling)
        estimated_operating_temp = min(
            ambient_temp_celsius + temp_rise_per_hour * 0.5,  # Assume 50% heat retention
            70  # Practical limit before boiling issues
        )
        
        return {
            'heat_generation_watts': heat_generation_watts,
            'temp_rise_per_hour_celsius': temp_rise_per_hour,
            'estimated_operating_temp_celsius': estimated_operating_temp,
            'cooling_recommended': estimated_operating_temp > 55,
            'temperature_status': self._temp_status(estimated_operating_temp),
        }
    
    def _temp_status(self, temp: float) -> str:
        """Assess operating temperature."""
        if temp < 30:
            return "Cool - suboptimal efficiency"
        elif temp < 50:
            return "Optimal temperature range"
        elif temp < 70:
            return "Warm - good efficiency but monitor"
        else:
            return "Hot - cooling required"
    
    def cell_voltage_per_gap(self, total_voltage: float) -> float:
        """
        Calculate voltage per cell gap in series configuration.
        
        Args:
            total_voltage: Total applied voltage
            
        Returns:
            Voltage per gap in volts
        """
        num_gaps = self.config.number_of_plates - 1
        return total_voltage / num_gaps if num_gaps > 0 else total_voltage


def main():
    """Example usage of the physical model."""
    # Dry cell configuration from sources (similar to Instructables design)
    dry_cell_config = ElectrodeConfig(
        material="stainless_steel_316",
        number_of_plates=15,  # 7 neutral + 8 charged plates typical
        plate_width_mm=160,
        plate_height_mm=200,
        plate_thickness_mm=0.7,
        plate_spacing_mm=3.0,  # 3mm gasket spacing
        active_area_percentage=0.85
    )
    
    # Operating conditions
    current = 20.0  # A (typical high-current dry cell)
    voltage = 12.0  # V
    electrolyte_conductivity = 20.0  # S/m (good NaOH solution)
    
    model = PhysicalModel(dry_cell_config, temperature_celsius=45.0)
    
    print("=== Physical Model for Hydrogen Generator ===\n")
    
    print(f"Electrode Configuration:")
    print(f"  Material: {dry_cell_config.material}")
    print(f"  Number of plates: {dry_cell_config.number_of_plates}")
    print(f"  Dimensions: {dry_cell_config.plate_width_mm}x{dry_cell_config.plate_height_mm}mm")
    print(f"  Spacing: {dry_cell_config.plate_spacing_mm}mm\n")
    
    area = model.electrode_surface_area()
    print(f"Electrode Surface Area:")
    print(f"  Per plate: {area['area_per_plate_cm2']:.1f} cm²")
    print(f"  Total active area: {area['total_active_area_cm2']:.1f} cm²\n")
    
    cd = model.current_density(current)
    print(f"Current Density:")
    print(f"  {cd['current_density_ma_cm2']:.1f} mA/cm²")
    print(f"  Status: {cd['status']}\n")
    
    resistance = model.ohmic_resistance(electrolyte_conductivity)
    print(f"Resistance:")
    print(f"  Electrolyte: {resistance['electrolyte_resistance_ohms']:.4f} Ω")
    print(f"  Electrodes: {resistance['electrode_resistance_ohms']:.6f} Ω")
    print(f"  Total: {resistance['total_ohmic_resistance_ohms']:.4f} Ω\n")
    
    req_voltage = model.required_voltage(current, electrolyte_conductivity)
    print(f"Voltage Analysis:")
    print(f"  Theoretical minimum: {req_voltage['theoretical_voltage_v']:.2f} V")
    print(f"  Total overpotential: {req_voltage['overpotential_v']:.2f} V")
    print(f"  Required voltage: {req_voltage['total_required_voltage_v']:.2f} V")
    print(f"  Ohmic losses: {req_voltage['ohmic_percentage']:.1f}%")
    print(f"  Activation losses: {req_voltage['activation_percentage']:.1f}%\n")
    
    bubbles = model.bubble_effects(current)
    print(f"Bubble Effects:")
    print(f"  Coverage: {bubbles['bubble_coverage_fraction']*100:.1f}%")
    print(f"  {bubbles['recommendation']}\n")
    
    temp = model.temperature_effects(current, voltage)
    print(f"Temperature:")
    print(f"  Heat generation: {temp['heat_generation_watts']:.1f} W")
    print(f"  Estimated operating temp: {temp['estimated_operating_temp_celsius']:.1f}°C")
    print(f"  Status: {temp['temperature_status']}")


if __name__ == "__main__":
    main()
