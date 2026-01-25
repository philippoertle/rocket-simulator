"""
Integration tests for Module 1 → Module 2

ISO/IEC/IEEE 12207:2017 - Verification Process
Tests the integration between combustion simulation and system dynamics
"""

import pytest
import numpy as np
from rocket_sim.combustion.cantera_wrapper import simulate_combustion
from rocket_sim.system_model import (
    get_material,
    VesselGeometry,
    simulate_system_dynamics,
    run_full_simulation,
    SimulationConfig,
    calculate_burst_pressure,
)


class TestModule1ToModule2Integration:
    """Test integration between combustion (M1) and system model (M2)."""

    def test_combustion_to_system_dynamics(self):
        """Test that combustion results can be passed to system dynamics."""
        # Step 1: Run combustion simulation
        comb_result = simulate_combustion(
            volume=0.001,
            mix_ratio=2.0,
            T0=300.0,
            P0=101325.0,
            end_time=0.001,
            n_points=100
        )

        # Verify combustion ran
        assert len(comb_result.time) > 0
        assert len(comb_result.pressure) > 0

        # Step 2: Set up vessel
        geometry = VesselGeometry(
            inner_diameter=0.095,
            wall_thickness=0.0003,
            length=0.30
        )
        material = get_material("PET")

        # Step 3: Run system dynamics
        sys_result = simulate_system_dynamics(
            combustion_result=comb_result,
            geometry=geometry,
            material=material,
            end_time=0.001,
            max_step=1e-5
        )

        # Verify system dynamics ran
        assert len(sys_result.time) > 0
        assert len(sys_result.pressure) > 0
        assert len(sys_result.hoop_stress) > 0
        assert len(sys_result.safety_factor) > 0

        # Verify stresses are realistic
        assert np.all(sys_result.hoop_stress >= 0)
        assert np.all(sys_result.von_mises_stress >= 0)

    def test_full_simulation_workflow(self):
        """Test complete end-to-end simulation."""
        config = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            vessel_diameter=0.095,
            vessel_thickness=0.0003,
            vessel_length=0.30,
            vessel_material="PET",
            combustion_time=0.001,
            max_step=1e-5
        )

        comb_result, sys_result = run_full_simulation(config)

        # Verify both modules ran
        assert comb_result is not None
        assert sys_result is not None

        # Verify results are consistent
        assert len(comb_result.time) > 0
        assert len(sys_result.time) > 0

        # Peak pressure should be similar (interpolation may differ slightly)
        comb_peak = np.max(comb_result.pressure)
        sys_peak = np.max(sys_result.pressure)

        # Should be within 10% (interpolation differences)
        assert np.isclose(comb_peak, sys_peak, rtol=0.1)

    def test_safety_factor_behavior(self):
        """Test that safety factor decreases with increasing pressure."""
        config = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            vessel_diameter=0.095,
            vessel_thickness=0.0003,
            combustion_time=0.001
        )

        _, sys_result = run_full_simulation(config)

        # Safety factor should be positive
        assert np.all(sys_result.safety_factor > 0)

        # At low pressure, SF should be high
        # At high pressure, SF should be lower
        idx_low = np.argmin(sys_result.pressure)
        idx_high = np.argmax(sys_result.pressure)

        SF_low = sys_result.safety_factor[idx_low]
        SF_high = sys_result.safety_factor[idx_high]

        assert SF_low > SF_high

    def test_pressure_vessel_does_not_fail_at_low_pressure(self):
        """Test that vessel doesn't fail at low combustion pressures."""
        # Use very small volume to keep pressure low
        config = SimulationConfig(
            vessel_volume=0.01,  # 10L (larger volume = lower pressure)
            fuel_oxidizer_ratio=2.0,
            vessel_diameter=0.095,
            vessel_thickness=0.0003,
            combustion_time=0.001
        )

        _, sys_result = run_full_simulation(config)

        # Should not fail
        assert not sys_result.failed
        assert sys_result.failure_time is None

        # All safety factors should be > 1
        assert np.all(sys_result.safety_factor > 1.0)


class TestBurstPrediction:
    """Test burst pressure prediction accuracy."""

    def test_burst_pressure_comparison(self):
        """Compare analytical burst with system simulation."""
        geometry = VesselGeometry(
            inner_diameter=0.095,
            wall_thickness=0.0003
        )
        material = get_material("PET")

        # Analytical burst pressure
        P_burst_analytical = calculate_burst_pressure(
            geometry, material, use_yield=True, safety_factor=1.0
        )

        # System simulation should predict failure near this pressure
        assert 500e3 < P_burst_analytical < 1000e3

    def test_thicker_wall_safer(self):
        """Test that thicker walls provide higher safety margins."""
        # Thin wall
        config_thin = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            vessel_thickness=0.0002,  # 0.2mm
            combustion_time=0.001
        )

        # Thick wall
        config_thick = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            vessel_thickness=0.0004,  # 0.4mm (2x thicker)
            combustion_time=0.001
        )

        _, sys_thin = run_full_simulation(config_thin)
        _, sys_thick = run_full_simulation(config_thick)

        # Thicker wall should have higher safety factors
        SF_thin = np.min(sys_thin.safety_factor)
        SF_thick = np.min(sys_thick.safety_factor)

        assert SF_thick > SF_thin


class TestPhysicalConsistency:
    """Test physical consistency of integrated simulation."""

    def test_hoop_stress_twice_axial(self):
        """Test that hoop stress = 2 * axial stress throughout simulation."""
        config = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.001
        )

        _, sys_result = run_full_simulation(config)

        # Check relationship holds at all time points
        for i in range(len(sys_result.time)):
            ratio = sys_result.hoop_stress[i] / sys_result.axial_stress[i]
            assert np.isclose(ratio, 2.0, rtol=1e-6)

    def test_stress_increases_with_pressure(self):
        """Test that stress increases as pressure increases."""
        config = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.001
        )

        _, sys_result = run_full_simulation(config)

        # Find indices of min and max pressure
        idx_min_p = np.argmin(sys_result.pressure)
        idx_max_p = np.argmax(sys_result.pressure)

        # Stress should be higher at higher pressure
        assert sys_result.hoop_stress[idx_max_p] > sys_result.hoop_stress[idx_min_p]
        assert sys_result.von_mises_stress[idx_max_p] > sys_result.von_mises_stress[idx_min_p]


class TestDataExport:
    """Test data export functionality."""

    def test_system_state_to_dict(self):
        """Test that SystemState can be exported to dictionary."""
        config = SimulationConfig(
            vessel_volume=0.001,
            fuel_oxidizer_ratio=2.0,
            combustion_time=0.001
        )

        _, sys_result = run_full_simulation(config)

        # Export to dict
        data = sys_result.to_dict()

        # Verify structure
        assert isinstance(data, dict)
        assert 'time' in data
        assert 'pressure' in data
        assert 'temperature' in data
        assert 'hoop_stress' in data
        assert 'safety_factor' in data
        assert 'failed' in data

        # Verify data types
        assert isinstance(data['time'], list)
        assert isinstance(data['failed'], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
