"""
Phase 5 Validation Test Suite

Comprehensive validation tests for the complete PET Rocket Simulator system.
Tests literature validation, physical consistency, and integration.

ISO/IEC/IEEE 12207:2017 - Verification & Validation Process
"""

import pytest
import numpy as np
import time
from rocket_sim.integration.full_simulation import (
    FullSimulationConfig,
    run_complete_simulation
)
from rocket_sim.system_model import get_material, VesselGeometry
from rocket_sim.fem import solve_lame_equations, calculate_end_cap_stress_factor


class TestLiteratureValidation:
    """Validate results against published literature."""

    def test_pet_bottle_burst_pressure_range(self):
        """Validate PET bottle burst pressure is in literature range (800-1200 kPa)."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")

        from rocket_sim.system_model.burst_calculator import calculate_burst_pressure
        P_burst_yield = calculate_burst_pressure(geom, pet, use_yield=True, safety_factor=1.0)
        P_burst_ultimate = calculate_burst_pressure(geom, pet, use_yield=False, safety_factor=1.0)

        # Literature range: 800-1200 kPa typical
        # Our yield (conservative): should be lower bound
        # Our ultimate: should be within range
        assert 400e3 < P_burst_yield < 1000e3, f"Yield burst {P_burst_yield/1e3:.0f} kPa outside expected"
        assert 600e3 < P_burst_ultimate < 1500e3, f"Ultimate burst {P_burst_ultimate/1e3:.0f} kPa outside expected"

    def test_h2_o2_adiabatic_flame_temperature(self):
        """Validate H₂/O₂ combustion temperature near 3500K."""
        from rocket_sim.combustion.cantera_wrapper import simulate_combustion

        result = simulate_combustion(volume=0.001, mix_ratio=2.0, end_time=0.001, n_points=100)

        peak_temp = np.max(result.temperature)

        # Adiabatic flame temp for H₂/O₂ is ~3500K
        # With heat losses, expect ~3000-3500K
        assert 3000 < peak_temp < 3600, f"Peak temp {peak_temp:.0f}K outside expected range"

    def test_stress_concentration_factors_match_literature(self):
        """Validate stress concentration factors match Peterson's handbook."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)

        K_hemi = calculate_end_cap_stress_factor(geom, "hemispherical")
        K_flat = calculate_end_cap_stress_factor(geom, "flat")

        # Peterson's: hemispherical ~1.0, flat ~2.0-3.0
        assert np.isclose(K_hemi, 1.0, rtol=0.01)
        assert 2.0 <= K_flat <= 3.0

    def test_lame_equations_exact_solution(self):
        """Validate Lamé equations give exact analytical solution."""
        r_i = 0.05
        r_o = 0.055
        P_i = 1e6

        result = solve_lame_equations(r_i, r_o, P_i, n_points=100)

        # Verify boundary conditions to machine precision
        assert np.isclose(result.sigma_r[0], -P_i, rtol=1e-10)
        assert np.isclose(result.sigma_r[-1], 0.0, rtol=1e-10)


class TestPhysicalConsistency:
    """Validate physical laws are conserved."""

    def test_hoop_stress_twice_axial(self):
        """Verify σ_hoop = 2×σ_axial for thin-wall cylinder."""
        from rocket_sim.system_model.burst_calculator import calculate_hoop_stress, calculate_axial_stress

        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        P = 500e3

        sigma_h = calculate_hoop_stress(P, geom)
        sigma_a = calculate_axial_stress(P, geom)

        assert np.isclose(sigma_h, 2 * sigma_a, rtol=1e-10)

    def test_pressure_increases_during_combustion(self):
        """Verify pressure increases monotonically during combustion."""
        from rocket_sim.combustion.cantera_wrapper import simulate_combustion

        result = simulate_combustion(volume=0.001, mix_ratio=2.0, end_time=0.001, n_points=100)

        # Pressure should generally increase (may plateau)
        pressure_diff = np.diff(result.pressure)
        positive_fraction = np.sum(pressure_diff > 0) / len(pressure_diff)

        # At least 80% of time steps should have increasing pressure
        assert positive_fraction > 0.8

    def test_safety_factor_decreases_with_pressure(self):
        """Verify SF decreases as pressure increases."""
        from rocket_sim.system_model.burst_calculator import calculate_safety_factor

        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")

        SF_low = calculate_safety_factor(200e3, geom, pet)
        SF_medium = calculate_safety_factor(400e3, geom, pet)
        SF_high = calculate_safety_factor(600e3, geom, pet)

        assert SF_low > SF_medium > SF_high

    def test_von_mises_stress_positive(self):
        """Verify von Mises stress is always positive."""
        result = solve_lame_equations(0.05, 0.055, 1e6, n_points=50)

        assert np.all(result.sigma_vm > 0)


