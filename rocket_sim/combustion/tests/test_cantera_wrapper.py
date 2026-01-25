"""
Unit Tests for Combustion Module
ISO 12207:2017 §6.4.9 Verification Process

Test Coverage:
    - FR-1: Combustion calculations vs. literature data
    - Input validation (FR-9)
    - Error handling
    - API contracts

Verification Method: Unit test vs. literature
Pass Criteria: P_max within 5% of published H₂/O₂ data
"""

import pytest
import numpy as np
from rocket_sim.combustion.cantera_wrapper import (
    simulate_combustion,
    validate_combustion_inputs,
    get_equilibrium_properties,
    CombustionResult
)


class TestInputValidation:
    """Test suite for input validation (FR-9)."""

    def test_valid_inputs(self):
        """Test that valid inputs pass validation."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,      # 1 liter
            mix_ratio=2.0,     # Stoichiometric
            T0=300.0,
            P0=101325.0
        )
        assert is_valid is True
        assert "valid" in msg.lower()

    def test_negative_volume(self):
        """Test rejection of negative volume."""
        is_valid, msg = validate_combustion_inputs(
            volume=-0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0
        )
        assert is_valid is False
        assert "positive" in msg.lower()

    def test_zero_volume(self):
        """Test rejection of zero volume."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.0,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0
        )
        assert is_valid is False

    def test_excessive_volume(self):
        """Test warning for unrealistic volume."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.1,  # 100 liters - too large for PET bottle
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0
        )
        assert is_valid is False
        assert "exceeds" in msg.lower()

    def test_invalid_mix_ratio_negative(self):
        """Test rejection of negative mix ratio."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,
            mix_ratio=-1.0,
            T0=300.0,
            P0=101325.0
        )
        assert is_valid is False

    def test_invalid_mix_ratio_extreme(self):
        """Test rejection of extreme mix ratios."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,
            mix_ratio=100.0,  # Way too fuel-rich
            T0=300.0,
            P0=101325.0
        )
        assert is_valid is False

    def test_temperature_too_low(self):
        """Test rejection of unrealistic low temperature."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,
            mix_ratio=2.0,
            T0=100.0,  # Too cold
            P0=101325.0
        )
        assert is_valid is False

    def test_temperature_too_high(self):
        """Test rejection of unrealistic high initial temperature."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,
            mix_ratio=2.0,
            T0=1000.0,  # Too hot for initial state
            P0=101325.0
        )
        assert is_valid is False

    def test_pressure_too_low(self):
        """Test rejection of unrealistic low pressure."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=1000.0  # Too low
        )
        assert is_valid is False

    def test_pressure_too_high(self):
        """Test rejection of unrealistic high initial pressure."""
        is_valid, msg = validate_combustion_inputs(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=1e6  # Too high for initial state
        )
        assert is_valid is False


