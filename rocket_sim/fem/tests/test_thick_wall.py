"""
Unit tests for thick-wall solver (Lamé equations)

ISO/IEC/IEEE 12207:2017 - Verification Process
"""

import pytest
import numpy as np
from rocket_sim.fem.thick_wall_solver import (
    ThickWallResult,
    solve_lame_equations,
    compare_thick_vs_thin_wall,
    calculate_thick_wall_burst_pressure,
    validate_lame_solution,
)
from rocket_sim.system_model import get_material, VesselGeometry


class TestLameEquations:
    """Test Lamé equation solver."""

    def test_solve_lame_basic(self):
        """Test basic Lamé equation solution."""
        result = solve_lame_equations(
            inner_radius=0.05,
            outer_radius=0.055,
            internal_pressure=1e6,  # 1 MPa
            n_points=20
        )

        assert isinstance(result, ThickWallResult)
        assert len(result.r) == 20
        assert len(result.sigma_theta) == 20
        assert len(result.sigma_r) == 20

    def test_boundary_conditions(self):
        """Test that boundary conditions are satisfied."""
        P_i = 500e3  # 500 kPa
        P_o = 0.0

        result = solve_lame_equations(
            inner_radius=0.047,
            outer_radius=0.050,
            internal_pressure=P_i,
            external_pressure=P_o,
            n_points=100
        )

        # At inner surface: σ_r = -P_i
        assert np.isclose(result.sigma_r[0], -P_i, rtol=1e-6)

        # At outer surface: σ_r = -P_o = 0
        assert np.isclose(result.sigma_r[-1], -P_o, rtol=1e-6)

    def test_hoop_stress_maximum_at_inner(self):
        """Test that hoop stress is maximum at inner surface."""
        result = solve_lame_equations(
            inner_radius=0.05,
            outer_radius=0.055,
            internal_pressure=1e6,
            n_points=50
        )

        # Maximum hoop stress should occur at inner surface
        max_idx = np.argmax(result.sigma_theta)
        assert max_idx == 0

    def test_hoop_stress_positive(self):
        """Test that hoop stress is positive for internal pressure."""
        result = solve_lame_equations(
            inner_radius=0.05,
            outer_radius=0.055,
            internal_pressure=1e6,
            n_points=30
        )

        # All hoop stresses should be positive
        assert np.all(result.sigma_theta > 0)

    def test_stress_decreases_through_thickness(self):
        """Test that stresses decrease from inner to outer surface."""
        result = solve_lame_equations(
            inner_radius=0.05,
            outer_radius=0.055,
            internal_pressure=1e6,
            n_points=50
        )

        # Hoop stress should decrease monotonically
        diffs = np.diff(result.sigma_theta)
        assert np.all(diffs <= 0)  # Non-increasing


class TestThickVsThinWall:
    """Test comparison between thick and thin-wall theories."""

    def test_thin_wall_limit(self):
        """Test that thin wall (t→0) approaches thin-wall theory."""
        # Very thin wall
        r_i = 0.0475
        t = 0.0001  # Very thin: t/D = 0.001
        r_o = r_i + t
        P = 500e3

        geom = VesselGeometry(inner_diameter=2*r_i, wall_thickness=t)
        pet = get_material("PET")

        comparison = compare_thick_vs_thin_wall(geom, P, pet)

        # Error should be very small for thin walls
        assert comparison['thickness_ratio'] < 0.01
        assert comparison['thin_wall_valid']
        assert comparison['error_percent'] < 1.0  # < 1% error

    def test_thick_wall_deviation(self):
        """Test that thick walls deviate from thin-wall theory."""
        # Moderately thick wall
        r_i = 0.05
        t = 0.008  # t/D = 0.08 (marginal)
        r_o = r_i + t
        P = 1e6

        geom = VesselGeometry(inner_diameter=2*r_i, wall_thickness=t)
        pet = get_material("PET")

        comparison = compare_thick_vs_thin_wall(geom, P, pet)

        # Should show measurable error
        assert comparison['error_percent'] > 2.0  # > 2% error
        assert comparison['hoop_stress_thick_max'] > comparison['hoop_stress_thin']

    def test_thin_wall_assumption_validity(self):
        """Test thin-wall assumption validity flag."""
        pet = get_material("PET")
        P = 500e3

        # Thin wall
        geom_thin = VesselGeometry(inner_diameter=0.095, wall_thickness=0.0003)
        comp_thin = compare_thick_vs_thin_wall(geom_thin, P, pet)
        assert comp_thin['thin_wall_valid']

        # Thick wall
        geom_thick = VesselGeometry(inner_diameter=0.095, wall_thickness=0.012)
        comp_thick = compare_thick_vs_thin_wall(geom_thick, P, pet)
        assert not comp_thick['thin_wall_valid']