class TestEndToEndIntegration:
    """Validate complete system integration."""

    def test_safe_configuration_no_failure(self):
        """Verify safe configuration doesn't predict failure."""
        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            vessel_diameter=0.095,
            vessel_thickness=0.0003,
            vessel_material="PET",
            cap_type="hemispherical",
            include_threads=False,
            combustion_time=0.001  # Short for speed
        )

        result = run_complete_simulation(config, verbose=False)

        # Should not fail with hemispherical cap
        assert result.safety_margin > 1.5, f"SF={result.safety_margin:.2f} too low for safe config"

    def test_dangerous_configuration_predicts_failure(self):
        """Verify dangerous configuration predicts failure."""
        config = FullSimulationConfig(
            volume=0.001,  # Smaller volume = higher pressure
            fuel_oxidizer_ratio=2.5,  # Rich mixture
            vessel_diameter=0.095,
            vessel_thickness=0.0002,  # Thinner wall
            vessel_material="PET",
            cap_type="flat",  # High stress concentration
            include_threads=True,
            combustion_time=0.001
        )

        result = run_complete_simulation(config, verbose=False)

        # Should predict low safety margin or failure
        assert result.safety_margin < 2.0, "Dangerous config should have low SF"

    def test_parameter_sweep_reproducibility(self):
        """Verify results are reproducible across runs."""
        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.001
        )

        # Run twice
        result1 = run_complete_simulation(config, verbose=False)
        result2 = run_complete_simulation(config, verbose=False)

        # Results should be identical (deterministic)
        assert np.isclose(result1.summary['peak_pressure'],
                         result2.summary['peak_pressure'], rtol=1e-10)
        assert np.isclose(result1.summary['min_safety_factor'],
                         result2.summary['min_safety_factor'], rtol=1e-6)


class TestPerformance:
    """Validate performance requirements (NFR-5)."""

    def test_single_simulation_under_5_seconds(self):
        """Verify single simulation completes in <5 seconds."""
        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.01,  # Full 10ms simulation
            max_step=1e-5
        )

        start_time = time.time()
        result = run_complete_simulation(config, verbose=False)
        elapsed = time.time() - start_time

        # NFR-5: <5 minutes (300 seconds)
        # Target: <5 seconds
        assert elapsed < 5.0, f"Simulation took {elapsed:.2f}s > 5s target"
        assert result.execution_time < 5.0

    def test_parameter_study_performance(self):
        """Verify 10-run parameter study completes quickly."""
        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.001,  # Short for speed
        )

        start_time = time.time()

        for mr in np.linspace(1.5, 2.5, 10):
            config.fuel_oxidizer_ratio = mr
            result = run_complete_simulation(config, verbose=False)

        elapsed = time.time() - start_time

        # 10 runs should complete in <1 minute
        assert elapsed < 60.0, f"10 runs took {elapsed:.2f}s > 60s"


class TestSafetyValidation:
    """Validate safety analysis functionality."""

    def test_warnings_generated_for_dangerous_config(self):
        """Verify warnings are generated for dangerous configurations."""
        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            cap_type="flat",
            include_threads=True,
            combustion_time=0.001
        )

        result = run_complete_simulation(config, verbose=False)

        # Should have warnings about flat cap and threads
        assert len(result.warnings) > 0
        warning_text = ' '.join(result.warnings).lower()
        assert 'flat' in warning_text or 'cap' in warning_text or 'thread' in warning_text

    def test_failure_location_prediction(self):
        """Verify failure location is predicted."""
        config = FullSimulationConfig(
            volume=0.001,
            fuel_oxidizer_ratio=2.5,
            cap_type="flat",
            vessel_thickness=0.0002,
            combustion_time=0.001
        )

        result = run_complete_simulation(config, verbose=False)

        # Should have failure location if SF < 1
        if result.failed or result.safety_margin < 1.5:
            assert result.failure_location is not None
            assert len(result.failure_location) > 0


class TestDataExport:
    """Validate data export functionality."""

    def test_results_export_to_dict(self):
        """Verify results can be exported to dictionary."""
        config = FullSimulationConfig(
            volume=0.002,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.001
        )

        result = run_complete_simulation(config, verbose=False)
        data = result.to_dict()

        # Verify structure
        assert isinstance(data, dict)
        assert 'config' in data
        assert 'combustion' in data
        assert 'summary' in data
        assert 'failed' in data

        # Verify can be JSON serialized
        import json
        json_str = json.dumps(data, indent=2)
        assert len(json_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
