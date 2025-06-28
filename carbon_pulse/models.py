"""Data models for Carbon Pulse."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CarbonIntensityData(BaseModel):
    """Carbon intensity data model."""

    zone: str = Field(..., description="Geographic zone identifier")
    timestamp: datetime = Field(..., description="Timestamp of the measurement")
    carbon_intensity: float = Field(..., description="Carbon intensity in gCO2eq/kWh")
    fossil_fuel_percentage: Optional[float] = Field(
        None, description="Percentage of fossil fuel in energy mix"
    )
    renewable_percentage: Optional[float] = Field(
        None, description="Percentage of renewable energy"
    )
    nuclear_percentage: Optional[float] = Field(
        None, description="Percentage of nuclear energy"
    )
    hydro_percentage: Optional[float] = Field(
        None, description="Percentage of hydroelectric energy"
    )
    wind_percentage: Optional[float] = Field(
        None, description="Percentage of wind energy"
    )
    solar_percentage: Optional[float] = Field(
        None, description="Percentage of solar energy"
    )
    biomass_percentage: Optional[float] = Field(
        None, description="Percentage of biomass energy"
    )
    coal_percentage: Optional[float] = Field(
        None, description="Percentage of coal energy"
    )
    gas_percentage: Optional[float] = Field(
        None, description="Percentage of gas energy"
    )
    oil_percentage: Optional[float] = Field(
        None, description="Percentage of oil energy"
    )
    unknown_percentage: Optional[float] = Field(
        None, description="Percentage of unknown energy sources"
    )
    total_production: Optional[float] = Field(
        None, description="Total energy production in MW"
    )
    total_consumption: Optional[float] = Field(
        None, description="Total energy consumption in MW"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ZoneInfo(BaseModel):
    """Zone information model."""

    zone: str = Field(..., description="Zone identifier")
    name: str = Field(..., description="Zone name")
    country: str = Field(..., description="Country name")
    latitude: float = Field(..., description="Zone latitude")
    longitude: float = Field(..., description="Zone longitude")
    timezone: str = Field(..., description="Zone timezone")


class APIResponse(BaseModel):
    """Standard API response model."""

    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[dict] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
