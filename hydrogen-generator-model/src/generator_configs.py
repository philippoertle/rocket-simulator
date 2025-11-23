"""
Configuration data for various hydrogen generator designs from DIY sources.

Based on real designs from:
- Instructables (multiple projects)
- Hackaday
- Making-hydrogen.com
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GeneratorConfig:
    """Configuration for a specific generator design."""
    name: str
    source: str
    description: str
    
    # Electrical parameters
    voltage_volts: float
    current_amperes: float
    power_supply_type: str
    
    # Electrode configuration
    electrode_material: str
    number_of_plates: int
    plate_width_mm: float
    plate_height_mm: float
    plate_thickness_mm: float
    plate_spacing_mm: float
    
    # Electrolyte
    electrolyte_type: str
    electrolyte_concentration_description: str
    naoh_concentration_molar: float
    water_volume_ml: float
    
    # Cell type
    cell_type: str  # "dry_cell" or "wet_cell"
    
    # Performance data (if available)
    reported_production_lpm: float = 0.0
    operating_temperature_celsius: float = 25.0
    
    # Additional notes
    notes: List[str] = field(default_factory=list)


# Collection of generator configurations from sources
GENERATOR_CONFIGS: Dict[str, GeneratorConfig] = {
    
    "instructables_dry_cell": GeneratorConfig(
        name="Instructables Dry Cell Electrolyser",
        source="https://www.instructables.com/Dry-Cell-Electrolyser/",
        description="Professional dry cell design with 15 stainless steel plates, polycarbonate ends, and PVC gaskets",
        voltage_volts=12.0,
        current_amperes=20.0,
        power_supply_type="Car battery or PSU (12V, >20A)",
        electrode_material="stainless_steel_304",
        number_of_plates=15,  # 8 A plates, 7 B plates
        plate_width_mm=160.0,
        plate_height_mm=200.0,
        plate_thickness_mm=0.7,
        plate_spacing_mm=3.0,  # 3mm PVC gasket
        electrolyte_type="NaOH (Sodium Hydroxide)",
        electrolyte_concentration_description="1:40 water to NaOH",
        naoh_concentration_molar=0.375,  # Calculated from 1:40 ratio
        water_volume_ml=2000.0,
        cell_type="dry_cell",
        operating_temperature_celsius=45.0,
        notes=[
            "Uses 3mm PVC gaskets between plates",
            "Polycarbonate end walls with threaded fittings",
            "Multiple gaskets required for sealing",
            "Professional quality construction"
        ]
    ),
    
    "instructables_basic": GeneratorConfig(
        name="Basic DIY Hydrogen Generator",
        source="https://www.instructables.com/DIY-hydrogen-generator/",
        description="Simple design using pencil lead electrodes in container",
        voltage_volts=12.0,
        current_amperes=2.0,
        power_supply_type="Hacked ATX power supply or DC adapter",
        electrode_material="graphite",  # pencil lead
        number_of_plates=2,  # Simple anode/cathode
        plate_width_mm=5.0,  # Pencil lead diameter
        plate_height_mm=100.0,
        plate_thickness_mm=2.0,
        plate_spacing_mm=50.0,
        electrolyte_type="Salt water or NaOH",
        electrolyte_concentration_description="Tap water with salt",
        naoh_concentration_molar=0.1,
        water_volume_ml=500.0,
        cell_type="wet_cell",
        operating_temperature_celsius=30.0,
        reported_production_lpm=0.05,
        notes=[
            "Beginner-friendly design",
            "Uses common household items",
            "Low production rate",
            "Educational purposes"
        ]
    ),
    
    "instructables_adjustable": GeneratorConfig(
        name="Electrolyzer with Adjustable Torch (3000°C)",
        source="https://www.instructables.com/How-to-Make-an-Electrolyzer-3000C-Adjustable-Homem/",
        description="HHO generator with adjustable power supply and burner",
        voltage_volts=6.0,
        current_amperes=6.0,
        power_supply_type="Adjustable power supply (6-12V, 4-6A)",
        electrode_material="stainless_steel_316",
        number_of_plates=10,  # Stainless steel rings on studs
        plate_width_mm=50.0,  # Estimated ring diameter
        plate_height_mm=50.0,
        plate_thickness_mm=1.0,
        plate_spacing_mm=5.0,
        electrolyte_type="NaOH",
        electrolyte_concentration_description="Water with NaOH powder",
        naoh_concentration_molar=0.3,
        water_volume_ml=1000.0,
        cell_type="wet_cell",
        operating_temperature_celsius=50.0,
        notes=[
            "Uses stainless steel rings as electrodes",
            "Water barrier for safety",
            "Adjustable flame up to 2000-3000°C",
            "Temperature reaches 45-55°C during operation"
        ]
    ),
    
    "instructables_razor_blade": GeneratorConfig(
        name="Powerful HHO Generator (99+ Razor Blades)",
        source="https://www.instructables.com/Powerful-HHO-Generator-Using-99-Razor-Blades-for-E/",
        description="High-power generator using 150+ razor blades as electrodes",
        voltage_volts=12.0,
        current_amperes=10.0,
        power_supply_type="Air-cooled power supply (6-12V, ≥4A)",
        electrode_material="razor_blade",  # Stainless steel razor blades
        number_of_plates=150,
        plate_width_mm=40.0,  # Approximate razor blade width
        plate_height_mm=20.0,
        plate_thickness_mm=0.1,  # Very thin blades
        plate_spacing_mm=1.0,  # Nut spacing between blades
        electrolyte_type="NaOH",
        electrolyte_concentration_description="Water with sodium hydroxide",
        naoh_concentration_molar=0.4,
        water_volume_ml=2000.0,
        cell_type="wet_cell",
        operating_temperature_celsius=55.0,
        notes=[
            "Very large surface area from many thin blades",
            "Flame reaches 2500°C",
            "No corrosion observed after 30 minutes",
            "High-pressure tubes used",
            "Water barrier for safety"
        ]
    ),
    
    "hackaday_automated": GeneratorConfig(
        name="Automated Hydrogen Generator",
        source="https://hackaday.com/2023/10/06/creating-an-automated-hydrogen-generator-at-home/",
        description="Automated system with glass bell separator and vacuum pump",
        voltage_volts=12.0,
        current_amperes=15.0,
        power_supply_type="DC power supply with control system",
        electrode_material="stainless_steel_316",
        number_of_plates=10,
        plate_width_mm=100.0,
        plate_height_mm=150.0,
        plate_thickness_mm=2.0,
        plate_spacing_mm=10.0,
        electrolyte_type="NaOH",
        electrolyte_concentration_description="NaOH in water",
        naoh_concentration_molar=0.5,
        water_volume_ml=3000.0,
        cell_type="wet_cell",
        operating_temperature_celsius=40.0,
        notes=[
            "Uses glass bell for gas collection",
            "Vacuum pump for gas transfer",
            "Aluminum storage tank (hydrogen embrittlement concerns)",
            "Automated control system with safety features",
            "Can run for hours unattended"
        ]
    ),
    
    "typical_small_scale": GeneratorConfig(
        name="Typical Small-Scale DIY Generator",
        source="Multiple sources - averaged parameters",
        description="Representative small DIY generator for experimentation",
        voltage_volts=12.0,
        current_amperes=5.0,
        power_supply_type="12V DC adapter or battery",
        electrode_material="stainless_steel_316",
        number_of_plates=7,
        plate_width_mm=100.0,
        plate_height_mm=100.0,
        plate_thickness_mm=1.0,
        plate_spacing_mm=5.0,
        electrolyte_type="NaOH",
        electrolyte_concentration_description="~1 tablespoon per liter",
        naoh_concentration_molar=0.35,
        water_volume_ml=1000.0,
        cell_type="wet_cell",
        operating_temperature_celsius=35.0,
        reported_production_lpm=0.3,
        notes=[
            "Good balance of size and performance",
            "Moderate power consumption",
            "Suitable for demonstrations"
        ]
    ),
    
    "high_performance_dry_cell": GeneratorConfig(
        name="High-Performance Dry Cell",
        source="Multiple sources - optimized design",
        description="Optimized dry cell for maximum efficiency",
        voltage_volts=14.0,
        current_amperes=30.0,
        power_supply_type="High-current DC supply (14V, 30A+)",
        electrode_material="stainless_steel_316",
        number_of_plates=21,
        plate_width_mm=200.0,
        plate_height_mm=200.0,
        plate_thickness_mm=1.0,
        plate_spacing_mm=2.5,
        electrolyte_type="KOH (Potassium Hydroxide)",
        electrolyte_concentration_description="25% KOH solution",
        naoh_concentration_molar=4.5,  # Using KOH instead
        water_volume_ml=3000.0,
        cell_type="dry_cell",
        operating_temperature_celsius=60.0,
        reported_production_lpm=2.5,
        notes=[
            "High current density design",
            "KOH for better conductivity than NaOH",
            "Cooling may be required",
            "Maximum practical efficiency",
            "Requires robust power supply"
        ]
    ),
}


# Operating parameter ranges from literature
PARAMETER_RANGES = {
    "voltage": {
        "min": 1.23,  # Theoretical minimum
        "typical_min": 1.8,
        "typical_max": 2.5,
        "practical_min": 6.0,  # For multi-cell DIY
        "practical_max": 14.0,
        "description": "Applied voltage (V)"
    },
    "current": {
        "min": 0.1,
        "typical_min": 2.0,
        "typical_max": 30.0,
        "max": 100.0,
        "description": "Operating current (A)"
    },
    "current_density": {
        "low": 50,
        "optimal_min": 100,
        "optimal_max": 500,
        "high": 1000,
        "max": 2000,
        "description": "Current density (mA/cm²)"
    },
    "temperature": {
        "min": 20,
        "optimal_min": 40,
        "optimal_max": 60,
        "max": 80,
        "description": "Operating temperature (°C)"
    },
    "naoh_concentration": {
        "min": 0.1,
        "typical": 0.35,
        "optimal": 4.5,
        "max": 8.0,
        "description": "NaOH concentration (mol/L)"
    },
    "plate_spacing": {
        "min": 1.0,
        "optimal_min": 2.0,
        "optimal_max": 5.0,
        "max": 10.0,
        "description": "Electrode spacing (mm)"
    },
    "efficiency": {
        "poor": 0.30,
        "typical": 0.50,
        "good": 0.70,
        "excellent": 0.85,
        "theoretical_max": 1.0,
        "description": "Overall system efficiency (fraction)"
    }
}


# Material properties for electrodes
ELECTRODE_MATERIALS = {
    "stainless_steel_316": {
        "cost_relative": 1.0,
        "corrosion_resistance": "excellent",
        "conductivity_relative": 0.8,
        "lifetime_hours": 1000,
        "notes": "Most common DIY choice, good balance"
    },
    "stainless_steel_304": {
        "cost_relative": 0.9,
        "corrosion_resistance": "very_good",
        "conductivity_relative": 0.8,
        "lifetime_hours": 800,
        "notes": "Slightly less corrosion resistant than 316"
    },
    "graphite": {
        "cost_relative": 0.3,
        "corrosion_resistance": "good",
        "conductivity_relative": 0.3,
        "lifetime_hours": 200,
        "notes": "Cheap but degrades, suitable for experiments"
    },
    "platinum": {
        "cost_relative": 100.0,
        "corrosion_resistance": "excellent",
        "conductivity_relative": 1.0,
        "lifetime_hours": 10000,
        "notes": "Ideal but prohibitively expensive for DIY"
    },
    "razor_blade": {
        "cost_relative": 0.5,
        "corrosion_resistance": "good",
        "conductivity_relative": 0.8,
        "lifetime_hours": 500,
        "notes": "Thin, high surface area, stainless steel"
    }
}


def get_config(name: str) -> GeneratorConfig:
    """Get a generator configuration by name."""
    if name not in GENERATOR_CONFIGS:
        raise ValueError(f"Unknown configuration: {name}. Available: {list(GENERATOR_CONFIGS.keys())}")
    return GENERATOR_CONFIGS[name]


def list_configs() -> List[str]:
    """List all available generator configurations."""
    return list(GENERATOR_CONFIGS.keys())


def print_config_summary(config: GeneratorConfig):
    """Print a summary of a generator configuration."""
    print(f"\n=== {config.name} ===")
    print(f"Source: {config.source}")
    print(f"Description: {config.description}")
    print(f"\nElectrical:")
    print(f"  Voltage: {config.voltage_volts} V")
    print(f"  Current: {config.current_amperes} A")
    print(f"  Power: {config.voltage_volts * config.current_amperes} W")
    print(f"\nElectrodes:")
    print(f"  Material: {config.electrode_material}")
    print(f"  Number: {config.number_of_plates}")
    print(f"  Size: {config.plate_width_mm}x{config.plate_height_mm}x{config.plate_thickness_mm} mm")
    print(f"  Spacing: {config.plate_spacing_mm} mm")
    print(f"\nElectrolyte:")
    print(f"  Type: {config.electrolyte_type}")
    print(f"  Concentration: {config.electrolyte_concentration_description}")
    print(f"  Volume: {config.water_volume_ml} ml")
    print(f"\nPerformance:")
    print(f"  Type: {config.cell_type}")
    print(f"  Temperature: {config.operating_temperature_celsius}°C")
    if config.reported_production_lpm > 0:
        print(f"  Production: {config.reported_production_lpm} L/min")
    print(f"\nNotes:")
    for note in config.notes:
        print(f"  - {note}")


if __name__ == "__main__":
    print("=== Available Hydrogen Generator Configurations ===\n")
    
    for config_name in list_configs():
        config = get_config(config_name)
        print_config_summary(config)
        print("\n" + "="*60)
