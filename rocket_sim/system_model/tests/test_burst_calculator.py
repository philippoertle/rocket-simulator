"""
Unit tests for burst_calculator module

ISO/IEC/IEEE 12207:2017 - Verification Process
Tests analytical pressure vessel calculations
"""

import pytest
import numpy as np
from rocket_sim.system_model.materials import get_material
from rocket_sim.system_model.burst_calculator import (
    VesselGeometry,
    StressState,
    validate_thin_wall_assumption,
    calculate_hoop_stress,
    calculate_axial_stress,
    calculate_von_mises_stress,
    calculate_stress_state,
    calculate_burst_pressure,
    calculate_safety_factor,
    check_failure,
    predict_failure_pressure,
)


class TestVesselGeometry:
    """Test VesselGeometry dataclass."""

    def test_create_vessel_geometry(self):
        """Test creating VesselGeometry object."""
        geom = VesselGeometry(
            inner_diameter=0.1,
            wall_thickness=0.001,
            length=0.3
        )
        assert geom.inner_diameter == 0.1
        assert geom.wall_thickness == 0.001
        assert geom.length == 0.3

    def test_vessel_geometry_without_length(self):
        """Test creating geometry without length."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        assert geom.length is None


class TestThinWallValidation:
    """Test thin-wall assumption validation."""

    def test_valid_thin_wall(self):
        """Test that typical bottle passes thin-wall check."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        # Should not raise
        validate_thin_wall_assumption(geom)

    def test_marginal_thin_wall_warning(self):
        """Test warning for marginal thin-wall ratio."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.006)
        # Should warn but not raise
        with pytest.warns(UserWarning, match="marginal"):
            validate_thin_wall_assumption(geom)

    def test_thick_wall_raises_error(self):
        """Test that thick wall raises ValueError."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.015)
        with pytest.raises(ValueError, match="Thin-wall assumption violated"):
            validate_thin_wall_assumption(geom)


class TestStressCalculations:
    """Test stress calculation functions."""

    def test_hoop_stress_formula(self):
        """Test hoop stress calculation σ = PD/(2t)."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        P = 500e3  # 500 kPa

        sigma_hoop = calculate_hoop_stress(P, geom)

        # Manual calculation
        expected = P * 0.1 / (2 * 0.001)
        assert np.isclose(sigma_hoop, expected, rtol=1e-10)
        assert sigma_hoop == 25e6  # 25 MPa

    def test_axial_stress_formula(self):
        """Test axial stress calculation σ = PD/(4t)."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        P = 500e3

        sigma_axial = calculate_axial_stress(P, geom)

        # Manual calculation
        expected = P * 0.1 / (4 * 0.001)
        assert np.isclose(sigma_axial, expected, rtol=1e-10)
        assert sigma_axial == 12.5e6  # 12.5 MPa

    def test_hoop_twice_axial(self):
        """Test that hoop stress is exactly 2x axial stress."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        P = 300e3

        sigma_hoop = calculate_hoop_stress(P, geom)
        sigma_axial = calculate_axial_stress(P, geom)

        assert np.isclose(sigma_hoop, 2 * sigma_axial, rtol=1e-10)

    def test_von_mises_stress(self):
        """Test von Mises stress calculation."""
        sigma_hoop = 100e6  # 100 MPa
        sigma_axial = 50e6  # 50 MPa

        sigma_vm = calculate_von_mises_stress(sigma_hoop, sigma_axial)

        # For σ_h = 2σ_a: σ_vm = √(σ_h² - σ_h·σ_a + σ_a²)
        expected = np.sqrt(sigma_hoop**2 - sigma_hoop*sigma_axial + sigma_axial**2)
        assert np.isclose(sigma_vm, expected, rtol=1e-10)

    def test_stress_state_complete(self):
        """Test complete stress state calculation."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        P = 400e3

        state = calculate_stress_state(P, geom)

        assert isinstance(state, StressState)
        assert state.hoop_stress > 0
        assert state.axial_stress > 0
        assert state.radial_stress == 0  # Thin-wall assumption
        assert state.von_mises_stress > 0
        assert state.hoop_stress == 2 * state.axial_stress


