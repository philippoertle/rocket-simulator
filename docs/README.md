# Documentation

This directory contains all documentation for the PET Rocket Simulator.

## Structure

### `/development/`
Development process documentation following ISO/IEC/IEEE 12207:2017:

**Project Planning & Progress:**
- `PROJECT-PLAN-12207.md` - Complete development plan
- `PROJECT-PROGRESS.md` - Progress tracking throughout development
- `PROJECT-COMPLETE.md` - Final project completion summary

**Phase Reports:**
Each phase has planning (REPORT) and completion (COMPLETE) documents:
- Phase 4A: Foundation (Module 1 - Combustion)
- Phase 4B: System Modeling (Module 2)
- Phase 4C: FEM Analysis (Module 3)
- Phase 4D: Integration & Optimization
- Phase 5: Verification & Validation
- Phase 6: Deployment

**Summary Documents:**
- `IMPLEMENTATION-COMPLETE.md` - Phase 4 (all implementation) summary
- `VERIFICATION-COMPLETE.md` - Phase 5 summary

## User Documentation

User-facing documentation is in the repository root:
- `README.md` - Project overview
- `INSTALL.md` - Installation guide
- `QUICKSTART.md` - Quick start tutorial
- `CONTRIBUTING.md` - How to contribute
- `CHANGELOG.md` - Version history
- `RELEASE-NOTES-v0.1.0.md` - Release announcement

## API Documentation

All modules have comprehensive inline documentation:
- 100% docstring coverage
- Type hints throughout
- Examples in all public functions
- Theory references where applicable

To access API docs programmatically:
```python
import rocket_sim
help(rocket_sim)
```

## Development Process

The development followed ISO/IEC/IEEE 12207:2017 standard with these phases:
1. Planning & Analysis
2. Requirements Definition
3. Architecture & Design
4. Implementation (4A-4D)
5. Verification & Validation
6. Deployment

See `/development/` for detailed phase documentation.
