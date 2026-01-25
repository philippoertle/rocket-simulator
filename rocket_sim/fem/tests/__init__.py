"""
Unit tests for FEM geometry module

ISO/IEC/IEEE 12207:2017 - Verification Process
"""

import pytest
import numpy as np
from rocket_sim.fem.geometry import (
    VesselMesh,
    create_axisymmetric_mesh,
    create_1d_radial_mesh,
    calculate_mesh_quality,
    refine_mesh,
)


class TestVesselMesh:
    """Test VesselMesh dataclass."""

    def test_create_vessel_mesh(self):
        """Test creating VesselMesh object."""
        nodes = np.array([[0.1, 0.0, 0.0], [0.1, 0.1, 0.0]])
        elements = np.array([[0, 1]])
        boundary = {'inner': [0], 'outer': [1]}

        mesh = VesselMesh(
            nodes=nodes,
            elements=elements,
            boundary_nodes=boundary,
            n_radial=1,
            n_axial=1
        )

        assert mesh.nodes.shape == (2, 3)
        assert mesh.elements.shape == (1, 2)
        assert 'inner' in mesh.boundary_nodes


class TestAxisymmetricMesh:
    """Test axisymmetric mesh generation."""

    def test_create_simple_mesh(self):
        """Test creating simple axisymmetric mesh."""
        mesh = create_axisymmetric_mesh(
            inner_radius=0.05,
            outer_radius=0.051,
            length=0.1,
            n_radial=2,
            n_axial=4
        )

        # Check dimensions
        assert mesh.n_radial == 2
        assert mesh.n_axial == 4

        # Number of nodes: (n_radial+1) * (n_axial+1)
        expected_nodes = (2+1) * (4+1)
        assert len(mesh.nodes) == expected_nodes

        # Number of elements: n_radial * n_axial
        expected_elements = 2 * 4
        assert len(mesh.elements) == expected_elements

        # Each quad element has 4 nodes
        assert mesh.elements.shape[1] == 4

    def test_mesh_geometry_bounds(self):
        """Test that mesh covers correct geometric region."""
        r_i = 0.047
        r_o = 0.050
        length = 0.30

        mesh = create_axisymmetric_mesh(r_i, r_o, length, n_radial=5, n_axial=10)

        # Check radial bounds
        r_vals = mesh.nodes[:, 0]
        assert np.isclose(np.min(r_vals), r_i, rtol=1e-10)
        assert np.isclose(np.max(r_vals), r_o, rtol=1e-10)

        # Check axial bounds
        z_vals = mesh.nodes[:, 1]
        assert np.isclose(np.min(z_vals), 0.0, rtol=1e-10)
        assert np.isclose(np.max(z_vals), length, rtol=1e-10)

    def test_boundary_nodes_identified(self):
        """Test that boundary nodes are correctly identified."""
        mesh = create_axisymmetric_mesh(0.05, 0.051, 0.1, n_radial=3, n_axial=5)

        # Should have all four boundaries
        assert 'inner' in mesh.boundary_nodes
        assert 'outer' in mesh.boundary_nodes
        assert 'bottom' in mesh.boundary_nodes
        assert 'top' in mesh.boundary_nodes

        # Check sizes
        assert len(mesh.boundary_nodes['inner']) == 5+1  # n_axial+1
        assert len(mesh.boundary_nodes['outer']) == 5+1
        assert len(mesh.boundary_nodes['bottom']) == 3+1  # n_radial+1
        assert len(mesh.boundary_nodes['top']) == 3+1

    def test_element_connectivity(self):
        """Test that elements have valid node connectivity."""
        mesh = create_axisymmetric_mesh(0.05, 0.051, 0.1, n_radial=2, n_axial=2)

        # All element nodes should be valid indices
        max_node_id = len(mesh.nodes) - 1
        assert np.all(mesh.elements >= 0)
        assert np.all(mesh.elements <= max_node_id)


