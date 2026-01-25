# Scripts

Utility scripts for testing and validation.

## Test Runners

### `run_phase5_validation.py`
Comprehensive validation test suite runner.

Executes:
- All unit tests across modules
- Integration & validation tests
- Code coverage analysis
- Performance benchmarks
- Integration examples

Usage:
```bash
python scripts/run_phase5_validation.py
```

### `test_module2.py`
Quick test script for Module 2 (System Model).

Usage:
```bash
python scripts/test_module2.py
```

### `run_module2_tests.py`
Test runner specifically for Module 2 tests.

Usage:
```bash
python scripts/run_module2_tests.py
```

## Running Tests

For regular development, use pytest directly:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rocket_sim --cov-report=html

# Run specific module
pytest rocket_sim/combustion/tests/

# Run validation tests
pytest tests/test_phase5_validation.py -v
```

## Validation Suite

For complete validation (recommended before releases):

```bash
python scripts/run_phase5_validation.py
```

This runs:
- 186+ unit and integration tests
- Code coverage analysis (>90% target)
- Performance benchmarks (<5s target)
- Literature validation
- Physical consistency checks
- Safety validation

Results are saved to `validation_results.json`.
