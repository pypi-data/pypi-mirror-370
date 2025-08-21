from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntensityIndex(str, Enum):
    VERY_LOW = "very low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very high"


class FuelType(str, Enum):
    GAS = "gas"
    COAL = "coal"
    BIOMASS = "biomass"
    NUCLEAR = "nuclear"
    HYDRO = "hydro"
    IMPORTS = "imports"
    OTHER = "other"
    WIND = "wind"
    SOLAR = "solar"


class IntensityData(BaseModel):
    forecast: int | None = None
    actual: int | None = None
    index: IntensityIndex


class StatisticsData(BaseModel):
    max: int
    average: int
    min: int
    index: IntensityIndex


class GenerationMixItem(BaseModel):
    fuel: FuelType
    perc: float


class IntensityPeriod(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime
    intensity: IntensityData


class StatisticsPeriod(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime
    intensity: StatisticsData


class GenerationPeriod(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime
    generationmix: list[GenerationMixItem]


class RegionData(BaseModel):
    regionid: int
    dnoregion: str
    shortname: str
    intensity: IntensityData
    generationmix: list[GenerationMixItem] | None = None


class RegionalPeriod(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime
    regions: list[RegionData]


class RegionalByIdData(BaseModel):
    regionid: int
    dnoregion: str
    shortname: str
    data: list[IntensityPeriod]
    postcode: str | None = None


class IntensityResponse(BaseModel):
    data: list[IntensityPeriod]


class StatisticsResponse(BaseModel):
    data: list[StatisticsPeriod]


class GenerationResponse(BaseModel):
    data: list[GenerationPeriod]


class RegionalResponse(BaseModel):
    data: list[RegionalPeriod]


class RegionalByIdResponse(BaseModel):
    data: list[RegionalByIdData]


class FactorsResponse(BaseModel):
    data: list[dict[str, int]]


class ErrorResponse(BaseModel):
    error: dict[str, Any]
