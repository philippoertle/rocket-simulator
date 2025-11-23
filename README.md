# Rocket Simulator

A collection of aerospace engineering simulation tools and models.

## Projects

### 🔬 Hydrogen Generator Efficiency Model

A comprehensive chemical and physical model for analyzing hydrogen production efficiency in DIY electrolysis-based hydrogen generators.

**Location**: [`hydrogen-generator-model/`](./hydrogen-generator-model/)

**Features**:
- Chemical process modeling (Faraday's law, thermodynamics)
- Physical design analysis (electrode geometry, current density)
- Real-world DIY configurations from multiple sources
- Battery-powered operation analysis (3×9V batteries)
- Comprehensive visualizations and reporting tools

**Quick Start**:
```bash
cd hydrogen-generator-model
pip install -r requirements.txt
python battery_report.py  # Generate full analysis
```

See the [Hydrogen Generator Model README](./hydrogen-generator-model/README.md) for detailed documentation.

---

## Repository Structure

```
rocket-simulator/
├── hydrogen-generator-model/    # Hydrogen production efficiency models
│   ├── src/                     # Source code modules
│   ├── outputs/                 # Generated reports and visualizations
│   ├── docs/                    # Documentation
│   └── examples/                # Usage examples
└── README.md                    # This file
```

## Future Projects

- Rocket trajectory simulation
- Propulsion system analysis
- Aerodynamic modeling
- Flight control systems

## Contributing

This repository contains educational and research tools. Contributions and improvements are welcome.

## License

Educational use - See individual project directories for specific licensing.

## Safety

⚠️ **Warning**: Projects involving hydrogen generation, rocket propulsion, or other energetic systems carry significant safety risks. All models are for educational and analysis purposes only. Always follow proper safety protocols and consult qualified experts before constructing any physical systems.

---

**Owner**: philippoertle  
**Repository**: rocket-simulator  
**Last Updated**: November 23, 2025
