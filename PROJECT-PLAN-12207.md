# PET Rocket Simulator - ISO/IEC/IEEE 12207:2017 Development Plan

**Project:** PET Bottle H₂/O₂ Rocket Safety Simulation Framework  
**Standard:** ISO/IEC/IEEE 12207:2017 Software Life Cycle Processes  
**Plan Created:** January 25, 2026  
**Status:** Planning Phase

---

## Executive Summary

### Business Mission
Develop a fully open-source, code-driven simulation framework to predict and prevent catastrophic structural failure in experimental PET bottle hydrogen/oxygen rockets through transient pressure, temperature, and stress modeling.

### Critical Success Factors
- **Primary Goal:** Failure prevention and structural safety analysis (NOT propulsion optimization)
- **Safety Priority:** Predict burst conditions before physical testing
- **Key Risk:** PET bottles behave as rapidly exploding pressure vessels (6-12 bar burst, H₂/O₂ can reach 50-100+ bar)
- **Target Users:** Scientists, experimenters, educational/research institutions

### Solution Approach
Four-module coupled simulation system:
1. Thermochemistry (Cantera) - combustion → pressure curves
2. System Dynamics (SciPy ODE) - mass/energy transient modeling
3. Structural FEM (CalculiX) - burst analysis
4. Optional CFD (OpenFOAM) - flow field refinement

---

## ISO 12207:2017 Process Mapping

### Phase 1: Planning & Analysis (§6.4.1)

#### Business/Mission Analysis - COMPLETED
**Status:** ✅ Defined

**Problem Space:**
- **Problem Statement:** Experimental PET bottle H₂/O₂ rockets exhibit unpredictable behavior - sometimes successful launch, sometimes catastrophic rupture/explosion
- **Safety Hazard:** Brittle failure of thin-walled plastic pressure vessel with extremely fast pressure rise (µs-ms timescale)
- **Gap:** No existing open-source toolchain to predict failure conditions before physical testing

**Stakeholder Groups:**
- Primary: Amateur rocket experimenters, educational institutions
- Secondary: Safety regulators, researchers
- Tertiary: Open-source scientific software community

**Trade-Space Factors:**
- **Technical:** Must handle multi-physics (combustion, thermodynamics, structural mechanics)
- **Economic:** Zero-cost constraint (open-source only)
- **Social:** Educational/safety mission
- **Legal:** Liability considerations require conservative safety predictions
- **Environmental:** Minimal computational resources required

**Solution Space Characterization:**

| Solution Class | Feasibility | Selected |
|----------------|-------------|----------|
| Manual calculations | Low (too complex) | ❌ |
| Commercial FEM software | Low (cost barrier) | ❌ |
| Simplified spreadsheet model | Medium (insufficient accuracy) | ❌ |
| Integrated open-source simulation | **High** | ✅ |

**Preferred Solution:** Custom Python-based framework integrating Cantera, SciPy, and CalculiX

---

### Phase 2: Requirements (§6.4.2, §6.4.3)

#### Stakeholder Requirements Definition

**SR-1: Safety Prediction**
- System shall identify unsafe pressure/temperature combinations before physical testing
- Rationale: Prevent injury from catastrophic vessel rupture

**SR-2: Accessibility**
- System shall use only open-source tools (no proprietary licenses)
- Rationale: Enable broad educational/research access

**SR-3: Reproducibility**
- System shall be fully scriptable and automatable
- Rationale: Scientific reproducibility and batch analysis

**SR-4: Usability**
- System shall provide clear safety factor outputs and automated visualization
- Rationale: Support non-expert users in making go/no-go decisions

**SR-5: Performance**
- System shall complete single simulation in < 5 minutes on standard hardware
- Rationale: Enable parameter sweep studies

#### System/Software Requirements Definition

**Functional Requirements:**