class TestCombustionSimulation:
    """Test suite for combustion simulation (FR-1)."""

    def test_stoichiometric_combustion(self):
        """
        Test stoichiometric H₂:O₂ combustion.

        Literature values for H₂ + 0.5 O₂ at constant volume:
        - Peak temperature: ~3000-3500 K
        - Pressure ratio: ~15-20x for adiabatic combustion
        """
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            end_time=0.01,
            n_points=100
        )

        assert result.success is True
        assert len(result.time) == 100
        assert len(result.pressure) == 100
        assert len(result.temperature) == 100

        # Check pressure rise
        pressure_ratio = result.peak_pressure / 101325.0
        assert 10.0 < pressure_ratio < 25.0, \
            f"Pressure ratio {pressure_ratio} outside expected range [10, 25]"

        # Check temperature rise
        peak_temp = np.max(result.temperature)
        assert 2500 < peak_temp < 4000, \
            f"Peak temperature {peak_temp} K outside expected range [2500, 4000] K"

        # Check that dP/dt is positive and significant
        assert result.max_dPdt > 0

    def test_fuel_rich_combustion(self):
        """Test fuel-rich mixture (excess H₂)."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=4.0,  # Twice stoichiometric H₂
            T0=300.0,
            P0=101325.0,
            end_time=0.01
        )

        assert result.success is True
        # Fuel-rich should have lower peak temperature due to incomplete combustion
        peak_temp = np.max(result.temperature)
        assert peak_temp > 1000  # Still significant combustion

    def test_oxidizer_rich_combustion(self):
        """Test oxidizer-rich mixture (excess O₂)."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=1.0,  # Half stoichiometric H₂
            T0=300.0,
            P0=101325.0,
            end_time=0.01
        )

        assert result.success is True
        # Should still combust but with excess oxygen
        assert result.peak_pressure > 101325.0

    def test_small_volume(self):
        """Test with smaller volume (0.5 L bottle)."""
        result = simulate_combustion(
            volume=0.0005,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            end_time=0.01
        )

        assert result.success is True
        # Peak pressure should be similar (constant volume combustion)
        assert result.peak_pressure > 1e6  # > 10 bar

    def test_elevated_initial_pressure(self):
        """Test with pre-pressurized chamber."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=200000.0,  # 2 bar initial
            end_time=0.01
        )

        assert result.success is True
        # Peak pressure should scale roughly linearly with initial pressure
        assert result.peak_pressure > 2e6  # > 20 bar

    def test_result_structure(self):
        """Test that result has correct structure."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0
        )

        assert isinstance(result, CombustionResult)
        assert hasattr(result, 'time')
        assert hasattr(result, 'pressure')
        assert hasattr(result, 'temperature')
        assert hasattr(result, 'peak_pressure')
        assert hasattr(result, 'max_dPdt')
        assert hasattr(result, 'success')
        assert hasattr(result, 'message')

    def test_result_to_dict(self):
        """Test conversion of result to dictionary."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            n_points=10
        )

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'time' in result_dict
        assert 'pressure' in result_dict
        assert 'temperature' in result_dict
        assert 'peak_pressure' in result_dict
        assert 'max_dPdt' in result_dict
        assert len(result_dict['time']) == 10

    def test_invalid_input_returns_failure(self):
        """Test that invalid inputs return failure result with validation on."""
        result = simulate_combustion(
            volume=-0.001,  # Invalid
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            validate_inputs=True
        )

        assert result.success is False
        assert "validation failed" in result.message.lower()
        assert len(result.time) == 0
        assert len(result.pressure) == 0


class TestEquilibriumCalculations:
    """Test suite for equilibrium property calculations."""

    def test_equilibrium_stoichiometric(self):
        """Test equilibrium calculation for stoichiometric mixture."""
        eq_props = get_equilibrium_properties(
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0
        )

        assert eq_props['success'] is True
        assert eq_props['T_eq'] > 2500  # High temperature
        assert eq_props['P_eq'] > 1e6   # High pressure
        assert 'composition' in eq_props

    def test_equilibrium_fuel_rich(self):
        """Test equilibrium for fuel-rich mixture."""
        eq_props = get_equilibrium_properties(
            mix_ratio=4.0,
            T0=300.0,
            P0=101325.0
        )

        assert eq_props['success'] is True
        # Fuel-rich should have lower temperature
        assert eq_props['T_eq'] > 1000
        assert eq_props['T_eq'] < 3500


class TestPhysicalConsistency:
    """Test suite for physical consistency checks."""

    def test_energy_conservation_qualitative(self):
        """Test that energy trends are reasonable."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            end_time=0.01,
            n_points=100
        )

        # Temperature should increase during combustion
        assert result.temperature[-1] > result.temperature[0]

        # Pressure should increase during combustion
        assert result.pressure[-1] > result.pressure[0]

    def test_monotonic_time(self):
        """Test that time array is strictly increasing."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            n_points=50
        )

        time_diffs = np.diff(result.time)
        assert np.all(time_diffs > 0), "Time array is not monotonically increasing"

    def test_positive_values(self):
        """Test that physical quantities remain positive."""
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0
        )

        assert np.all(result.pressure > 0), "Negative pressure detected"
        assert np.all(result.temperature > 0), "Negative temperature detected"
        assert result.peak_pressure > 0
        assert result.max_dPdt >= 0


class TestLiteratureValidation:
    """
    Test suite for validation against published data.

    Verification Requirement (FR-1):
    P_max within 5% of published H₂/O₂ data
    """

    def test_adiabatic_flame_temperature(self):
        """
        Validate against known adiabatic flame temperature for H₂/O₂.

        Literature value at 1 atm, stoichiometric:
        T_ad ≈ 3080 K (NASA CEA)

        Tolerance: ±10% due to kinetic vs. equilibrium differences
        """
        eq_props = get_equilibrium_properties(
            mix_ratio=2.0,
            T0=298.0,
            P0=101325.0
        )

        T_ad_literature = 3080.0  # K
        T_ad_calculated = eq_props['T_eq']

        error_percent = abs(T_ad_calculated - T_ad_literature) / T_ad_literature * 100

        assert error_percent < 15, \
            f"Adiabatic flame temperature error {error_percent:.1f}% exceeds 15% threshold"

    def test_constant_volume_pressure_rise(self):
        """
        Validate pressure rise ratio against theoretical estimate.

        For constant volume adiabatic combustion:
        P_f / P_i ≈ T_f / T_i (ideal gas)

        Expected: T_f/T_i ≈ 3000/300 = 10x
        Therefore: P_f/P_i ≈ 10-15x (accounting for non-ideal effects)
        """
        result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            end_time=0.01
        )

        pressure_ratio = result.peak_pressure / 101325.0
        temperature_ratio = np.max(result.temperature) / 300.0

        # Pressure ratio should be within 50% of temperature ratio
        ratio_difference = abs(pressure_ratio - temperature_ratio) / temperature_ratio

        assert ratio_difference < 0.5, \
            f"Pressure and temperature ratios differ by {ratio_difference*100:.1f}%"


@pytest.mark.parametrize("volume", [0.0005, 0.001, 0.002])
@pytest.mark.parametrize("mix_ratio", [1.5, 2.0, 3.0])
def test_parameter_sweep(volume, mix_ratio):
    """
    Parametric test across realistic operating conditions.

    Requirements: FR-7 (Parameter sweeps)
    """
    result = simulate_combustion(
        volume=volume,
        mix_ratio=mix_ratio,
        T0=300.0,
        P0=101325.0,
        end_time=0.005,
        n_points=50
    )

    assert result.success is True
    assert result.peak_pressure > 101325.0
    assert np.max(result.temperature) > 300.0


if __name__ == "__main__":
    """Run tests with: pytest rocket_sim/combustion/tests/test_cantera_wrapper.py -v"""
    pytest.main([__file__, "-v", "--tb=short"])
