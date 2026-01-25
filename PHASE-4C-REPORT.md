# Phase 4C: FEM Structural Analysis - Implementation Plan

**ISO/IEC/IEEE 12207:2017 §6.4.7 Implementation Process**  
**Phase:** 4C - FEM Structural Analysis  
**Date:** January 25, 2026  
**Status:** 🟡 IN PROGRESS

---

## Objectives

Implement Module 3 (FEM) to perform detailed 3D structural analysis of pressure vessels under internal pressure loading. This module will validate and extend the analytical results from Module 2 using finite element methods.

---

## Scope

### In Scope
1. **Mesh Generation**
   - Cylindrical vessel geometry creation
   - Automatic mesh refinement
   - Boundary condition application

2. **FEM Solver**
   - Linear elastic stress analysis
   - Displacement/strain calculation
   - Von Mises stress computation
   - Integration with pressure loading from Module 2

3. **Validation**
   - Compare FEM vs analytical (Module 2)
   - Convergence studies
   - Physical consistency checks

4. **Alternative: Simplified FEM**
   - If FEniCSx proves too complex, implement simplified analytical 3D model
   - Use NumPy/SciPy for matrix assembly
   - Focus on educational value over production FEM

### Out of Scope (Phase 4D)
- Non-linear material models (plasticity)
- Dynamic/transient FEM
- Thermal-structural coupling
- Complex geometries (non-cylindrical)

---

## Design Decision: Simplified Approach

Given the educational focus and time constraints, we'll implement a **hybrid approach**:

1. **Primary: Analytical 3D Extension** (60% effort)
   - Extend Module 2 with axisymmetric formulation
   - Include stress concentrations at end caps
   - Radial stress variation (not just thin-wall)

2. **Secondary: Basic FEM Framework** (40% effort)
   - Simple 1D axisymmetric FEM for demonstration
   - NumPy-based implementation (no external FEM library)
   - Educational value: show FEM principles

This approach:
- ✅ Avoids FEniCSx installation complexity
- ✅ Maintains educational value
- ✅ Provides validation against analytical results
- ✅ Completes Phase 4C in reasonable time
- ✅ Meets FR-4 requirement (stress analysis)

---

## Module 3 Architecture

```
rocket_sim/fem/
├── __init__.py
├── geometry.py           # Vessel geometry & mesh generation
├── thick_wall_solver.py  # Lamé equations for thick walls
├── stress_concentrations.py  # End cap & neck stress factors
├── simple_fem.py         # Basic 1D axisymmetric FEM
└── tests/
    ├── __init__.py
    ├── test_geometry.py
    ├── test_thick_wall.py
    ├── test_stress_concentrations.py
    └── test_simple_fem.py
```

---

## API Design

### 1. Geometry (`geometry.py`)

```python
@dataclass
class VesselMesh:
    """Simple mesh for cylindrical vessel"""
    nodes: np.ndarray          # Node coordinates
    elements: np.ndarray       # Element connectivity
    boundary_nodes: Dict[str, List[int]]  # Boundary node sets

def create_cylindrical_mesh(
    geometry: VesselGeometry,
    n_radial: int = 10,
    n_axial: int = 20,
    n_circumferential: int = 16
) -> VesselMesh:
    """Generate structured mesh for cylinder"""
```

### 2. Thick-Wall Solver (`thick_wall_solver.py`)

```python
def solve_thick_wall_cylinder(
    inner_radius: float,
    outer_radius: float,
    internal_pressure: float,
    external_pressure: float,
    material: MaterialProperties,
    r_eval: Optional[np.ndarray] = None
) -> Dict[str, np.ndarray]:
    """
    Solve Lamé equations for thick-wall cylinder.
    
    Returns:
        {
            'r': radial positions,
            'sigma_r': radial stress,
            'sigma_theta': hoop stress,
            'sigma_z': axial stress,
            'sigma_vm': von Mises stress,
            'u_r': radial displacement
        }
    """
```

### 3. Stress Concentrations (`stress_concentrations.py`)

```python
def calculate_end_cap_stress_factor(
    geometry: VesselGeometry,
    cap_type: str = "hemispherical"
) -> float:
    """
    Calculate stress concentration factor for end caps.
    
    cap_type: "flat", "hemispherical", "elliptical"
    """

def calculate_maximum_stress(
    pressure: float,
    geometry: VesselGeometry,
    material: MaterialProperties,
    include_concentrations: bool = True
) -> Dict[str, float]:
    """Calculate peak stresses including concentrations"""
```

### 4. Simple FEM (`simple_fem.py`)

```python
def solve_axisymmetric_fem(
    mesh: VesselMesh,
    material: MaterialProperties,
    pressure: float,
    element_order: int = 1
) -> Dict[str, np.ndarray]:
    """
    Simple 1D axisymmetric FEM solver for educational purposes.
    
    Returns displacement and stress at nodes.
    """
```

---

## Implementation Tasks

### Task 1: Geometry & Meshing ✅
**File:** `rocket_sim/fem/geometry.py`
**Effort:** 1 hour
- [ ] Define VesselMesh dataclass
- [ ] Implement cylindrical mesh generator
- [ ] Boundary node identification
- [ ] Unit tests

### Task 2: Thick-Wall Solver ✅
**File:** `rocket_sim/fem/thick_wall_solver.py`
**Effort:** 1.5 hours
- [ ] Implement Lamé equations
- [ ] Radial stress variation
- [ ] Displacement calculation
- [ ] Compare with thin-wall (Module 2)
- [ ] Unit tests

