"""
Chemical Model for Hydrogen Production via Electrolysis

This module implements the chemical equations and calculations for water electrolysis
including Faraday's law, theoretical efficiency, and electrolyte effects.

Based on DIY hydrogen generator designs from various sources.
"""

import numpy as np
from typing import Dict, Tuple


class ChemicalModel:
    """Chemical model for water electrolysis process."""
    
    # Physical constants
    FARADAY_CONSTANT = 96485.3329  # C/mol (Coulombs per mole)
    MOLAR_MASS_H2 = 2.016  # g/mol
    MOLAR_VOLUME_H2_STP = 22.414  # L/mol at STP (0°C, 1 atm)
    GIBBS_FREE_ENERGY_25C = 237.2  # kJ/mol (standard Gibbs free energy at 25°C)
    ENTHALPY_CHANGE = 285.8  # kJ/mol (enthalpy change for water formation)
    
    def __init__(self, temperature_celsius: float = 25.0, pressure_atm: float = 1.0):
        """
        Initialize the chemical model.
        
        Args:
            temperature_celsius: Operating temperature in Celsius
            pressure_atm: Operating pressure in atmospheres
        """
        self.temperature_celsius = temperature_celsius
        self.temperature_kelvin = temperature_celsius + 273.15
        self.pressure_atm = pressure_atm
        
    def theoretical_voltage(self) -> float:
        """
        Calculate theoretical minimum voltage required for water electrolysis.
        
        Based on Gibbs free energy: ΔG = nFE
        Where E = ΔG / (nF)
        
        Returns:
            Theoretical voltage in volts
        """
        # Standard voltage at 25°C, 1 atm
        voltage_standard = self.GIBBS_FREE_ENERGY_25C * 1000 / (2 * self.FARADAY_CONSTANT)
        
        # Temperature correction (simplified Nernst equation)
        # V(T) ≈ V₀ - (T - T₀) × dV/dT
        # dV/dT ≈ -0.00085 V/K for water electrolysis
        temperature_correction = -0.00085 * (self.temperature_celsius - 25)
        
        return voltage_standard + temperature_correction
    
    def thermoneutral_voltage(self) -> float:
        """
        Calculate thermoneutral voltage (no heat exchange with surroundings).
        
        Based on enthalpy: ΔH = nFE_tn
        Where E_tn = ΔH / (nF)
        
        Returns:
            Thermoneutral voltage in volts
        """
        return self.ENTHALPY_CHANGE * 1000 / (2 * self.FARADAY_CONSTANT)
    
    def theoretical_efficiency(self, actual_voltage: float) -> float:
        """
        Calculate thermodynamic efficiency of electrolysis.
        
        Efficiency = E_theoretical / E_actual
        
        Args:
            actual_voltage: Actual applied voltage in volts
            
        Returns:
            Efficiency as a fraction (0-1)
        """
        theoretical_v = self.theoretical_voltage()
        return min(theoretical_v / actual_voltage, 1.0)
    
    def hydrogen_production_rate_faraday(self, current_amperes: float) -> Dict[str, float]:
        """
        Calculate hydrogen production rate using Faraday's law.
        
        Q = It (charge in coulombs)
        n = Q / (zF) where z = 2 for H₂
        
        Args:
            current_amperes: Current in amperes
            
        Returns:
            Dictionary with production rates in various units
        """
        # Moles of H2 produced per second
        moles_per_second = current_amperes / (2 * self.FARADAY_CONSTANT)
        
        # Convert to various units
        return {
            'moles_per_second': moles_per_second,
            'moles_per_hour': moles_per_second * 3600,
            'grams_per_hour': moles_per_second * 3600 * self.MOLAR_MASS_H2,
            'liters_per_hour_stp': moles_per_second * 3600 * self.MOLAR_VOLUME_H2_STP,
            'liters_per_minute_stp': moles_per_second * 60 * self.MOLAR_VOLUME_H2_STP,
        }
    
    def actual_production_rate(self, current_amperes: float, 
                               faradaic_efficiency: float = 0.95) -> Dict[str, float]:
        """
        Calculate actual hydrogen production rate accounting for losses.
        
        Args:
            current_amperes: Current in amperes
            faradaic_efficiency: Fraction of current that produces H2 (0-1)
            
        Returns:
            Dictionary with actual production rates
        """
        theoretical = self.hydrogen_production_rate_faraday(current_amperes)
        return {key: value * faradaic_efficiency for key, value in theoretical.items()}
    
    def electrolyte_conductivity(self, naoh_concentration_molar: float) -> float:
        """
        Estimate electrolyte conductivity for NaOH solution.
        
        Based on empirical data for NaOH solutions at 25°C.
        
        Args:
            naoh_concentration_molar: NaOH concentration in mol/L
            
        Returns:
            Conductivity in S/m (Siemens per meter)
        """
        # Empirical relationship for NaOH at 25°C
        # Peak conductivity around 4-5 M
        if naoh_concentration_molar <= 0:
            return 0.0
        
        # Simplified model based on literature data
        # Conductivity increases then decreases at high concentrations
        conductivity_peak = 25.0  # S/m at optimal concentration
        optimal_concentration = 4.5  # M
        
        if naoh_concentration_molar <= optimal_concentration:
            # Linear increase region
            conductivity = (conductivity_peak / optimal_concentration) * naoh_concentration_molar
        else:
            # Decrease at high concentration due to viscosity
            excess = naoh_concentration_molar - optimal_concentration
            conductivity = conductivity_peak * np.exp(-0.15 * excess)
        
        # Temperature correction (approximate)
        temp_factor = 1 + 0.02 * (self.temperature_celsius - 25)
        
        return conductivity * temp_factor
    
    def naoh_from_weight_ratio(self, water_ml: float, naoh_grams: float) -> float:
        """
        Calculate NaOH molarity from weight ratio.
        
        Common DIY recipe: 1 tablespoon (15-20g) NaOH per liter of water
        
        Args:
            water_ml: Volume of water in milliliters
            naoh_grams: Mass of NaOH in grams
            
        Returns:
            NaOH concentration in mol/L
        """
        naoh_molar_mass = 40.0  # g/mol
        moles_naoh = naoh_grams / naoh_molar_mass
        liters_water = water_ml / 1000.0
        
        return moles_naoh / liters_water if liters_water > 0 else 0.0
    
    def power_consumption(self, voltage: float, current: float) -> Dict[str, float]:
        """
        Calculate power consumption and energy per unit hydrogen.
        
        Args:
            voltage: Applied voltage in volts
            current: Current in amperes
            
        Returns:
            Dictionary with power metrics
        """
        power_watts = voltage * current
        
        # Hydrogen production rate
        h2_rate = self.hydrogen_production_rate_faraday(current)
        liters_per_hour = h2_rate['liters_per_hour_stp']
        
        # Energy per liter of H2
        kwh_per_liter = (power_watts / 1000) / liters_per_hour if liters_per_hour > 0 else 0
        
        return {
            'power_watts': power_watts,
            'power_kw': power_watts / 1000,
            'energy_kwh_per_liter_h2': kwh_per_liter,
            'energy_kwh_per_kg_h2': kwh_per_liter * (1000 / (self.MOLAR_MASS_H2 * self.MOLAR_VOLUME_H2_STP)),
        }
    
    def thermal_effects(self, voltage: float, current: float) -> Dict[str, float]:
        """
        Calculate thermal effects and heat generation.
        
        Args:
            voltage: Applied voltage in volts
            current: Current in amperes
            
        Returns:
            Dictionary with thermal data
        """
        total_power = voltage * current
        thermoneutral_v = self.thermoneutral_voltage()
        
        # Heat generation (overvoltage losses)
        voltage_loss = voltage - thermoneutral_v
        heat_generation_watts = voltage_loss * current
        
        # Heat that must be removed to maintain temperature
        cooling_required = max(0, heat_generation_watts)
        
        return {
            'total_power_watts': total_power,
            'thermoneutral_power_watts': thermoneutral_v * current,
            'heat_generation_watts': heat_generation_watts,
            'cooling_required_watts': cooling_required,
            'heat_generation_percentage': (heat_generation_watts / total_power * 100) if total_power > 0 else 0,
        }