| ID | Requirement | Priority | Verification Method |
|----|-------------|----------|---------------------|
| FR-1 | Compute H₂/O₂ combustion P(t), T(t) using validated chemistry | Must Have | Unit test vs. literature data |
| FR-2 | Model transient pressure including filling, ignition, rise time | Must Have | Integration test with known scenarios |
| FR-3 | Calculate structural stress (hoop, von Mises) with temperature-dependent PET properties | Must Have | FEM validation vs. analytical thin-wall theory |
| FR-4 | Compute safety factor against burst | Must Have | Test with known failure cases |
| FR-5 | Export results in CSV/JSON formats | Must Have | Automated parsing test |
| FR-6 | Generate automated plots (P vs t, stress vs t, safety margin) | Should Have | Visual inspection |
| FR-7 | Support parameter sweeps (mixture ratio, volume, wall thickness) | Should Have | Batch execution test |
| FR-8 | Provide CLI interface | Must Have | Integration test |
| FR-9 | Include analytical pre-check (thin-wall σ = Pr/t) | Must Have | Unit test |

**Non-Functional Requirements:**

| ID | Requirement | Specification | Verification |
|----|-------------|---------------|--------------|
| NFR-1 | Platform | Python 3.11+ | Version check in CI |
| NFR-2 | Dependencies | NumPy, SciPy, Matplotlib, Cantera, CalculiX only (OpenFOAM optional) | Dependency audit |
| NFR-3 | Execution Mode | Fully CLI-driven, no GUI required | Automated testing |
| NFR-4 | Reproducibility | Identical inputs → identical outputs | Regression test suite |
| NFR-5 | Performance | < 5 min per simulation on 4-core CPU | Benchmark suite |
| NFR-6 | Maintainability | Modular architecture, <20% code duplication | Static analysis |
| NFR-7 | Portability | Linux, macOS, Windows support | Multi-platform CI |
| NFR-8 | Documentation | Inline docstrings, README, example notebooks | Coverage check |

**Constraints:**
- No proprietary software dependencies
- PET material model: E=2.5 GPa, ν=0.38, σ_yield≈55 MPa, temperature-dependent modulus
- Pressure vessel geometry: thin-walled cylinder + dome, threaded neck weakness

**Acceptance Criteria:**
- ✅ Correctly predicts known safe configuration (low pressure)
- ✅ Correctly predicts known failure configuration (high pressure)
- ✅ Safety factor accuracy within ±15% of analytical calculation
- ✅ All modules pass unit and integration tests
- ✅ Complete documentation with worked examples

---

### Phase 3: Architecture & Design (§6.4.4, §6.4.5, §6.4.6)

#### Architecture Definition

**Architectural Pattern:** Layered Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Orchestration Layer (main.py)                   │
│  - Parameter management                                 │
│  - Execution sequencing                                 │
│  - Results aggregation                                  │
├─────────────────────────────────────────────────────────┤
│  Module 1: Thermochemistry     │  Module 2: System     │
│  (combustion/)                  │  Dynamics             │
│  - Cantera interface            │  (system_model/)      │
│  - H₂/O₂ kinetics               │  - ODE solver         │
│  - P(t), T(t) output            │  - Mass/energy balance│
├─────────────────────────────────┼───────────────────────┤
│  Module 3: Structural FEM       │  Module 4: CFD        │
│  (fem/)                         │  (Optional)           │
│  - CalculiX wrapper             │  - OpenFOAM wrapper   │
│  - Geometry generation          │  - Refinement only    │
│  - Stress analysis              │                       │
├─────────────────────────────────────────────────────────┤
│         Utilities Layer (utils/)                        │
│  - Plotting, I/O, validation, material models           │
└─────────────────────────────────────────────────────────┘
```

**Data Flow:**
```
Input Parameters → Combustion Module → P(t), T(t) →
System Dynamics → Refined P(t) → Analytical Check →
FEM Module → Stress(t) → Safety Analysis → Report + Plots
```

**Module Interfaces:**

**Module 1 API:**
```python
def simulate_combustion(volume: float, mix_ratio: float, 
                       T0: float, P0: float) -> dict:
    """
    Returns: {
        "time": np.ndarray,
        "pressure": np.ndarray, 
        "temperature": np.ndarray,
        "peak_pressure": float,
        "max_dPdt": float
    }
    """
```

**Module 2 API:**
```python
def run_system_model(params: dict) -> dict:
    """
    params: {
        "bottle_volume": float,
        "valve_area": float,
        "ignition_time": float,
        ...
    }
    Returns: {
        "time": np.ndarray,
        "chamber_pressure": np.ndarray,
        "thrust_estimate": np.ndarray,
        "loads_for_fem": dict
    }
    """
