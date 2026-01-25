# Installation Guide

**PET Rocket Simulator v0.1.0**

---

## Prerequisites

### Required Software

- **Python 3.11 or higher** (tested with Python 3.13)
- **pip** (Python package installer)
- **Git** (for development installation)

### Operating Systems

Tested and supported:
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, Fedora)

---

## Quick Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install rocket-simulator
```

### Option 2: Install from Source

```bash
# Clone repository
git clone https://github.com/yourusername/rocket-simulator.git
cd rocket-simulator

# Install in development mode
pip install -e .
```

---

## Detailed Installation Steps

### Step 1: Verify Python Version

```bash
python --version
```

Expected output: `Python 3.11.x` or higher

If you don't have Python 3.11+:
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** `brew install python@3.11`
- **Linux:** `sudo apt install python3.11` (Ubuntu/Debian)

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv rocket-sim-env

# Activate it
# Windows:
rocket-sim-env\Scripts\activate

# macOS/Linux:
source rocket-sim-env/bin/activate
```

### Step 3: Install Package

```bash
pip install rocket-simulator
```

This will automatically install all dependencies:
- numpy ≥1.24.0
- scipy ≥1.10.0
- matplotlib ≥3.7.0
- cantera ≥3.0.0
- pyyaml ≥6.0

### Optional: Install GUI Support

If you want to use the graphical user interface:

```bash
# Install with GUI support
pip install rocket-simulator[gui]

# Or if installing from source
pip install -e ".[gui]"
```

This will install additional dependencies:
- PySide6 ≥6.6.0 (Qt6 bindings for Python)

**Note:** The GUI is optional. You can use the Python API without installing GUI dependencies.

### Step 4: Verify Installation

```python
# Test import
python -c "from rocket_sim import __version__; print(__version__)"
```

Expected output: `0.1.0`

### Step 5: Test GUI (Optional)

If you installed GUI support:

```bash
# Launch GUI
python -m rocket_sim.gui

# Or use entry point
rocket-sim-gui
```

The GUI window should open. If you see errors about missing PySide6, install GUI support (see Step 3 Optional).

### Step 6: Run Quick Test

```python
from rocket_sim.integration.full_simulation import (
    FullSimulationConfig, run_complete_simulation
)

config = FullSimulationConfig(
    volume=0.002,
    fuel_oxidizer_ratio=2.0,
    combustion_time=0.001
)

result = run_complete_simulation(config, verbose=False)
print(f"Peak pressure: {result.summary['peak_pressure']/1e5:.2f} bar")
print(f"Status: {'FAILED' if result.failed else 'SAFE'}")
```

---

## Troubleshooting

### Cantera Installation Issues

Cantera can be tricky to install. If you encounter issues:

**Windows:**
```bash
# Install via conda (easier)
conda install -c conda-forge cantera
```

**macOS:**
```bash
brew install cantera
pip install cantera
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install cantera-python3

# Or via conda
conda install -c conda-forge cantera
```

See [Cantera installation guide](https://cantera.org/install/index.html) for details.

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Verify installation
pip list | grep rocket-simulator

# Reinstall
pip uninstall rocket-simulator
pip install rocket-simulator
```

### Permission Errors

If you get permission errors on Linux/macOS:

```bash
# Install for current user only
pip install --user rocket-simulator
```

### Version Conflicts

If you have dependency conflicts:

```bash
# Create fresh environment
python -m venv fresh-env
source fresh-env/bin/activate  # or activate on Windows
pip install rocket-simulator
```

---

## Development Installation

For developers who want to contribute:

```bash
# Clone repository
git clone https://github.com/yourusername/rocket-simulator.git
cd rocket-simulator

# Create development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run validation suite
python run_phase5_validation.py
```

---

## Uninstallation

```bash
pip uninstall rocket-simulator
```

---

## System Requirements

### Minimum
- **CPU:** Dual-core 2.0 GHz
- **RAM:** 4 GB
- **Disk:** 500 MB (including dependencies)
- **Python:** 3.11+

### Recommended
- **CPU:** Quad-core 3.0 GHz or better
- **RAM:** 8 GB or more
- **Disk:** 1 GB
- **Python:** 3.13

### Performance
- Single simulation: ~3-5 seconds
- Parameter study (10 runs): ~30-50 seconds

---

## Next Steps

After installation:

1. Read the [Quick Start Guide](QUICKSTART.md)
2. Check out the [API Documentation](docs/)
3. Review [Example Notebooks](examples/notebooks/)
4. See [Contributing Guidelines](CONTRIBUTING.md) to contribute

---

## Support

- **Documentation:** See `docs/` directory
- **Issues:** Report on [GitHub Issues](https://github.com/yourusername/rocket-simulator/issues)
- **Questions:** Check existing issues or open a new one

---

**⚠️ SAFETY WARNING:** This software is for educational purposes only. DO NOT attempt to build actual hydrogen/oxygen rockets. See LICENSE for full disclaimer.

---

**Installation guide for PET Rocket Simulator v0.1.0**  
Last updated: January 25, 2026
