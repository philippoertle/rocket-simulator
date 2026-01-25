"""
Unit tests for stress concentrations module

ISO/IEC/IEEE 12207:2017 - Verification Process
"""

import pytest
import numpy as np
from rocket_sim.fem.stress_concentrations import (
    calculate_end_cap_stress_factor,
    calculate_thread_stress_factor,
    calculate_transition_radius_factor,
    calculate_maximum_stress,
    estimate_failure_location,
)
from rocket_sim.system_model import get_material, VesselGeometry


class TestEndCapStressFactors:
    """Test end cap stress concentration factors."""

    def test_hemispherical_cap_ideal(self):
        """Test that hemispherical cap has K=1.0 (ideal)."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        K = calculate_end_cap_stress_factor(geom, "hemispherical")
        assert K == 1.0

    def test_flat_cap_high_stress(self):
        """Test that flat cap has high stress concentration."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        K = calculate_end_cap_stress_factor(geom, "flat")
        assert K > 2.0

    def test_cap_factor_ordering(self):
        """Test that stress factors are ordered correctly."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)

        K_hemi = calculate_end_cap_stress_factor(geom, "hemispherical")
        K_ellip = calculate_end_cap_stress_factor(geom, "elliptical")
        K_flat = calculate_end_cap_stress_factor(geom, "flat")

        # Should be ordered: hemisph < elliptical < flat
        assert K_hemi < K_ellip < K_flat

    def test_invalid_cap_type(self):
        """Test that invalid cap type raises error."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)

        with pytest.raises(ValueError, match="Unknown cap type"):
            calculate_end_cap_stress_factor(geom, "invalid_type")


class TestThreadStressFactors:
    """Test thread stress concentration factors."""

    def test_thread_factor_range(self):
        """Test that thread factors are in reasonable range."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        K = calculate_thread_stress_factor(geom)

        # Threads typically K=2.0 to 4.5
        assert 2.0 <= K <= 4.5

    def test_sharper_threads_higher_stress(self):
        """Test that sharper threads have higher stress."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)

        # Sharp thread (small radius)
        K_sharp = calculate_thread_stress_factor(geom, thread_radius=0.00001)

        # Rounded thread (larger radius)
        K_round = calculate_thread_stress_factor(geom, thread_radius=0.0001)

        assert K_sharp > K_round


class TestMaximumStress:
    """Test maximum stress calculation."""

    def test_maximum_stress_calculation(self):
        """Test maximum stress with stress concentrations."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")
        P = 500e3

        result = calculate_maximum_stress(P, geom, pet, cap_type="flat")

        assert 'sigma_nominal' in result
        assert 'sigma_max' in result
        assert 'K_total' in result
        assert 'location' in result

        # Max should be greater than nominal
        assert result['sigma_max'] > result['sigma_nominal']

    def test_hemispherical_vs_flat_stress(self):
        """Test that flat cap gives higher stress than hemispherical."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")
        P = 600e3

        result_hemi = calculate_maximum_stress(P, geom, pet, cap_type="hemispherical")
        result_flat = calculate_maximum_stress(P, geom, pet, cap_type="flat")

        assert result_flat['sigma_max'] > result_hemi['sigma_max']

    def test_thread_increases_stress(self):
        """Test that including threads increases maximum stress."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        pet = get_material("PET")
        P = 500e3

        result_no_thread = calculate_maximum_stress(P, geom, pet, include_thread=False)
        result_with_thread = calculate_maximum_stress(P, geom, pet, include_thread=True)

        assert result_with_thread['K_total'] >= result_no_thread['K_total']


class TestFailureLocationPrediction:
    """Test failure location prediction."""

    def test_flat_cap_failure_prediction(self):
        """Test failure location for flat cap bottle."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)

        location = estimate_failure_location(800e3, geom, "flat")

        # Should predict cap or thread failure (not body)
        assert "cap" in location.lower() or "thread" in location.lower()

    def test_hemispherical_cap_failure(self):
        """Test failure location for ideal hemispherical cap."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)

        location = estimate_failure_location(800e3, geom, "hemispherical")

        # With ideal cap, threads are likely critical
        assert "thread" in location.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