```

**Module 3 API:**
```python
def run_fem(pressure_curve: np.ndarray, geometry: dict, 
           material: dict) -> dict:
    """
    Returns: {
        "max_stress": float,
        "safety_factor": float,
        "predicted_rupture": bool,
        "stress_time_series": np.ndarray
    }
    """
```

**Design Decisions:**

| Decision | Option Chosen | Rationale |
|----------|---------------|-----------|
| Language | Python | Ecosystem support, ease of integration |
| Combustion solver | Cantera | Validated H₂/O₂ kinetics, open-source |
| FEM tool | CalculiX | Simpler than Code_Aster, sufficient for thin-wall analysis |
| ODE solver | SciPy solve_ivp | Robust, well-documented |
| Data format | JSON/CSV | Human-readable, tool-agnostic |
| Execution model | Sequential pipeline | Matches physics causality, simplifies debugging |

#### Design Definition

**Directory Structure:**
```
rocket_sim/
├── combustion/
│   ├── __init__.py
│   ├── cantera_wrapper.py
│   └── tests/
├── system_model/
│   ├── __init__.py
│   ├── ode_model.py
│   ├── analytical_checks.py
│   └── tests/
├── fem/
│   ├── __init__.py
│   ├── calculix_wrapper.py
│   ├── geometry_gen.py
│   └── tests/
├── utils/
│   ├── __init__.py
│   ├── plotting.py
│   ├── io_utils.py
│   └── material_models.py
├── configs/
│   ├── default_config.json
│   ├── safe_example.json
│   └── unsafe_example.json
├── notebooks/
│   └── tutorial.ipynb
├── main.py
├── requirements.txt
├── README.md
└── tests/
    └── integration/
