# Quick Start Guide

**PET Rocket Simulator v0.1.0**

Get up and running in 5 minutes!

---

## Your First Simulation

### 1. Basic Simulation

```python
from rocket_sim.integration.full_simulation import (
    FullSimulationConfig,
    run_complete_simulation
)

# Configure 2L PET bottle with H₂:O₂ combustion
config = FullSimulationConfig(
    volume=0.002,              # 2 liters
    fuel_oxidizer_ratio=2.0,   # Stoichiometric H₂:O₂
    vessel_diameter=0.095,     # 95mm
    vessel_thickness=0.0003,   # 0.3mm
    vessel_material="PET"
)

# Run complete simulation
result = run_complete_simulation(config, verbose=True)
```

**Output:**
```
======================================================================
PET ROCKET SIMULATOR - Full System Analysis
======================================================================

[1/3] Running combustion simulation (Cantera)...
      Peak combustion pressure: 2.44 bar
      Peak temperature: 3369 K

[2/3] Running system dynamics (ODE + thin-wall analysis)...
      Peak system pressure: 2.44 bar
      Min safety factor: 1.92

[3/3] Running FEM analysis (Lamé + stress concentrations)...
      Max hoop stress (inner): 38.7 MPa
      Critical location: Cylindrical body

SUMMARY:
  Peak Pressure: 2.44 bar
  Safety Factor: 1.92
  Vessel Status: ✅ Safe
```

### 2. Access Results

```python
# Summary statistics
print(f"Peak Pressure: {result.summary['peak_pressure']/1e5:.2f} bar")
print(f"Peak Temperature: {result.summary['peak_temperature']:.0f} K")
print(f"Min Safety Factor: {result.summary['min_safety_factor']:.2f}")
print(f"Max Stress: {result.summary['max_von_mises_stress']/1e6:.1f} MPa")

# Check safety
if result.failed:
    print(f"⚠️ FAILURE PREDICTED at {result.failure_location}")
else:
    print(f"✅ Safe (SF = {result.safety_margin:.2f})")

# Warnings
for warning in result.warnings:
    print(f"⚠️ {warning}")
```

### 3. Visualize Results

```python
from rocket_sim.visualization.plots import (
    plot_pressure_temperature_time,
    plot_stress_distribution,
    plot_safety_factor_evolution,
    create_comprehensive_dashboard
)

# Individual plots
plot_pressure_temperature_time(result)
plot_stress_distribution(result)
plot_safety_factor_evolution(result)

# Or create complete dashboard
create_comprehensive_dashboard(result, save_path='simulation_results.png')
```

---

## Common Use Cases

### Safe vs Dangerous Configuration

```python
# Safe configuration (hemispherical cap)
config_safe = FullSimulationConfig(
    volume=0.002,
    fuel_oxidizer_ratio=2.0,
    cap_type="hemispherical",  # Ideal cap design
    include_threads=False
)

result_safe = run_complete_simulation(config_safe, verbose=False)
print(f"Safe config SF: {result_safe.safety_margin:.2f}")

# Dangerous configuration (flat cap)
config_danger = FullSimulationConfig(
    volume=0.002,
    fuel_oxidizer_ratio=2.0,
    cap_type="flat",           # High stress concentration!
    include_threads=True       # Additional stress concentration
)

result_danger = run_complete_simulation(config_danger, verbose=False)
print(f"Dangerous config SF: {result_danger.safety_margin:.2f}")
```

### Parameter Study

```python
import numpy as np

# Study effect of wall thickness
thicknesses = np.linspace(0.0002, 0.0005, 5)  # 0.2mm to 0.5mm

for thickness in thicknesses:
    config = FullSimulationConfig(
        volume=0.002,
        fuel_oxidizer_ratio=2.0,
        vessel_thickness=thickness
    )
    
    result = run_complete_simulation(config, verbose=False)
    
    print(f"Thickness {thickness*1000:.2f}mm: "
          f"SF={result.safety_margin:.2f}, "
          f"Status={'FAIL' if result.failed else 'SAFE'}")
```

