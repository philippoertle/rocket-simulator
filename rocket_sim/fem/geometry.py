"""
Geometry and Mesh Generation for Pressure Vessel FEM

This module provides geometry definition and simple mesh generation
for cylindrical pressure vessels.

ISO/IEC/IEEE 12207:2017 - Implementation Process
Requirements: FR-4 (FEM stress analysis)
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class VesselMesh:
    """
    Simple structured mesh for cylindrical pressure vessel.

    This is a simplified mesh suitable for axisymmetric analysis
    or basic 3D cylindrical geometries.

    Attributes:
        nodes: Node coordinates (N x 3 array: x, y, z or r, θ, z)
        elements: Element connectivity (M x n array, n=nodes per element)
        boundary_nodes: Dictionary of boundary node sets
                       {'inner': [...], 'outer': [...], 'top': [...], 'bottom': [...]}
        n_radial: Number of elements in radial direction
        n_axial: Number of elements in axial direction
        n_circumferential: Number of elements circumferentially (0 for axisymmetric)
    """
    nodes: np.ndarray
    elements: np.ndarray
    boundary_nodes: Dict[str, List[int]]
    n_radial: int = 10
    n_axial: int = 20
    n_circumferential: int = 0  # 0 = axisymmetric


def create_axisymmetric_mesh(
    inner_radius: float,
    outer_radius: float,
    length: float,
    n_radial: int = 10,
    n_axial: int = 20
) -> VesselMesh:
    """
    Create axisymmetric mesh for cylindrical vessel (2D r-z plane).

    This generates a structured quad mesh suitable for axisymmetric FEM analysis.

    Args:
        inner_radius: Inner radius (m)
        outer_radius: Outer radius (m)
        length: Cylinder length (m)
        n_radial: Number of elements through thickness
        n_axial: Number of elements along length

    Returns:
        VesselMesh with 2D axisymmetric mesh

    Example:
        >>> mesh = create_axisymmetric_mesh(0.0475, 0.04775, 0.30, n_radial=5, n_axial=10)
        >>> print(f"Nodes: {len(mesh.nodes)}, Elements: {len(mesh.elements)}")
    """
    # Create grid in r-z plane
    r = np.linspace(inner_radius, outer_radius, n_radial + 1)
    z = np.linspace(0, length, n_axial + 1)

    # Generate nodes
    nodes = []
    node_id = {}

    for i, z_val in enumerate(z):
        for j, r_val in enumerate(r):
            node_id[(i, j)] = len(nodes)
            nodes.append([r_val, z_val, 0.0])  # r, z, theta=0

    nodes = np.array(nodes)

    # Generate quad elements (4 nodes per element)
    elements = []

    for i in range(n_axial):
        for j in range(n_radial):
            # Quad element nodes (counter-clockwise)
            n1 = node_id[(i, j)]
            n2 = node_id[(i, j+1)]
            n3 = node_id[(i+1, j+1)]
            n4 = node_id[(i+1, j)]
            elements.append([n1, n2, n3, n4])

    elements = np.array(elements)

    # Identify boundary nodes
    boundary_nodes = {
        'inner': [node_id[(i, 0)] for i in range(n_axial + 1)],  # Inner surface
        'outer': [node_id[(i, n_radial)] for i in range(n_axial + 1)],  # Outer surface
        'bottom': [node_id[(0, j)] for j in range(n_radial + 1)],  # Bottom edge
        'top': [node_id[(n_axial, j)] for j in range(n_radial + 1)]  # Top edge
    }

    return VesselMesh(
        nodes=nodes,
        elements=elements,
        boundary_nodes=boundary_nodes,
        n_radial=n_radial,
        n_axial=n_axial,
        n_circumferential=0
    )


def create_1d_radial_mesh(
    inner_radius: float,
    outer_radius: float,
    n_elements: int = 10
) -> VesselMesh:
    """
    Create simple 1D radial mesh through vessel wall thickness.

    This is the simplest mesh for demonstrating thick-wall theory.

    Args:
        inner_radius: Inner radius (m)
        outer_radius: Outer radius (m)
        n_elements: Number of elements through thickness

    Returns:
        VesselMesh with 1D radial mesh

    Example:
        >>> mesh = create_1d_radial_mesh(0.0475, 0.04775, n_elements=10)
        >>> print(f"Nodes: {len(mesh.nodes)}")
    """
    # Create nodes along radius
    r = np.linspace(inner_radius, outer_radius, n_elements + 1)
    nodes = np.column_stack([r, np.zeros_like(r), np.zeros_like(r)])  # r, z=0, θ=0

    # Create line elements (2 nodes per element)
    elements = np.array([[i, i+1] for i in range(n_elements)])

    # Boundary nodes
    boundary_nodes = {
        'inner': [0],
        'outer': [n_elements]
    }

    return VesselMesh(
        nodes=nodes,
        elements=elements,
        boundary_nodes=boundary_nodes,
        n_radial=n_elements,
        n_axial=0,
        n_circumferential=0
    )


def calculate_mesh_quality(mesh: VesselMesh) -> Dict[str, float]:
    """
    Calculate mesh quality metrics.

    Args:
        mesh: VesselMesh object

    Returns:
        Dictionary with quality metrics:
        - element_count: Total elements
        - node_count: Total nodes
        - min_element_size: Minimum element dimension
        - max_element_size: Maximum element dimension
        - aspect_ratio: Average aspect ratio
    """
    metrics = {
        'element_count': len(mesh.elements),
        'node_count': len(mesh.nodes),
    }

    # Calculate element sizes
    element_sizes = []
    aspect_ratios = []

    for elem in mesh.elements:
        # Get element nodes
        elem_nodes = mesh.nodes[elem]

        if len(elem) == 2:  # Line element
            size = np.linalg.norm(elem_nodes[1] - elem_nodes[0])
            element_sizes.append(size)
            aspect_ratios.append(1.0)

        elif len(elem) == 4:  # Quad element
            # Calculate edge lengths
            e1 = np.linalg.norm(elem_nodes[1] - elem_nodes[0])
            e2 = np.linalg.norm(elem_nodes[2] - elem_nodes[1])
            e3 = np.linalg.norm(elem_nodes[3] - elem_nodes[2])
            e4 = np.linalg.norm(elem_nodes[0] - elem_nodes[3])

            min_edge = min(e1, e2, e3, e4)
            max_edge = max(e1, e2, e3, e4)

            element_sizes.append(min_edge)
            aspect_ratios.append(max_edge / min_edge if min_edge > 0 else 1.0)

    if element_sizes:
        metrics['min_element_size'] = min(element_sizes)
        metrics['max_element_size'] = max(element_sizes)
        metrics['aspect_ratio'] = np.mean(aspect_ratios)
    else:
        metrics['min_element_size'] = 0.0
        metrics['max_element_size'] = 0.0
        metrics['aspect_ratio'] = 1.0

    return metrics


def refine_mesh(mesh: VesselMesh, refinement_factor: int = 2) -> VesselMesh:
    """
    Refine mesh by subdividing elements.

    Args:
        mesh: Original mesh
        refinement_factor: Number of subdivisions per element

    Returns:
        Refined mesh

    Note:
        This is a simple uniform refinement. More sophisticated
        adaptive refinement would be needed for production FEM.
    """
    # This is a placeholder - full implementation would be complex
    # For now, just recreate mesh with more elements

    if mesh.n_circumferential == 0:  # Axisymmetric
        # Extract geometry from mesh
        r_inner = np.min(mesh.nodes[:, 0])
        r_outer = np.max(mesh.nodes[:, 0])
        length = np.max(mesh.nodes[:, 1])

        return create_axisymmetric_mesh(
            r_inner, r_outer, length,
            n_radial=mesh.n_radial * refinement_factor,
            n_axial=mesh.n_axial * refinement_factor
        )
    else:
        raise NotImplementedError("3D mesh refinement not yet implemented")


# Demonstration
if __name__ == "__main__":
    print("=== Geometry & Mesh Generation ===\n")

    # Example: 2L PET bottle mesh
    print("Example 1: Axisymmetric mesh for 2L PET bottle")
    print("-" * 50)

    r_inner = 0.0475  # 95mm diameter / 2
    r_outer = 0.04775  # 0.3mm wall thickness
    length = 0.30     # 30cm length

    mesh = create_axisymmetric_mesh(r_inner, r_outer, length, n_radial=5, n_axial=10)

    print(f"Geometry:")
    print(f"  Inner radius: {r_inner*1000:.2f} mm")
    print(f"  Outer radius: {r_outer*1000:.2f} mm")
    print(f"  Wall thickness: {(r_outer-r_inner)*1000:.2f} mm")
    print(f"  Length: {length*1000:.0f} mm")
    print()

    print(f"Mesh:")
    print(f"  Nodes: {len(mesh.nodes)}")
    print(f"  Elements: {len(mesh.elements)}")
    print(f"  Radial elements: {mesh.n_radial}")
    print(f"  Axial elements: {mesh.n_axial}")
    print()

    quality = calculate_mesh_quality(mesh)
    print(f"Quality:")
    print(f"  Min element size: {quality['min_element_size']*1000:.3f} mm")
    print(f"  Max element size: {quality['max_element_size']*1000:.3f} mm")
    print(f"  Aspect ratio: {quality['aspect_ratio']:.2f}")
    print()

    # Example: 1D radial mesh
    print("\nExample 2: 1D radial mesh")
    print("-" * 50)

    mesh_1d = create_1d_radial_mesh(r_inner, r_outer, n_elements=10)
    print(f"  Nodes: {len(mesh_1d.nodes)}")
    print(f"  Elements: {len(mesh_1d.elements)}")
    print(f"  Radial positions: {mesh_1d.nodes[:, 0] * 1000}")  # mm
