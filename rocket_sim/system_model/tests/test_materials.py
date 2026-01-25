"""
Unit tests for materials module

ISO/IEC/IEEE 12207:2017 - Verification Process
"""

import pytest
from rocket_sim.system_model.materials import (
    MaterialProperties,
    get_material,
    list_available_materials,
    get_material_summary,
    get_bottle_material,
    MATERIALS
)


class TestMaterialDatabase:
    """Test material database functionality."""

    def test_list_available_materials(self):
        """Test that we can list available materials."""
        materials = list_available_materials()
        assert isinstance(materials, list)
        assert len(materials) > 0
        assert "PET" in materials
        assert "HDPE" in materials

    def test_get_material_pet(self):
        """Test retrieving PET material properties."""
        pet = get_material("PET")
        assert isinstance(pet, MaterialProperties)
        assert pet.name == "Polyethylene Terephthalate (PET)"
        assert pet.yield_strength > 0
        assert pet.tensile_strength > pet.yield_strength
        assert pet.elastic_modulus > 0
        assert 0 < pet.poisson_ratio < 0.5

    def test_get_material_case_insensitive(self):
        """Test case-insensitive material lookup."""
        pet1 = get_material("PET")
        pet2 = get_material("pet")
        pet3 = get_material("Pet")
        assert pet1.name == pet2.name == pet3.name

    def test_get_material_invalid(self):
        """Test that invalid material raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            get_material("InvalidMaterial")

    def test_get_material_hdpe(self):
        """Test retrieving HDPE material."""
        hdpe = get_material("HDPE")
        assert hdpe.name == "High-Density Polyethylene (HDPE)"
        assert hdpe.yield_strength > 0

    def test_get_material_aluminum(self):
        """Test retrieving aluminum material."""
        al = get_material("Aluminum_6061_T6")
        assert "Aluminum" in al.name
        assert al.yield_strength > 200e6  # >200 MPa

    def test_material_properties_complete(self):
        """Test that all materials have required properties."""
        for mat_name in list_available_materials():
            mat = get_material(mat_name)
            assert mat.yield_strength > 0
            assert mat.tensile_strength > 0
            assert mat.elastic_modulus > 0
            assert mat.poisson_ratio > 0
            assert mat.density > 0
            assert mat.max_temperature > 0
            assert len(mat.source) > 0


class TestMaterialProperties:
    """Test MaterialProperties dataclass."""

    def test_material_properties_creation(self):
        """Test creating MaterialProperties object."""
        mat = MaterialProperties(
            name="Test Material",
            yield_strength=50e6,
            tensile_strength=70e6,
            elastic_modulus=2e9,
            poisson_ratio=0.35,
            density=1000.0,
            max_temperature=400.0,
            source="Test data"
        )
        assert mat.name == "Test Material"
        assert mat.yield_strength == 50e6

    def test_pet_properties_realistic(self):
        """Test that PET properties are in realistic range."""
        pet = get_material("PET")
        # Typical PET values
        assert 40e6 < pet.yield_strength < 80e6  # 40-80 MPa
        assert 60e6 < pet.tensile_strength < 100e6  # 60-100 MPa
        assert 2e9 < pet.elastic_modulus < 4e9  # 2-4 GPa
        assert 0.3 < pet.poisson_ratio < 0.45
        assert 1300 < pet.density < 1500  # kg/m³

    def test_strength_ordering(self):
        """Test that tensile strength >= yield strength for all materials."""
        for mat_name in list_available_materials():
            mat = get_material(mat_name)
            assert mat.tensile_strength >= mat.yield_strength, \
                f"{mat_name}: tensile must be >= yield"


class TestBottleMaterials:
    """Test bottle material helper functions."""

    def test_get_bottle_material_soda(self):
        """Test getting soda bottle material (PET)."""
        mat = get_bottle_material("soda")
        assert "PET" in mat.name or "Polyethylene Terephthalate" in mat.name

    def test_get_bottle_material_milk(self):
        """Test getting milk bottle material (HDPE)."""
        mat = get_bottle_material("milk")
        assert "HDPE" in mat.name or "Polyethylene" in mat.name

    def test_get_bottle_material_case_insensitive(self):
        """Test case-insensitive bottle type."""
        mat1 = get_bottle_material("SODA")
        mat2 = get_bottle_material("soda")
        assert mat1.name == mat2.name

    def test_get_bottle_material_invalid(self):
        """Test invalid bottle type raises error."""
        with pytest.raises(ValueError, match="Unknown bottle type"):
            get_bottle_material("invalid_bottle")


class TestMaterialSummary:
    """Test material summary function."""

    def test_get_material_summary(self):
        """Test that summary returns formatted string."""
        summary = get_material_summary("PET")
        assert isinstance(summary, str)
        assert "PET" in summary
        assert "MPa" in summary
        assert "GPa" in summary

    def test_summary_contains_key_properties(self):
        """Test that summary includes all key properties."""
        summary = get_material_summary("PET")
        assert "Yield Strength" in summary
        assert "Tensile Strength" in summary
        assert "Elastic Modulus" in summary
        assert "Poisson Ratio" in summary
        assert "Density" in summary
        assert "Source" in summary


class TestMaterialComparisons:
    """Test comparisons between different materials."""

    def test_metals_stronger_than_polymers(self):
        """Test that metals have higher strength than polymers."""
        pet = get_material("PET")
        aluminum = get_material("Aluminum_6061_T6")
        steel = get_material("Steel_304")

        assert aluminum.yield_strength > pet.yield_strength
        assert steel.yield_strength > pet.yield_strength

    def test_metals_stiffer_than_polymers(self):
        """Test that metals have higher modulus than polymers."""
        pet = get_material("PET")
        aluminum = get_material("Aluminum_6061_T6")

        assert aluminum.elastic_modulus > pet.elastic_modulus

    def test_metals_denser_than_polymers(self):
        """Test that metals are denser than polymers."""
        pet = get_material("PET")
        aluminum = get_material("Aluminum_6061_T6")

        assert aluminum.density > pet.density


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
