import pytest
from carbon_intensity_mcp.models import IntensityIndex, FuelType, IntensityData

def test_intensity_index_enum():
    assert IntensityIndex.MODERATE == "moderate"
    assert IntensityIndex.HIGH == "high"

def test_fuel_type_enum():
    assert FuelType.GAS == "gas"
    assert FuelType.NUCLEAR == "nuclear"

def test_intensity_data_model():
    data = IntensityData(
        forecast=266,
        actual=263,
        index=IntensityIndex.MODERATE
    )
    assert data.forecast == 266
    assert data.actual == 263
    assert data.index == IntensityIndex.MODERATE