```

**Key Algorithms:**

1. **Thin-Wall Analytical Check:**
   - Hoop stress: σ = P·r/t
   - Burst pressure: P_burst = σ_fail·t/r
   - Quick rejection before expensive FEM

2. **Temperature-Dependent Modulus:**
   - E(T) = E₀ · (1 - α·(T - T₀)) for T < T_soften
   - E(T) = E₀ · 0.1 for T > T_soften (softening model)

3. **Pressure Rise Model:**
   - Cantera: constant-volume explosion
   - System ODE: valve flow + chamber filling
   - Coupling: use Cantera P_max as boundary condition

#### System Analysis

**Failure Mode Analysis:**

| Failure Mode | Probability | Mitigation |
|--------------|-------------|------------|
| Cantera installation failure | Medium | Docker container option |
| CalculiX mesh convergence issues | Medium | Adaptive meshing, validation vs. analytical |
| Numerical instability in ODE | Low | Stiff solver selection |
| Incorrect material properties | High | Literature validation, conservative assumptions |
| User input errors | High | Input validation, unit checking |

**Performance Analysis:**
- Cantera combustion: ~1-5 seconds
- System ODE: <1 second
- CalculiX FEM: ~30-120 seconds (mesh-dependent)
- Total: 2-5 minutes target achieved

**Traceability:**
- Each module maps to specific FRs
- Test cases trace to SRs
- Safety requirements trace through to safety factor calculation

---

### Phase 4: Implementation (§6.4.7, §6.4.8)

#### Implementation Strategy

**Development Approach:** Iterative, bottom-up integration

**Phase 4A: Foundation (Week 1-2)**
- Set up project repository structure
- Configure Python environment, dependencies
- Implement Module 1 (Cantera combustion wrapper)
- Unit tests for thermochemistry
- Deliverable: Working combustion simulator with validated H₂/O₂ data

**Phase 4B: System Modeling (Week 2-3)**
- Implement Module 2 (ODE-based system dynamics)
- Analytical burst calculator (thin-wall theory)
- Integration tests (combustion → system model)
- Deliverable: Complete pressure profile generator

**Phase 4C: Structural Analysis (Week 3-4)**
- Implement Module 3 (CalculiX wrapper)
- Geometry generation for PET bottle (cylinder + dome + neck)
- Temperature-dependent material model
- Deliverable: FEM automation with stress output

**Phase 4D: Integration (Week 4-5)**
- Main pipeline orchestration script
- Parameter sweep framework
- End-to-end validation with known safe/unsafe cases
- Deliverable: Complete simulation pipeline

**Phase 4E: Reporting & Documentation (Week 5-6)**
- Automated plotting (Matplotlib)
- CSV/JSON export functions
- README, installation guide
- Jupyter notebook tutorials
- Deliverable: Production-ready package

#### Integration Process

**Integration Sequence:**
1. Unit test Module 1 (Cantera) independently
2. Unit test Module 2 (ODE) independently
3. Integrate M1→M2, validate pressure curves
4. Add analytical thin-wall check as validation layer
5. Unit test Module 3 (FEM) with static pressure
6. Integrate M2→M3 with transient pressure
7. Full pipeline testing

**Integration Test Cases:**

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| IT-1 | Low pressure (2 bar), room temp | Safety factor > 3.0, no rupture |
| IT-2 | High pressure (10 bar), high temp | Safety factor < 1.0, rupture predicted |
| IT-3 | Edge case (6 bar) | Safety factor ≈ 1.0-1.5 |
| IT-4 | Thin wall (0.1mm) vs. thick wall (0.5mm) | SF scales proportionally |
| IT-5 | Parameter sweep (50 configs) | All complete without crash |

**Version Control Strategy:**
- Git with semantic versioning (0.1.0 → 1.0.0)
- Feature branches for each module
- CI/CD with automated testing on push

---

### Phase 5: Verification & Validation (§6.4.9, §6.4.11)

#### Verification Process

**Verification Methods:**

| Requirement | Verification Method | Pass Criteria |
|-------------|---------------------|---------------|
| FR-1 (Combustion) | Unit test vs. literature | P_max within 5% of published H₂/O₂ data |
| FR-2 (System model) | ODE solver validation | Mass/energy conservation errors < 0.1% |
| FR-3 (Stress calc) | FEM vs. analytical | Hoop stress within 10% of thin-wall formula |
| FR-4 (Safety factor) | Known failure cases | Correctly identifies burst in test cases |
| FR-5 (Export) | Automated parsing | Valid JSON/CSV structure |
| FR-6 (Plots) | Visual inspection | Axes labeled, units correct |
| FR-7 (Sweeps) | Batch execution | 100% completion rate |
| FR-8 (CLI) | Command-line test | Help text, error handling |
| NFR-5 (Performance) | Benchmark suite | 95th percentile < 5 min |

**Code Quality Checks:**
- Pylint/Flake8: Score > 8.0/10
- Test coverage: > 80%
- Documentation coverage: 100% of public APIs

**Peer Review:**
- Architecture review before Phase 4A
- Code review for each module
- Integration review before Phase 5

#### Validation Process

**Validation Against Stakeholder Needs:**

| Stakeholder Need | Validation Method | Success Criteria |
|------------------|-------------------|------------------|
| SR-1 (Safety prediction) | Compare with actual burst tests (if available) OR literature case studies | Correct classification of safe/unsafe |
| SR-2 (Accessibility) | Dependency audit | Zero proprietary dependencies |
| SR-3 (Reproducibility) | Repeat test runs | Identical outputs |
| SR-4 (Usability) | User acceptance testing | Non-expert can run tutorial in < 30 min |
| SR-5 (Performance) | Profiling | Meets timing requirements |

**Validation Test Plan:**

1. **Literature Validation:**
   - Find published PET bottle burst pressure data
   - Simulate those exact conditions
   - Compare predicted vs. actual burst pressure

2. **Physical Validation (if safe to conduct):**
   - Low-pressure water tests with pressure gauge
   - Compare measured P(t) vs. predicted P(t)
   - (NO combustion testing for safety reasons)

3. **Expert Review:**
   - Pressure vessel engineer reviews stress calculations
   - Combustion expert reviews Cantera setup
   - Software engineer reviews code quality

**Acceptance Testing:**
- Run all example configurations
- Verify plots are interpretable
- Confirm CSV exports load into Excel/Python
- Documentation walkthrough with test user

---

### Phase 6: Deployment & Operations (§6.4.10, §6.4.12)

#### Transition Process

**Deployment Strategy:**
- Package as Python module: `pip install rocket-sim`
- Docker container for dependencies (especially CalculiX)
- GitHub repository with releases

**Deliverables:**

| Artifact | Description | Format |
|----------|-------------|--------|
| Source code | Complete implementation | Git repository |
| Installation guide | Step-by-step setup | README.md |
| User manual | CLI usage, parameters | Markdown + docstrings |
| Tutorial | Worked examples | Jupyter notebook |
| Example configs | Safe/unsafe scenarios | JSON files |
| Test suite | All verification tests | pytest |
| API documentation | Auto-generated | Sphinx HTML |

**Installation Instructions:**
```bash
# Option 1: pip install
pip install rocket-sim

