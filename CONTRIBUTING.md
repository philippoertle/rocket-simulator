# Contributing Guidelines

Thank you for your interest in contributing to the PET Rocket Simulator!

This document provides guidelines for contributing to the project.

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Safety First

This project deals with simulation of dangerous devices. All contributions must:
- Emphasize educational and safety analysis purposes
- Include appropriate warnings
- Never encourage actual construction of dangerous devices

---

## How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
1. Check existing issues to avoid duplicates
2. Verify it's actually a bug (not expected behavior)
3. Test with the latest version

**Bug report should include:**
- Python version
- Operating system
- Minimal code to reproduce
- Expected vs actual behavior
- Error messages/stack traces

### Suggesting Features

Feature requests are welcome! Please:
- Check if it aligns with project goals (education/safety)
- Explain the use case
- Consider backwards compatibility
- Be open to discussion

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes** (see guidelines below)
4. **Test thoroughly** (see testing section)
5. **Commit with clear messages**: `git commit -m "Add feature X"`
6. **Push to your fork**: `git push origin feature/my-feature`
7. **Open a pull request**

---

## Development Setup

### Environment Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/rocket-simulator.git
cd rocket-simulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Development Dependencies

```bash
pip install pytest pytest-cov black flake8 mypy pylint
```

---

## Coding Standards

### Style Guide

We follow **PEP 8** with some specifics:

**Formatting:**
- Use `black` for automatic formatting: `black rocket_sim/`
- Line length: 100 characters max
- Indentation: 4 spaces (no tabs)

**Naming:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

**Imports:**
```python
# Standard library
import sys
import time

# Third-party
import numpy as np
from scipy.integrate import solve_ivp

# Local
from rocket_sim.system_model import get_material
```

### Type Hints

All public functions must have type hints:

```python
def calculate_stress(
    pressure: float,
    geometry: VesselGeometry,
    material: MaterialProperties
) -> float:
    """Calculate stress with type hints."""
    pass
```

### Documentation

Every public function/class needs a docstring:

```python
def my_function(param: float) -> float:
    """
    Brief description of function.
    
    Longer description if needed. Explain what it does,
    not how it does it.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param is negative
    
    Example:
        >>> result = my_function(5.0)
        >>> print(result)
        10.0
    """
    if param < 0:
        raise ValueError("param must be non-negative")
    return param * 2
```

---

## Testing Requirements

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rocket_sim --cov-report=html

# Run specific module
pytest rocket_sim/combustion/tests/

# Run validation suite
python run_phase5_validation.py
```

### Writing Tests

**Every new feature needs tests:**

```python
def test_my_feature():
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result > 0
    assert isinstance(result, float)
```

**Test organization:**
- Unit tests in same directory: `rocket_sim/module/tests/`
- Test file naming: `test_*.py`
- Test function naming: `test_*`

**Coverage requirements:**
- New code: >90% coverage
- Critical paths: 100% coverage
- Overall project: maintain >90%

---

## Code Review Process

### Before Submitting PR

**Checklist:**
- [ ] Code follows style guide (run `black`)
- [ ] All tests pass (run `pytest`)
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Type hints added
- [ ] No linting errors (run `flake8`)
- [ ] Commit messages are clear

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (usually within 1 week)
3. **Discussion** if changes needed
4. **Approval and merge** when ready

### What Reviewers Look For

- Correctness and accuracy
- Test coverage
- Code clarity
- Documentation quality
- Performance impact
- Safety considerations

---

## Specific Contribution Areas

### Adding New Materials

To add a material to the database:

```python
# In rocket_sim/system_model/materials.py

MATERIALS["MyMaterial"] = MaterialProperties(
    name="MyMaterial",
    yield_strength=50e6,      # Pa
    tensile_strength=65e6,    # Pa
    elastic_modulus=3.0e9,    # Pa
    poisson_ratio=0.35,
    density=1400.0,           # kg/m³
    max_temp=350.0,           # K
    source="Reference here"
)
```

Include source/reference for material properties!

### Adding Stress Concentration Factors

Add to `rocket_sim/fem/stress_concentrations.py`:

```python
def calculate_new_feature_stress_factor(
    geometry: VesselGeometry,
    ...
) -> float:
    """
    Calculate stress concentration for new feature.
    
    Reference: Peterson's Stress Concentration Factors, Fig X.XX
    """
    # Implementation with literature reference
    pass
```

### Adding Visualization Types

Add to `rocket_sim/visualization/plots.py`:

```python
def plot_new_visualization(
    result: FullSimulationResult,
    save_path: Optional[str] = None,
    show: bool = True
) -> Figure:
    """Create new visualization type."""
    # Implementation
    pass
```

---

## Documentation

### Building Docs

```bash
cd docs
make html
```

### Documentation Structure

- **README.md**: Project overview
- **INSTALL.md**: Installation guide
- **QUICKSTART.md**: Quick start tutorial
- **docs/**: Full API documentation
- **examples/**: Usage examples

---

## Performance Guidelines

### Optimization

- Profile before optimizing: `python -m cProfile`
- Target: <5 seconds for single simulation
- Avoid premature optimization
- Document performance-critical sections

### Benchmarking

```python
import time

def benchmark_function():
    start = time.time()
    # Your code
    elapsed = time.time() - start
    assert elapsed < 5.0, f"Too slow: {elapsed}s"
```

---

## Git Workflow

### Branch Naming

- Features: `feature/description`
- Bugs: `fix/description`
- Documentation: `docs/description`
- Tests: `test/description`

### Commit Messages

```
Short summary (50 chars or less)

Longer explanation if needed. Explain WHAT and WHY,
not HOW. Reference issues:

Fixes #123
Related to #456
```

### Keeping Fork Updated

```bash
# Add upstream remote
git remote add upstream https://github.com/original/rocket-simulator.git

# Fetch and merge
git fetch upstream
git merge upstream/main
```

---

## Release Process

(For maintainers)

1. Update version in `rocket_sim/__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create git tag: `git tag v0.x.0`
5. Push tag: `git push --tags`
6. Build package: `python setup.py sdist bdist_wheel`
7. Upload to PyPI: `twine upload dist/*`

---

## Questions?

- **Technical questions:** Open a GitHub issue
- **Security issues:** Email maintainers directly
- **General discussion:** GitHub Discussions

---

## Recognition

Contributors will be recognized in:
- `CHANGELOG.md`
- GitHub contributors page
- Future release notes

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to safer rocket education!**

---

Last updated: January 25, 2026
