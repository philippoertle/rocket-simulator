# Phase 4B: System Modeling - Implementation Plan

**ISO/IEC/IEEE 12207:2017 §6.4.7 Implementation Process**  
**Phase:** 4B - System Modeling  
**Date:** January 25, 2026  
**Status:** 🟡 IN PROGRESS

---

## Objectives

Implement Module 2 (System Model) to simulate the complete rocket system dynamics using ordinary differential equations (ODEs). This module integrates combustion data from Module 1 with pressure vessel physics to predict system behavior over time.

---

## Scope

### In Scope
1. **ODE System Solver**
   - Pressure dynamics (combustion + structural response)
   - Temperature evolution
   - Mass flow (if applicable)
   - Time integration using SciPy

2. **Analytical Burst Calculator**
   - Thin-wall pressure vessel theory
   - Von Mises stress criterion
   - Safety factor calculation
   - Failure prediction

3. **System Integrator**
   - Bridge Module 1 (combustion) → Module 2 (system dynamics)
   - Handle time-dependent combustion data
   - Predict pressure vessel failure point

4. **Unit Tests**
   - ODE solver validation
   - Analytical calculations verification
   - Integration tests with Module 1
   - Physical consistency checks

### Out of Scope (Phase 4C/4D)
- FEM structural analysis (Module 3)
- GUI/CLI development
- Visualization tools
- Performance optimization

---

## Requirements Coverage

### Functional Requirements
- **FR-2:** ODE solver for system dynamics ✅ This phase
- **FR-3:** Analytical burst calculator ✅ This phase
- **FR-6:** Parametric studies (partial) ✅ Framework

### Non-Functional Requirements
- **NFR-4:** Reproducibility ✅ Deterministic ODEs
- **NFR-5:** Performance ✅ Benchmark solver speed
- **NFR-6:** Maintainability ✅ Modular design
- **NFR-9:** Safety warnings ✅ Burst prediction

---

## Design

### Module 2 Architecture

```
rocket_sim/system_model/
├── __init__.py
├── ode_solver.py          # ODE system definition & solver
├── burst_calculator.py    # Analytical burst prediction
├── system_integrator.py   # Connects M1 → M2
└── tests/
    ├── __init__.py
    ├── test_ode_solver.py
    ├── test_burst_calculator.py
    └── test_integration.py
```

### API Design

#### 1. ODE Solver (`ode_solver.py`)

```python
@dataclass
class SystemState:
    """System state variables"""
    time: np.ndarray           # s
    pressure: np.ndarray       # Pa
    temperature: np.ndarray    # K
    volume: np.ndarray         # m³
    hoop_stress: np.ndarray    # Pa
    safety_factor: np.ndarray  # dimensionless
    failed: bool
    failure_time: Optional[float]

def simulate_system_dynamics(
    combustion_result: CombustionResult,
    vessel_diameter: float,      # m
    vessel_thickness: float,     # m
    vessel_material: str,        # "PET", "HDPE", etc.
    end_time: float = 1.0,       # s
    max_step: float = 1e-4       # s
) -> SystemState:
    """
    Simulate complete system dynamics with combustion + structural response.
    
    ODEs:
    - dP/dt from combustion data (interpolated)
    - Structural response (elastic deformation)
    - Failure detection
    """
```

#### 2. Burst Calculator (`burst_calculator.py`)

```python
@dataclass
class VesselGeometry:
    diameter: float      # m (inner)
    thickness: float     # m (wall)
    length: float        # m
    material: str

@dataclass
class MaterialProperties:
    name: str
    yield_strength: float    # Pa
    tensile_strength: float  # Pa
    elastic_modulus: float   # Pa
    poisson_ratio: float

def calculate_burst_pressure(
    geometry: VesselGeometry,
    material: MaterialProperties,
    safety_factor: float = 1.0
) -> float:
    """
    Calculate theoretical burst pressure using thin-wall theory.
    
    Barlow's formula: P_burst = 2 * σ_yield * t / D
    """

def calculate_hoop_stress(
    pressure: float,
    geometry: VesselGeometry
) -> float:
    """
    Calculate hoop stress: σ_hoop = P * D / (2 * t)
    """

def check_failure_criterion(
    stress_state: Dict[str, float],
    material: MaterialProperties
) -> Tuple[bool, float]:
    """
    Check von Mises failure criterion.
    Returns (failed: bool, safety_factor: float)
    """
```

#### 3. System Integrator (`system_integrator.py`)

```python
def run_full_simulation(
    fuel_oxidizer_ratio: float,
    vessel_config: VesselGeometry,
    initial_conditions: Dict[str, float],
    end_time: float = 1.0
) -> Tuple[CombustionResult, SystemState]:
    """
    End-to-end simulation: combustion → system dynamics → failure prediction
    
    1. Run Module 1: simulate_combustion()
    2. Run Module 2: simulate_system_dynamics()
    3. Detect failure point
    4. Return complete results
    """
```

---

## Implementation Tasks

### Task 1: Material Properties Database ✅
**File:** `rocket_sim/system_model/materials.py`
**Effort:** 30 min
- [ ] Define MaterialProperties dataclass
- [ ] Create material database (PET, HDPE, Aluminum)
- [ ] Add getter function `get_material(name)`
- [ ] Unit tests for material lookup