### Material Comparison

```python
materials = ["PET", "HDPE", "PP", "Aluminum 6061-T6"]

for material in materials:
    config = FullSimulationConfig(
        volume=0.002,
        fuel_oxidizer_ratio=2.0,
        vessel_material=material
    )
    
    result = run_complete_simulation(config, verbose=False)
    
    print(f"{material:20s}: SF={result.safety_margin:.2f}")
```

---

## Understanding the Results

### Key Metrics

**Peak Pressure** - Maximum pressure reached during combustion
- Typical: 2-5 bar for 2L bottle
- Dangerous: >10 bar

**Safety Factor** - How close to failure
- SF > 2.0: Safe (recommended)
- SF 1.0-2.0: Marginal (use caution)
- SF < 1.0: Failure predicted

**Max Stress** - Peak stress in vessel wall
- Compare to material yield strength
- Includes stress concentrations

**Failure Location** - Where vessel will fail
- Common: Threads, flat caps, transitions
- Ideal: Uniform cylindrical section

### Configuration Tips

**For Safety:**
- Use hemispherical caps (K=1.0)
- Avoid threads if possible
- Thicker walls (>0.3mm for PET)
- Lower fuel:oxidizer ratio
- Larger volumes (lower pressure)

**For Higher Performance:**
- Higher fuel:oxidizer ratio
- Smaller volumes
- ⚠️ Increases failure risk!

---

## Quick Reference

### Materials Available
- `"PET"` - Polyethylene terephthalate (bottles)
- `"HDPE"` - High-density polyethylene
- `"PP"` - Polypropylene
- `"Aluminum 6061-T6"` - Aluminum alloy
- `"Steel 304"` - Stainless steel

### Cap Types
- `"hemispherical"` - Ideal (K=1.0)
- `"elliptical"` - Good (K=1.5)
- `"torispherical"` - OK (K=1.8)
- `"conical"` - OK (K=1.5)
- `"flat"` - Dangerous (K=2.5)

### Typical Values (2L PET Bottle)

```python
FullSimulationConfig(
    volume=0.002,              # 2L
    fuel_oxidizer_ratio=2.0,   # Stoichiometric
    initial_temperature=300.0, # 27°C
    initial_pressure=101325.0, # 1 atm
    vessel_diameter=0.095,     # 95mm
    vessel_thickness=0.0003,   # 0.3mm
    vessel_length=0.30,        # 30cm
    vessel_material="PET",
    cap_type="hemispherical",
    combustion_time=0.01       # 10ms simulation
)
```

---

## Export Results

### To JSON

```python
import json

# Export complete results
data = result.to_dict()

with open('results.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### To CSV (Time Series)

```python
import pandas as pd

# Create DataFrame from time series
df = pd.DataFrame({
    'time_ms': result.system.time * 1000,
    'pressure_bar': result.system.pressure / 1e5,
    'temperature_K': result.system.temperature,
    'safety_factor': result.system.safety_factor
})

df.to_csv('timeseries.csv', index=False)
```

---

## Next Steps

1. **Explore Examples:** Check `examples/` directory
2. **Read Documentation:** Full API docs in `docs/`
3. **Run Validation:** `python run_phase5_validation.py`
4. **Customize:** Modify configurations for your scenarios

---

## Safety Reminder

⚠️ **EDUCATIONAL USE ONLY**

This software simulates extremely dangerous devices. DO NOT:
- Build actual H₂/O₂ rockets
- Mix hydrogen and oxygen
- Pressurize PET bottles
- Attempt any physical experiments

This tool is for:
- ✅ Understanding physics
- ✅ Safety analysis
- ✅ Academic research
- ✅ Engineering education

---

## Need Help?

- **Documentation:** See full docs in `docs/` directory
- **Examples:** Check `examples/` for more scenarios
- **Issues:** Report bugs on GitHub
- **Contributing:** See `CONTRIBUTING.md`

---

**Quick Start Guide for PET Rocket Simulator v0.1.0**  
Last updated: January 25, 2026