class Test1DRadialMesh:
    """Test 1D radial mesh generation."""

    def test_create_1d_mesh(self):
        """Test creating 1D radial mesh."""
        mesh = create_1d_radial_mesh(0.05, 0.051, n_elements=10)

        # Should have n_elements+1 nodes
        assert len(mesh.nodes) == 11

        # Should have n_elements line elements
        assert len(mesh.elements) == 10

        # Each line element has 2 nodes
        assert mesh.elements.shape[1] == 2

    def test_1d_mesh_uniform_spacing(self):
        """Test that 1D mesh has uniform spacing."""
        r_i = 0.047
        r_o = 0.050
        n_elem = 15

        mesh = create_1d_radial_mesh(r_i, r_o, n_elements=n_elem)

        # Calculate element sizes
        element_sizes = []
        for elem in mesh.elements:
            n1, n2 = elem
            dr = np.linalg.norm(mesh.nodes[n2] - mesh.nodes[n1])
            element_sizes.append(dr)

        # All elements should be same size (uniform mesh)
        expected_size = (r_o - r_i) / n_elem
        for size in element_sizes:
            assert np.isclose(size, expected_size, rtol=1e-10)

    def test_1d_boundary_nodes(self):
        """Test 1D mesh boundary nodes."""
        mesh = create_1d_radial_mesh(0.05, 0.051, n_elements=10)

        assert 'inner' in mesh.boundary_nodes
        assert 'outer' in mesh.boundary_nodes

        # Inner boundary should be node 0
        assert mesh.boundary_nodes['inner'] == [0]

        # Outer boundary should be last node
        assert mesh.boundary_nodes['outer'] == [10]


class TestMeshQuality:
    """Test mesh quality calculations."""

    def test_quality_metrics_axisymmetric(self):
        """Test quality metrics for axisymmetric mesh."""
        mesh = create_axisymmetric_mesh(0.05, 0.051, 0.1, n_radial=5, n_axial=10)

        quality = calculate_mesh_quality(mesh)

        # Check that all metrics are present
        assert 'element_count' in quality
        assert 'node_count' in quality
        assert 'min_element_size' in quality
        assert 'max_element_size' in quality
        assert 'aspect_ratio' in quality

        # Check values are reasonable
        assert quality['element_count'] == 5 * 10
        assert quality['node_count'] == (5+1) * (10+1)
        assert quality['min_element_size'] > 0
        assert quality['max_element_size'] > 0
        assert quality['aspect_ratio'] >= 1.0

    def test_quality_metrics_1d(self):
        """Test quality metrics for 1D mesh."""
        mesh = create_1d_radial_mesh(0.05, 0.051, n_elements=10)

        quality = calculate_mesh_quality(mesh)

        assert quality['element_count'] == 10
        assert quality['node_count'] == 11
        assert quality['aspect_ratio'] == 1.0  # Line elements


class TestMeshRefinement:
    """Test mesh refinement."""

    def test_refine_axisymmetric_mesh(self):
        """Test refining axisymmetric mesh."""
        mesh_coarse = create_axisymmetric_mesh(0.05, 0.051, 0.1, n_radial=2, n_axial=4)
        mesh_fine = refine_mesh(mesh_coarse, refinement_factor=2)

        # Refined mesh should have more elements
        assert mesh_fine.n_radial == mesh_coarse.n_radial * 2
        assert mesh_fine.n_axial == mesh_coarse.n_axial * 2

        # Element count should increase by factor²
        assert len(mesh_fine.elements) == len(mesh_coarse.elements) * 4

    def test_refined_mesh_covers_same_domain(self):
        """Test that refined mesh covers same geometric domain."""
        r_i, r_o, L = 0.047, 0.050, 0.30

        mesh_coarse = create_axisymmetric_mesh(r_i, r_o, L, n_radial=2, n_axial=4)
        mesh_fine = refine_mesh(mesh_coarse, refinement_factor=3)

        # Both meshes should have same bounds
        assert np.isclose(np.min(mesh_fine.nodes[:, 0]), r_i, rtol=1e-10)
        assert np.isclose(np.max(mesh_fine.nodes[:, 0]), r_o, rtol=1e-10)
        assert np.isclose(np.min(mesh_fine.nodes[:, 1]), 0.0, rtol=1e-10)
        assert np.isclose(np.max(mesh_fine.nodes[:, 1]), L, rtol=1e-10)


class TestPETBottleMesh:
    """Test mesh generation for realistic PET bottle geometry."""

    def test_typical_pet_bottle_mesh(self):
        """Test mesh for typical 2L PET bottle."""
        # Typical geometry
        r_i = 0.0475  # 95mm diameter
        t = 0.0003    # 0.3mm wall
        r_o = r_i + t
        L = 0.30      # 30cm length

        mesh = create_axisymmetric_mesh(r_i, r_o, L, n_radial=5, n_axial=15)

        # Mesh should be created successfully
        assert mesh is not None
        assert len(mesh.nodes) > 0
        assert len(mesh.elements) > 0

        # Quality should be reasonable
        quality = calculate_mesh_quality(mesh)
        assert quality['aspect_ratio'] < 10  # Not too distorted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