### Task 3: Stress Concentrations ✅
**File:** `rocket_sim/fem/stress_concentrations.py`
**Effort:** 1 hour
- [ ] End cap stress concentration factors
- [ ] Neck/thread stress factors
- [ ] Maximum stress calculator
- [ ] Unit tests

### Task 4: Simple FEM Solver ✅
**File:** `rocket_sim/fem/simple_fem.py`
**Effort:** 2 hours
- [ ] 1D axisymmetric element formulation
- [ ] Stiffness matrix assembly
- [ ] Boundary condition application
- [ ] Stress recovery
- [ ] Unit tests

### Task 5: Integration ✅
**File:** `rocket_sim/fem/fem_integrator.py`
**Effort:** 1 hour
- [ ] Connect Module 2 → Module 3
- [ ] Comparison utilities (analytical vs FEM)
- [ ] Integration tests

### Task 6: Testing & Validation ✅
**Effort:** 1.5 hours
- [ ] 40+ unit tests
- [ ] Convergence studies
- [ ] Validation against literature
- [ ] Physical consistency checks

---

## Test Plan

### Unit Tests (40+ planned)

#### Geometry Module (8 tests)
1. Mesh generation for typical bottle
2. Node numbering correctness
3. Boundary node identification
4. Mesh refinement behavior

#### Thick-Wall Module (12 tests)
5. Lamé equation accuracy (compare with hand calc)
6. Thick vs thin wall comparison
7. Stress distribution across thickness
8. Displacement calculation
9. Limit case: t→0 matches thin-wall
10. Limit case: P_ext=0
11. Material property variations

#### Stress Concentrations (10 tests)
12. Hemispherical cap stress factor
13. Flat cap stress factor
14. Comparison with literature values
15. Peak stress location
16. Thread stress concentration
17. Transition radius effects

#### Simple FEM (10 tests)
18. Single element test
19. Convergence with mesh refinement
20. Comparison with analytical (Lamé)
21. Energy balance check
22. Boundary condition enforcement
23. Symmetry verification

### Integration Tests (10 tests)
24. Module 2 → Module 3 data flow
25. Pressure loading from combustion
26. Analytical vs FEM comparison
27. Failure prediction consistency

---

## Acceptance Criteria

### Functionality
- [ ] Thick-wall solver matches literature (±2%)
- [ ] FEM solver converges with refinement
- [ ] Stress concentrations in realistic range (1.5-3.0x)
- [ ] Integration with Module 2 seamless

### Performance
- [ ] Thick-wall solver: instant (<0.1s)
- [ ] Simple FEM: <5s for typical mesh

### Quality
- [ ] 100% test pass rate
- [ ] >85% code coverage
- [ ] All functions documented

### Validation
- [ ] Thick-wall matches Lamé (exact)
- [ ] FEM matches analytical (±5%)
- [ ] Stress concentrations match literature

---

## Deliverables

1. **Code**
   - `geometry.py` (~150 LOC)
   - `thick_wall_solver.py` (~200 LOC)
   - `stress_concentrations.py` (~150 LOC)
   - `simple_fem.py` (~300 LOC)
   - `fem_integrator.py` (~100 LOC)
   - **Total: ~900 LOC**

2. **Tests**
   - 40+ unit tests (~800 LOC)
   - Integration tests (~200 LOC)

3. **Documentation**
   - Theory guide (Lamé equations, FEM basics)
   - Usage examples
   - Validation reports

---

## Theory Background

### Lamé Equations (Thick-Wall Cylinder)

For thick-wall cylinder with inner radius $r_i$, outer radius $r_o$:

**Hoop Stress:**
$$\sigma_\theta(r) = \frac{P_i r_i^2 - P_o r_o^2}{r_o^2 - r_i^2} + \frac{(P_i - P_o) r_i^2 r_o^2}{(r_o^2 - r_i^2) r^2}$$

**Radial Stress:**
$$\sigma_r(r) = \frac{P_i r_i^2 - P_o r_o^2}{r_o^2 - r_i^2} - \frac{(P_i - P_o) r_i^2 r_o^2}{(r_o^2 - r_i^2) r^2}$$

**Radial Displacement:**
$$u_r(r) = \frac{1}{E} \left[ (1-\nu) \frac{P_i r_i^2 - P_o r_o^2}{r_o^2 - r_i^2} r + (1+\nu) \frac{(P_i - P_o) r_i^2 r_o^2}{(r_o^2 - r_i^2) r} \right]$$

### Stress Concentration Factors

- **Hemispherical cap:** K ≈ 1.0 (ideal)
- **Flat cap:** K ≈ 2.0-3.0 (high concentration)
- **Thread/neck:** K ≈ 2.5-4.0 (critical region)

---

## Schedule

**Estimated Time:** 8 hours total

- **Hour 1:** Geometry & meshing
- **Hour 2-3:** Thick-wall solver
- **Hour 4:** Stress concentrations
- **Hour 5-6:** Simple FEM implementation
- **Hour 7:** Integration with Module 2
- **Hour 8:** Testing & validation

**Target Completion:** January 25, 2026 (same day)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| FEM complexity too high | High | Use simplified analytical approach |
| Mesh generation errors | Medium | Extensive validation tests |
| Numerical instability | Medium | Condition number checks |
| Time overrun | Medium | Prioritize thick-wall solver over FEM |

---

## Success Metrics

- [ ] Lamé solver implemented and validated
- [ ] Stress concentrations calculated
- [ ] Simple FEM working (even if basic)
- [ ] 40+ tests passing
- [ ] Integration with Module 2
- [ ] Documentation complete

---

**Status:** Ready to implement  
**Next Step:** Create geometry module  
**Updated:** January 25, 2026
