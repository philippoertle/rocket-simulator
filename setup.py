"""
Setup script for PET Rocket Simulator
ISO/IEC/IEEE 12207:2017 Compliant Development
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = []

setup(
    name="rocket-sim",
    version="0.1.0",
    author="Philipp Oertle",
    author_email="philip.oertle@protonmail.com",
    description="Safety-focused simulation framework for PET bottle H2/O2 rockets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/philippoertle/rocket-simulator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "pylint>=2.17.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.4.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
        "gui": [
            "PySide6>=6.6.0",
        ],
    },
    include_package_data=True,
    package_data={
        "rocket_sim": ["configs/*.json"],
    },
    entry_points={
        "console_scripts": [
            "rocket-sim-gui=rocket_sim.gui.__main__:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/philippoertle/rocket-simulator/issues",
        "Source": "https://github.com/philippoertle/rocket-simulator",
        "Documentation": "https://github.com/philippoertle/rocket-simulator/blob/main/README.md",
    },
    keywords="rocket simulation safety combustion cantera structural-analysis",
)
