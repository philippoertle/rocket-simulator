# PET Bottle Hydrogen/Oxygen Rocket --- Simulation Toolchain Specification

AI‑Optimized Development Input (for Claude Sonnet or similar coding
agents)

------------------------------------------------------------------------

## Objective

Develop a **fully open‑source, code‑driven simulation framework** to
analyze why a small experimental rocket using:

-   Hydrogen + Oxygen combustion
-   PET beverage bottle as pressure vessel

sometimes lifts off and sometimes ruptures/explodes.

Primary goal:

> Predict and prevent structural burst by modeling transient pressure,
> temperature, and stresses.

NOT focused on propulsion optimization.\
Focus is **failure prevention and structural safety analysis**.

------------------------------------------------------------------------

## Safety Context (important assumptions)

PET bottles:

-   thin wall plastic pressure vessel
-   brittle failure
-   softening above \~70--80 °C
-   burst typically 6--12 bar
-   sensitive to scratches/imperfections
-   weak threaded neck region

Hydrogen/Oxygen:

-   very high flame speed
-   extremely fast pressure rise (µs--ms)
-   peak pressure can exceed 50--100+ bar in closed volume

Therefore:

System behaves like a **rapidly exploding pressure vessel**, not a
steady rocket motor.

Simulation priority:

1.  Pressure rise rate (dP/dt)
2.  Peak pressure
3.  Thermal softening
4.  Hoop stress and rupture

CFD details are secondary.

------------------------------------------------------------------------

# System Architecture

The solution shall consist of 4 coupled modules:

1.  Thermochemistry (combustion → pressure curve)
2.  System dynamics (mass/energy ODE model)
3.  Structural FEM (burst analysis)
4.  Optional CFD (flow field refinement)

All modules must be scriptable and automatable.

Language preference: Python-first.

------------------------------------------------------------------------

# Required Open Source Stack

## Mandatory

-   Python 3.11+
-   NumPy
-   SciPy
-   Matplotlib
-   Cantera
-   CalculiX or Code_Aster

## Optional

-   OpenFOAM

------------------------------------------------------------------------

# Module Specifications

## Module 1 --- Thermochemistry

Tool: Cantera

Purpose:

Compute constant‑volume combustion of H₂/O₂ and output:

-   pressure vs time
-   temperature vs time
-   max pressure
-   rise time
-   heat release rate

Inputs:

-   initial T
-   initial P
-   mixture ratio
-   chamber volume

Outputs:

-   P(t)
-   T(t)
-   dP/dt_max

Example API:

``` python
simulate_combustion(volume, mix_ratio, T0, P0) -> dict
```

Return:

    {
      "time": array,
      "pressure": array,
      "temperature": array,
      "peak_pressure": float,
      "max_dPdt": float
    }

------------------------------------------------------------------------

## Module 2 --- System Dynamics

Tool: Python + SciPy ODE

Purpose:

Simulate:

-   tank depletion
-   valve opening
-   mass flow
-   chamber filling
-   ignition timing
-   transient pressure buildup

Method:

-   lumped parameter ODEs
-   solve_ivp

Inputs:

-   bottle volume
-   valve area
-   discharge coefficients
-   ignition time
-   gas properties

Outputs:

-   chamber pressure vs time
-   thrust estimate
-   loads for FEM

API:

``` python
run_system_model(params) -> dict
```

------------------------------------------------------------------------

## Module 3 --- Structural Burst Analysis

Tool: CalculiX (preferred for simplicity)

Purpose:

Determine:

-   hoop stress
-   von Mises stress
-   deformation
-   burst safety factor
-   failure time

Geometry:

-   thin-walled cylinder + dome
-   include neck thickness reduction

Material model (PET):

    E = 2.5e9 Pa
    nu = 0.38
    yield ≈ 55e6 Pa
    temperature dependent modulus

Load:

-   transient internal pressure P(t)
-   optional thermal load

Outputs:

-   max stress
-   safety factor
-   predicted rupture

API:

``` python
run_fem(pressure_curve, geometry, material) -> dict
```

------------------------------------------------------------------------

## Module 4 --- CFD (optional later)

Tool: OpenFOAM

Purpose:

-   injector mixing
-   combustion instability
-   spatial pressure gradients

Solvers:

-   rhoReactingFoam

Only required if structural model indicates safe pressures but failure
still occurs.

------------------------------------------------------------------------

# Coupling Workflow

Execution order:

1.  Cantera → P(t)
2.  System ODE → refined P(t)
3.  FEM → stress vs time
4.  Evaluate burst criteria

Pipeline:

    combustion → system → FEM → safety factor

------------------------------------------------------------------------

# Analytical Pre-Check (must implement)

Before FEM, compute thin-wall estimate:

Hoop stress:

σ = P r / t

Burst pressure:

P_burst = σ_fail t / r

Use as quick reject criterion.

------------------------------------------------------------------------

# Acceptance Criteria

The system shall:

-   run fully from CLI
-   be reproducible
-   require no proprietary tools
-   output plots automatically
-   export results as CSV/JSON
-   allow parameter sweeps
-   identify unsafe configurations

------------------------------------------------------------------------

# Suggested Project Structure

    rocket_sim/
    │
    ├─ combustion/
    ├─ system_model/
    ├─ fem/
    ├─ utils/
    ├─ configs/
    ├─ notebooks/
    └─ main.py

------------------------------------------------------------------------

# Development Tasks (for AI agent)

Implement in order:

1.  Cantera combustion simulator
2.  Python ODE pressure model
3.  Analytical burst calculator
4.  CalculiX automation wrapper
5.  Integrated pipeline script
6.  Parameter sweep tool
7.  Plotting + reports

------------------------------------------------------------------------

# Key Insight

For PET rockets:

Structural rupture risk dominates.

Therefore:

Prioritize: - transient pressure - material softening - burst stress

Deprioritize: - detailed CFD - nozzle optimization

------------------------------------------------------------------------

End of specification.