### Task 2: Burst Calculator ✅
**File:** `rocket_sim/system_model/burst_calculator.py`
**Effort:** 1 hour
- [ ] Implement `calculate_burst_pressure()`
- [ ] Implement `calculate_hoop_stress()`
- [ ] Implement `calculate_axial_stress()`
- [ ] Implement `check_failure_criterion()` (von Mises)
- [ ] Unit tests (compare with hand calculations)

### Task 3: ODE Solver ✅
**File:** `rocket_sim/system_model/ode_solver.py`
**Effort:** 2 hours
- [ ] Define `SystemState` dataclass
- [ ] Implement ODE system (pressure dynamics)
- [ ] Integrate with SciPy `solve_ivp`
- [ ] Add failure detection (stop at burst)
- [ ] Unit tests (simple test cases)

### Task 4: System Integrator ✅
**File:** `rocket_sim/system_model/system_integrator.py`
**Effort:** 1 hour
- [ ] Implement `run_full_simulation()`
- [ ] Connect Module 1 → Module 2
- [ ] Handle data passing
- [ ] Integration tests with real combustion data

### Task 5: Comprehensive Testing ✅
**Files:** `rocket_sim/system_model/tests/*.py`
**Effort:** 2 hours
- [ ] Unit tests for each module
- [ ] Integration tests (M1→M2)
- [ ] Physical consistency checks
- [ ] Edge case testing

### Task 6: Documentation ✅
**Effort:** 30 min
- [ ] Docstrings for all functions
- [ ] Usage examples
- [ ] Update README.md
- [ ] Theory documentation (formulas)

---

## Test Plan

### Unit Tests (40+ tests planned)

#### Materials Module
1. Test material property retrieval
2. Test invalid material raises error
3. Test all materials have required properties

#### Burst Calculator
4. Test Barlow's formula accuracy
5. Test hoop stress calculation
6. Test axial stress calculation
7. Test von Mises criterion
8. Test safety factor calculation
9. Verify against literature values
10. Test extreme pressure values
11. Test thin-wall assumption validity

#### ODE Solver
12. Test constant pressure (no combustion)
13. Test linear pressure rise
14. Test with real combustion data
15. Test failure detection
16. Test time stepping accuracy
17. Test mass conservation (if applicable)
18. Test energy conservation approximation

#### System Integrator
19. Test full simulation workflow
20. Test with various mix ratios
21. Test with different vessel sizes
22. Test with different materials
23. Test failure prediction accuracy
24. Test edge cases (very small/large vessels)

### Integration Tests
25. Module 1 → Module 2 data flow
26. End-to-end simulation
27. Parameter sweep consistency

### Validation Tests
28. Compare burst pressure with experiments
29. Compare with published PET bottle data
30. Verify safety factors are realistic

---

## Acceptance Criteria

### Functionality
- [ ] ODE solver produces smooth P(t), T(t) curves
- [ ] Burst calculator matches analytical values (±5%)
- [ ] System detects failure correctly
- [ ] Integration with Module 1 seamless

### Performance
- [ ] Full simulation runs in <10 seconds
- [ ] ODE solver stable (no numerical explosions)

### Quality
- [ ] 100% test pass rate
- [ ] >85% code coverage
- [ ] All functions documented
- [ ] Type hints complete

### Validation
- [ ] Burst pressure for 2L PET bottle: ~800-1200 kPa (literature)
- [ ] Safety factor calculation realistic
- [ ] Failure point prediction reasonable

---

## Deliverables

1. **Code**
   - `materials.py` (~100 LOC)
   - `burst_calculator.py` (~200 LOC)
   - `ode_solver.py` (~300 LOC)
   - `system_integrator.py` (~150 LOC)
   - **Total: ~750 LOC**

2. **Tests**
   - 40+ unit tests
   - 10+ integration tests
   - **Total: ~1000 LOC**

3. **Documentation**
   - Inline docstrings (100%)
   - Theory guide (formulas)
   - Usage examples

4. **Reports**
   - This file (planning)
   - `PHASE-4B-COMPLETE.md` (completion report)

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| ODE solver instability | High | Use implicit solvers, limit max step size |
| Combustion data interpolation errors | Medium | Use scipy interpolation, validate smoothness |
| Thin-wall assumption invalid | Medium | Check t/D ratio, warn if >0.1 |
| Material data inaccuracy | Medium | Use conservative values, cite sources |

---

## Schedule

**Estimated Time:** 6-8 hours total

- **Hour 1:** Materials database + burst calculator
- **Hour 2-3:** ODE solver implementation
- **Hour 4:** System integrator
- **Hour 5-6:** Unit testing
- **Hour 7:** Integration testing
- **Hour 8:** Documentation + wrap-up

**Target Completion:** January 25, 2026 (same day)

---

## References

### Theory
- **Barlow's Formula:** P = 2σt/D (thin-wall pressure vessels)
- **Hoop Stress:** σ_h = PD/(2t)
- **Axial Stress:** σ_a = PD/(4t)
- **Von Mises:** σ_vm = √(σ_h² - σ_h·σ_a + σ_a²)

### Literature
- ASME Boiler & Pressure Vessel Code
- Roark's Formulas for Stress and Strain
- PET bottle burst testing data

### Previous Work
- Module 1: `rocket_sim/combustion/cantera_wrapper.py`
- Phase 4A Report: `PHASE-4A-COMPLETE.md`

---

**Status:** Ready to implement  
**Next Step:** Create materials database  
**Updated:** January 25, 2026
