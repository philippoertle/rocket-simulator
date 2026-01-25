# Repository Structure

This document describes the organization of the PET Rocket Simulator repository.

## Overview

The repository is organized to separate:
- **User-facing files** (root) - Essential documentation and configuration
- **Development documentation** (`docs/development/`) - Process documentation
- **Utility scripts** (`scripts/`) - Test runners and utilities
- **Source code** (`rocket_sim/`) - Python package
- **Tests** (`tests/`) - Integration and validation tests
- **Historical artifacts** (`archive/`) - Original specs and references

---

## Root Directory

### Essential User Files
- **README.md** - Project overview, quick start, architecture
- **LICENSE** - MIT License with safety disclaimer
- **INSTALL.md** - Installation instructions
- **QUICKSTART.md** - 5-minute tutorial
- **CONTRIBUTING.md** - Contribution guidelines
- **CHANGELOG.md** - Version history
- **RELEASE-NOTES-v0.1.0.md** - Release announcement

### Configuration Files
- **setup.py** - Package configuration for pip
- **requirements.txt** - Python dependencies
- **MANIFEST.in** - Files to include in package distribution
- **pytest.ini** - Pytest configuration
- **.gitignore** - Git ignore patterns

---

## `/rocket_sim/` - Source Code

Main Python package with all simulation modules:

```
rocket_sim/
├── __init__.py                  # Package initialization
├── combustion/                  # Module 1: Combustion
│   ├── __init__.py
│   ├── cantera_wrapper.py      # Cantera integration
│   └── tests/                  # Unit tests
├── system_model/                # Module 2: System Dynamics
│   ├── __init__.py
│   ├── materials.py            # Materials database
│   ├── burst_calculator.py     # Burst pressure calculations
│   ├── ode_solver.py           # ODE integration
│   ├── system_integrator.py    # System integration
│   └── tests/                  # Unit tests
├── fem/                         # Module 3: FEM Analysis
│   ├── __init__.py
│   ├── geometry.py             # Mesh generation
│   ├── thick_wall_solver.py    # Lamé equations
│   ├── stress_concentrations.py # Stress factors
│   └── tests/                  # Unit tests
├── integration/                 # Full System Integration
│   ├── __init__.py
│   └── full_simulation.py      # M1→M2→M3 orchestrator
└── visualization/               # Visualization
    ├── __init__.py
    └── plots.py                # Matplotlib plots
```

**Total:** ~4,200 lines of production code

---

## `/tests/` - Integration Tests

System-level and validation tests:

```
tests/
└── test_phase5_validation.py   # Comprehensive validation suite
```

These tests validate:
- Literature comparisons
- Physical consistency
- End-to-end integration
- Performance benchmarks
- Safety validation

---

## `/docs/` - Documentation

### `/docs/README.md`
Documentation guide and overview.

### `/docs/development/` - Development Process

Complete ISO/IEC/IEEE 12207:2017 compliant development documentation:

**Project Planning:**
- `PROJECT-PLAN-12207.md` - Complete development plan with requirements
- `PROJECT-PROGRESS.md` - Progress tracking throughout development
- `PROJECT-COMPLETE.md` - Final completion summary

**Phase Reports (Implementation - Phase 4):**
- `PHASE-4A-REPORT.md` / `PHASE-4A-COMPLETE.md` - Module 1 (Combustion)
- `PHASE-4B-REPORT.md` / `PHASE-4B-COMPLETE.md` - Module 2 (System Model)
- `PHASE-4B-SUMMARY.md` - Quick summary
- `PHASE-4C-REPORT.md` / `PHASE-4C-COMPLETE.md` - Module 3 (FEM)
- `PHASE-4C-SUMMARY.md` - Quick summary
- `PHASE-4D-REPORT.md` / `PHASE-4D-COMPLETE.md` - Integration

**Phase Reports (V&V - Phase 5):**
- `PHASE-5-REPORT.md` / `PHASE-5-COMPLETE.md` - Verification & Validation

**Phase Reports (Deployment - Phase 6):**
- `PHASE-6-REPORT.md` / `PHASE-6-COMPLETE.md` - Deployment

**Summary Documents:**
- `IMPLEMENTATION-COMPLETE.md` - All implementation phases summary
- `VERIFICATION-COMPLETE.md` - Verification & validation summary

**Total:** 19 detailed development documents

---

## `/scripts/` - Utility Scripts

Test runners and utility scripts:

```
scripts/
├── README.md                    # Scripts documentation
├── run_phase5_validation.py     # Comprehensive validation suite
├── run_module2_tests.py         # Module 2 test runner
└── test_module2.py              # Module 2 quick test
```

**Usage:**
```bash
# Run full validation suite
python scripts/run_phase5_validation.py

# Run module-specific tests
python scripts/test_module2.py
```

---

## `/archive/` - Historical Artifacts

Original specifications and historical references:

```
archive/
├── README.md                    # Archive documentation
└── pet_rocket_ai_spec.md        # Original AI-assisted specification
```

These files are preserved for historical reference but are superseded by:
- Current requirements in `docs/development/PROJECT-PLAN-12207.md`
- Implementation in source code
- User documentation in root directory

---

## Development Artifacts (Not Committed)

Generated files (ignored by git):

```
.pytest_cache/                   # Pytest cache
htmlcov/                         # Coverage reports
.coverage                        # Coverage data
*.egg-info/                      # Package metadata
__pycache__/                     # Python bytecode
validation_results.json          # Validation results
```

---

## File Count Summary

| Category | Count | Lines |
|----------|-------|-------|
| Source modules | 11 | ~4,200 |
| Test files | 10+ | ~4,700 |
| User documentation | 7 | ~2,500 |
| Development docs | 19 | ~15,000 |
| Scripts | 3 | ~800 |
| **Total** | **50+** | **~27,200** |

---

## Navigation Guide

### For Users
Start here:
1. `README.md` - Understand what it does
2. `INSTALL.md` - Install the package
3. `QUICKSTART.md` - Run your first simulation

### For Contributors
Start here:
1. `CONTRIBUTING.md` - Contribution guidelines
2. `docs/development/PROJECT-PLAN-12207.md` - Understand requirements
3. Source code with inline documentation

### For Researchers/Validators
Start here:
1. `docs/development/PHASE-5-COMPLETE.md` - Validation results
2. `scripts/run_phase5_validation.py` - Run validation
3. Literature comparisons in validation tests

### For Project Managers
Start here:
1. `docs/development/PROJECT-COMPLETE.md` - Final summary
2. `docs/development/PROJECT-PROGRESS.md` - Development timeline
3. Phase completion reports in `docs/development/`

---

## Rationale for Organization

### Why This Structure?

**Root directory clarity:**
- Only essential user-facing files
- Easy to find documentation
- Professional appearance

**Separate docs/development/:**
- Preserves development history
- Doesn't clutter user view
- Complete process documentation

**Dedicated scripts/:**
- Clear utility location
- Easy to find test runners
- Separated from source code

**Archive for history:**
- Preserves original artifacts
- Clear they're superseded
- Available for reference

This organization balances:
- ✅ User experience (clean root)
- ✅ Developer needs (clear structure)
- ✅ Process compliance (documented)
- ✅ Maintainability (logical grouping)

---

**Last Updated:** January 25, 2026  
**Repository Version:** v0.1.0