def main():
    """Example usage of the chemical model."""
    # Create model at typical DIY operating conditions
    model = ChemicalModel(temperature_celsius=45.0, pressure_atm=1.0)
    
    # Typical DIY generator parameters (from sources)
    voltage = 12.0  # V
    current = 6.0   # A
    naoh_concentration = model.naoh_from_weight_ratio(1000, 15)  # ~1:40 mix
    
    print("=== Chemical Model for Hydrogen Generator ===\n")
    
    print(f"Operating Conditions:")
    print(f"  Temperature: {model.temperature_celsius}°C")
    print(f"  Pressure: {model.pressure_atm} atm")
    print(f"  Voltage: {voltage} V")
    print(f"  Current: {current} A")
    print(f"  NaOH Concentration: {naoh_concentration:.2f} M\n")
    
    print(f"Theoretical Values:")
    print(f"  Minimum Voltage: {model.theoretical_voltage():.3f} V")
    print(f"  Thermoneutral Voltage: {model.thermoneutral_voltage():.3f} V")
    print(f"  Thermodynamic Efficiency: {model.theoretical_efficiency(voltage)*100:.1f}%\n")
    
    production = model.hydrogen_production_rate_faraday(current)
    print(f"Hydrogen Production (Theoretical):")
    print(f"  {production['liters_per_minute_stp']:.3f} L/min (at STP)")
    print(f"  {production['liters_per_hour_stp']:.2f} L/hr (at STP)")
    print(f"  {production['grams_per_hour']:.2f} g/hr\n")
    
    power = model.power_consumption(voltage, current)
    print(f"Power Consumption:")
    print(f"  {power['power_watts']:.1f} W")
    print(f"  {power['energy_kwh_per_liter_h2']:.3f} kWh/L H₂")
    print(f"  {power['energy_kwh_per_kg_h2']:.2f} kWh/kg H₂\n")
    
    thermal = model.thermal_effects(voltage, current)
    print(f"Thermal Effects:")
    print(f"  Heat Generation: {thermal['heat_generation_watts']:.1f} W")
    print(f"  Heat %: {thermal['heat_generation_percentage']:.1f}%")
    print(f"  Cooling Required: {thermal['cooling_required_watts']:.1f} W\n")
    
    conductivity = model.electrolyte_conductivity(naoh_concentration)
    print(f"Electrolyte Conductivity: {conductivity:.2f} S/m")


if __name__ == "__main__":
    main()