class TestBurstPressure:
    """Test burst pressure calculations."""

    def test_burst_pressure_pet_bottle(self):
        """Test burst pressure for typical PET bottle."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")

        P_burst = calculate_burst_pressure(geom, pet, use_yield=True)

        # Manual: P = 2 * σ_yield * t / D
        expected = 2 * pet.yield_strength * 0.0003 / 0.095
        assert np.isclose(P_burst, expected, rtol=1e-10)

        # Should be in reasonable range (5-10 bar for PET bottle)
        assert 500e3 < P_burst < 1000e3

    def test_burst_pressure_yield_vs_ultimate(self):
        """Test that ultimate strength gives higher burst pressure."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        P_yield = calculate_burst_pressure(geom, pet, use_yield=True)
        P_ultimate = calculate_burst_pressure(geom, pet, use_yield=False)

        assert P_ultimate > P_yield

    def test_burst_pressure_with_safety_factor(self):
        """Test burst pressure with safety factor."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        P_no_sf = calculate_burst_pressure(geom, pet, safety_factor=1.0)
        P_sf4 = calculate_burst_pressure(geom, pet, safety_factor=4.0)

        assert np.isclose(P_sf4, P_no_sf / 4.0, rtol=1e-10)

    def test_burst_pressure_thicker_wall(self):
        """Test that thicker wall gives higher burst pressure."""
        thin = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        thick = VesselGeometry(inner_diameter=0.1, wall_thickness=0.002)
        pet = get_material("PET")

        P_thin = calculate_burst_pressure(thin, pet)
        P_thick = calculate_burst_pressure(thick, pet)

        assert P_thick > P_thin
        assert np.isclose(P_thick, 2 * P_thin, rtol=1e-10)


class TestSafetyFactor:
    """Test safety factor calculations."""

    def test_safety_factor_calculation(self):
        """Test safety factor SF = σ_allow / σ_actual."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")
        P = 300e3  # 300 kPa

        SF = calculate_safety_factor(P, geom, pet, criterion="yield")

        # Calculate manually
        stress_state = calculate_stress_state(P, geom)
        expected_SF = pet.yield_strength / stress_state.von_mises_stress

        assert np.isclose(SF, expected_SF, rtol=1e-10)
        assert SF > 1.0  # Should be safe at 300 kPa

    def test_safety_factor_at_burst(self):
        """Test that SF ≈ 1.0 at burst pressure."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        P_burst = predict_failure_pressure(geom, pet, criterion="yield")
        SF = calculate_safety_factor(P_burst, geom, pet, criterion="yield")

        assert np.isclose(SF, 1.0, rtol=1e-6)

    def test_safety_factor_decreases_with_pressure(self):
        """Test that safety factor decreases as pressure increases."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        SF1 = calculate_safety_factor(100e3, geom, pet)
        SF2 = calculate_safety_factor(200e3, geom, pet)
        SF3 = calculate_safety_factor(400e3, geom, pet)

        assert SF1 > SF2 > SF3


class TestFailureDetection:
    """Test failure detection."""

    def test_check_failure_safe(self):
        """Test that low pressure is safe."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")
        P = 200e3  # 200 kPa (should be safe)

        failed, SF = check_failure(P, geom, pet)

        assert not failed
        assert SF > 1.0

    def test_check_failure_at_burst(self):
        """Test failure detection at burst pressure."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        P_burst = predict_failure_pressure(geom, pet)
        failed, SF = check_failure(P_burst, geom, pet)

        assert failed or np.isclose(SF, 1.0, rtol=1e-3)

    def test_check_failure_above_burst(self):
        """Test failure detection above burst pressure."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        P_burst = predict_failure_pressure(geom, pet)
        P_over = P_burst * 1.5

        failed, SF = check_failure(P_over, geom, pet)

        assert failed
        assert SF < 1.0


class TestPredictFailurePressure:
    """Test failure pressure prediction."""

    def test_predict_failure_pressure(self):
        """Test failure pressure prediction."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")

        P_fail = predict_failure_pressure(geom, pet, criterion="yield")

        # Should match burst pressure with SF=1
        P_burst = calculate_burst_pressure(geom, pet, use_yield=True, safety_factor=1.0)
        assert np.isclose(P_fail, P_burst, rtol=1e-10)

    def test_predict_failure_yield_vs_ultimate(self):
        """Test that ultimate criterion gives higher failure pressure."""
        geom = VesselGeometry(inner_diameter=0.1, wall_thickness=0.001)
        pet = get_material("PET")

        P_yield = predict_failure_pressure(geom, pet, criterion="yield")
        P_ultimate = predict_failure_pressure(geom, pet, criterion="ultimate")

        assert P_ultimate > P_yield


class TestLiteratureValidation:
    """Validate against published data."""

    def test_pet_bottle_burst_realistic(self):
        """Test that PET bottle burst pressure is in literature range.

        Literature: 2L PET bottles burst at 800-1200 kPa typically.
        Our model uses simplified geometry, so expect conservative estimate.
        """
        # Typical 2L bottle
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")

        P_burst_yield = predict_failure_pressure(geom, pet, criterion="yield")
        P_burst_ultimate = predict_failure_pressure(geom, pet, criterion="ultimate")

        # Yield criterion should be conservative (lower bound)
        assert 400e3 < P_burst_yield < 1000e3, \
            f"Yield burst pressure {P_burst_yield/1e3:.0f} kPa outside expected range"

        # Ultimate criterion closer to actual burst
        assert 600e3 < P_burst_ultimate < 1500e3, \
            f"Ultimate burst pressure {P_burst_ultimate/1e3:.0f} kPa outside expected range"


class TestParametricStudies:
    """Test behavior across parameter ranges."""

    def test_burst_pressure_vs_thickness(self):
        """Test burst pressure scales linearly with thickness."""
        pet = get_material("PET")
        thicknesses = [0.0002, 0.0004, 0.0006]

        pressures = []
        for t in thicknesses:
            geom = VesselGeometry(inner_diameter=0.1, wall_thickness=t)
            P = calculate_burst_pressure(geom, pet)
            pressures.append(P)

        # Should scale linearly
        assert np.isclose(pressures[1], 2 * pressures[0], rtol=1e-6)
        assert np.isclose(pressures[2], 3 * pressures[0], rtol=1e-6)

    def test_burst_pressure_vs_diameter(self):
        """Test burst pressure scales inversely with diameter."""
        pet = get_material("PET")
        diameters = [0.05, 0.10, 0.15]

        pressures = []
        for D in diameters:
            geom = VesselGeometry(inner_diameter=D, wall_thickness=0.001)
            P = calculate_burst_pressure(geom, pet)
            pressures.append(P)

        # Should scale inversely
        assert pressures[0] > pressures[1] > pressures[2]
        assert np.isclose(pressures[1], pressures[0] * 0.05 / 0.10, rtol=1e-6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