class TestDisplacementCalculation:
    """Test displacement calculations."""

    def test_displacement_with_material(self):
        """Test that displacement is calculated when material provided."""
        pet = get_material("PET")

        result = solve_lame_equations(
            inner_radius=0.047,
            outer_radius=0.050,
            internal_pressure=500e3,
            material=pet,
            n_points=20
        )

        # Displacement should be non-zero
        assert np.any(result.u_r != 0)

        # Displacement should be positive (expansion)
        assert np.all(result.u_r > 0)

    def test_no_displacement_without_material(self):
        """Test that displacement is zero when no material provided."""
        result = solve_lame_equations(
            inner_radius=0.047,
            outer_radius=0.050,
            internal_pressure=500e3,
            material=None,
            n_points=20
        )

        # Displacement should be zero
        assert np.all(result.u_r == 0)


class TestBurstPressure:
    """Test burst pressure calculations."""

    def test_thick_wall_burst_pressure(self):
        """Test thick-wall burst pressure calculation."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.005)
        pet = get_material("PET")

        P_burst = calculate_thick_wall_burst_pressure(geom, pet, use_yield=True)

        # Should be positive and reasonable
        assert P_burst > 0
        assert 100e3 < P_burst < 10e6  # Between 100 kPa and 10 MPa

    def test_thicker_wall_higher_burst(self):
        """Test that thicker walls have higher burst pressure."""
        pet = get_material("PET")

        geom_thin = VesselGeometry(inner_diameter=0.095, wall_thickness=0.003)
        geom_thick = VesselGeometry(inner_diameter=0.095, wall_thickness=0.006)

        P_thin = calculate_thick_wall_burst_pressure(geom_thin, pet)
        P_thick = calculate_thick_wall_burst_pressure(geom_thick, pet)

        assert P_thick > P_thin

    def test_ultimate_vs_yield_burst(self):
        """Test that ultimate strength gives higher burst pressure."""
        geom = VesselGeometry(inner_diameter=0.095, wall_thickness=0.004)
        pet = get_material("PET")

        P_yield = calculate_thick_wall_burst_pressure(geom, pet, use_yield=True)
        P_ultimate = calculate_thick_wall_burst_pressure(geom, pet, use_yield=False)

        assert P_ultimate > P_yield


class TestSolutionValidation:
    """Test solution validation checks."""

    def test_validate_correct_solution(self):
        """Test validation of correct Lamé solution."""
        P_i = 800e3
        P_o = 0.0

        result = solve_lame_equations(
            inner_radius=0.047,
            outer_radius=0.050,
            internal_pressure=P_i,
            external_pressure=P_o,
            n_points=100
        )

        validation = validate_lame_solution(result, P_i, P_o)

        # All validation checks should pass
        assert validation['bc_inner']
        assert validation['bc_outer']
        assert validation['hoop_max_inner']
        assert validation['hoop_positive']

    def test_validation_with_external_pressure(self):
        """Test validation with both internal and external pressure."""
        P_i = 1e6
        P_o = 100e3

        result = solve_lame_equations(
            inner_radius=0.05,
            outer_radius=0.055,
            internal_pressure=P_i,
            external_pressure=P_o,
            n_points=50
        )

        validation = validate_lame_solution(result, P_i, P_o)

        # Boundary conditions should still be satisfied
        assert validation['bc_inner']
        assert validation['bc_outer']


class TestVonMisesStress:
    """Test von Mises stress calculation."""

    def test_von_mises_positive(self):
        """Test that von Mises stress is always positive."""
        result = solve_lame_equations(
            inner_radius=0.05,
            outer_radius=0.055,
            internal_pressure=1e6,
            n_points=30
        )

        # Von Mises should always be positive
        assert np.all(result.sigma_vm > 0)

    def test_von_mises_maximum_at_inner(self):
        """Test that maximum von Mises occurs at inner surface."""
        result = solve_lame_equations(
            inner_radius=0.047,
            outer_radius=0.050,
            internal_pressure=800e3,
            n_points=50
        )

        # Maximum should be at or near inner surface
        max_idx = np.argmax(result.sigma_vm)
        assert max_idx < 5  # Within first few points


class TestLiteratureValidation:
    """Validate against published results."""

    def test_roark_example(self):
        """Compare with Roark's Formulas example (simplified).

        Roark's gives example with known geometry and pressure.
        """
        # Simplified example: r_i=50mm, r_o=60mm, P_i=10MPa
        r_i = 0.050
        r_o = 0.060
        P = 10e6

        result = solve_lame_equations(r_i, r_o, P, n_points=100)

        # At inner surface (r=r_i):
        # σ_θ = P * (r_o² + r_i²) / (r_o² - r_i²)
        sigma_theta_inner_theory = P * (r_o**2 + r_i**2) / (r_o**2 - r_i**2)

        # Compare with calculated
        assert np.isclose(result.sigma_theta[0], sigma_theta_inner_theory, rtol=1e-6)

    def test_pet_bottle_realistic_stresses(self):
        """Test that PET bottle stresses are in realistic range."""
        # Typical 2L bottle at 500 kPa
        r_i = 0.0475
        t = 0.0003
        r_o = r_i + t
        P = 500e3

        pet = get_material("PET")
        result = solve_lame_equations(r_i, r_o, P, material=pet)

        max_stress = np.max(result.sigma_vm)

        # Should be well below yield strength (55 MPa)
        assert max_stress < pet.yield_strength

        # Should be in tens of MPa range
        assert 10e6 < max_stress < 100e6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