# Option 2: Docker
docker pull rocket-sim:latest
docker run -v $(pwd)/results:/results rocket-sim --config myconfig.json

# Option 3: From source
git clone https://github.com/user/rocket-sim.git
cd rocket-sim
pip install -r requirements.txt
python main.py --help
```

**Training Materials:**
- Quick start guide (5 min)
- Tutorial notebook (30 min)
- Parameter reference guide
- Troubleshooting FAQ

#### Operation Process

**Usage Workflow:**
1. User creates configuration JSON
2. Runs: `python main.py --config myconfig.json`
3. System generates results in `./results/`
4. User reviews plots and safety factor
5. Iterates parameter sweep if needed

**Operational Constraints:**
- Requires 4GB RAM minimum
- CalculiX must be in system PATH
- Python 3.11+ required

**Monitoring & Logging:**
- Progress logging to console
- Error logs to `./logs/error.log`
- Performance metrics logged for each module

**Support Plan:**
- GitHub Issues for bug reports
- Discussion forum for usage questions
- Quarterly dependency updates

---

### Phase 7: Maintenance & Disposal (§6.4.13, §6.4.14)

#### Maintenance Process

**Maintenance Categories:**

1. **Corrective Maintenance:**
   - Bug fixes based on user reports
   - Patch releases within 2 weeks of critical bugs

2. **Adaptive Maintenance:**
   - Updates for new Python versions
   - Dependency compatibility updates
   - OS compatibility fixes

3. **Perfective Maintenance:**
   - Performance optimizations
   - Additional material models
   - Enhanced visualization

4. **Preventive Maintenance:**
   - Security vulnerability scanning
   - Dependency audits (quarterly)
   - Code refactoring to reduce technical debt

**Version Control:**
- Semantic versioning: MAJOR.MINOR.PATCH
- LTS branch for stable releases
- Development branch for new features

**Update Schedule:**
- Bug fixes: As needed
- Minor updates: Quarterly
- Major updates: Annually

**Known Limitations (to document):**
- PET material model is simplified (no creep, no fatigue)
- Assumes axisymmetric geometry
- CFD module not included in v1.0
- No GUI (CLI only)

**Enhancement Roadmap:**
- v1.1: Add CFD integration
- v1.2: GUI wrapper
- v2.0: Multi-material support (aluminum, composites)
- v2.1: Time-dependent fatigue analysis

#### Disposal Process

**End-of-Life Criteria:**
- Superseded by superior open-source tool
- Dependencies become unmaintainable
- User base drops to zero

**Disposal Actions:**
- Archive repository (read-only)
- Update README with deprecation notice
- Recommend alternative tools
- Preserve documentation for historical reference

**Data Retention:**
- Source code archived indefinitely (GitHub)
- Release binaries retained for 5 years
- Documentation preserved in Internet Archive

---

## Cross-Process Elements

### Traceability Matrix

| Stakeholder Req | System Req | Design Element | Implementation | Test Case |
|-----------------|------------|----------------|----------------|-----------|
| SR-1 (Safety) | FR-3, FR-4 | Module 3 FEM, analytical check | `fem/calculix_wrapper.py` | IT-2, VT-FR4 |
| SR-2 (Open-source) | NFR-2 | Cantera, CalculiX, SciPy | `requirements.txt` | Dependency audit |
| SR-3 (Reproducible) | NFR-4 | Deterministic algorithms | All modules | Regression tests |
| SR-4 (Usable) | FR-6, FR-8 | Plotting, CLI | `main.py`, `utils/plotting.py` | UAT |
| SR-5 (Performance) | NFR-5 | Lightweight ODE, coarse FEM mesh | Solver configs | Benchmark suite |

### Quality Gates

| Gate | Phase Exit Criteria | Review Required |
|------|---------------------|-----------------|
| Gate 1 | Requirements approved, traceability matrix complete | Architecture review |
| Gate 2 | Architecture review passed, design docs complete | Technical review |
| Gate 3 | All unit tests pass, code coverage > 80% | Code review |
| Gate 4 | Integration tests pass, performance benchmarks met | Integration review |
| Gate 5 | Validation complete, user acceptance passed | Release approval |

### Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cantera installation difficulties | High | High | Provide Docker container |
| CalculiX learning curve | Medium | Medium | Pre-built mesh templates, examples |
| Inaccurate material properties | Medium | High | Conservative safety factors, validation |
| User misinterpretation of results | High | Critical | Clear warning labels, documentation |
| Performance on low-end hardware | Medium | Low | Provide cloud execution option |

### Configuration Management

**Baseline Items:**
- Source code (Git tags)
- Requirements document (this file)
- Test suite
- Dependencies (requirements.txt pinned versions)

**Change Control:**
- Minor changes: Developer approval
- Major changes: Architecture review board
- Breaking changes: User notification, deprecation period

**Release Process:**
1. Version bump in `setup.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create Git tag
5. Build and upload to PyPI
6. Announce on GitHub/mailing list

---

## Project Schedule

**Timeline:** 6 weeks (assuming 20 hrs/week effort)

| Week | Phase | Deliverables | Milestone |
|------|-------|--------------|-----------|
| 1-2 | Implementation Phase 4A | Module 1 complete, unit tests | ✓ Combustion working |
| 2-3 | Implementation Phase 4B | Module 2 complete, integration tests | ✓ System model working |
| 3-4 | Implementation Phase 4C | Module 3 complete, FEM tests | ✓ FEM working |
| 4-5 | Implementation Phase 4D | Full pipeline, parameter sweeps | ✓ Integration complete |
| 5-6 | Implementation Phase 4E, Verification | Documentation, validation | ✓ Release ready |
| 6+ | Deployment, Maintenance | Published package, user support | ✓ v1.0 released |

**Critical Path:**
Cantera wrapper → System ODE → FEM wrapper → Integration

**Dependencies:**
- CalculiX installation (external)
- Access to H₂/O₂ combustion literature (for validation)
- Test hardware (for performance benchmarks)

---

## Success Metrics

**Technical Metrics:**
- ✅ All functional requirements implemented
- ✅ Test coverage > 80%
- ✅ Performance < 5 min per simulation
- ✅ Zero proprietary dependencies

**User Metrics:**
- ✅ 10+ successful user installations
- ✅ < 5 critical bugs reported in first 3 months
- ✅ Tutorial completion rate > 80%

**Safety Metrics:**
- ✅ Conservative safety factors (no false negatives)
- ✅ Validation against literature within 15%

**Project Metrics:**
- ✅ Delivered on schedule (6 weeks)
- ✅ Documentation complete
- ✅ Maintainable codebase (low complexity)

---

## Compliance Statement

This project plan complies with ISO/IEC/IEEE 12207:2017 by addressing:

- ✅ **§6.4.1** Business or Mission Analysis Process
- ✅ **§6.4.2** Stakeholder Needs and Requirements Definition Process
- ✅ **§6.4.3** System/Software Requirements Definition Process
- ✅ **§6.4.4** Architecture Definition Process
- ✅ **§6.4.5** Design Definition Process
- ✅ **§6.4.6** System Analysis Process
- ✅ **§6.4.7** Implementation Process
- ✅ **§6.4.8** Integration Process
- ✅ **§6.4.9** Verification Process
- ✅ **§6.4.11** Validation Process
- ✅ **§6.4.10** Transition Process
- ✅ **§6.4.12** Operation Process
- ✅ **§6.4.13** Maintenance Process
- ✅ **§6.4.14** Disposal Process

All technical processes have defined outcomes, activities, and tasks as required by the standard.

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-25 | AI Development Team | Initial plan created from specification |

**Approvals:**
- [ ] Technical Lead
- [ ] Quality Assurance
- [ ] Project Sponsor

**Next Review Date:** Start of Phase 4 (Implementation)

---

**End of Project Plan**
