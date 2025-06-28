"""Tests for data models."""

import pytest
from datetime import datetime

from carbon_pulse.models import CarbonIntensityData, ZoneInfo, APIResponse


class TestCarbonIntensityData:
    """Test CarbonIntensityData model."""

    def test_carbon_intensity_data_creation(self):
        """Test creating a CarbonIntensityData instance."""
        data = CarbonIntensityData(
            zone="US",
            timestamp=datetime.utcnow(),
            carbon_intensity=300.5,
            renewable_percentage=25.0,
            fossil_fuel_percentage=60.0,
        )

        assert data.zone == "US"
        assert data.carbon_intensity == 300.5
        assert data.renewable_percentage == 25.0
        assert data.fossil_fuel_percentage == 60.0

    def test_carbon_intensity_data_optional_fields(self):
        """Test CarbonIntensityData with optional fields."""
        data = CarbonIntensityData(
            zone="DE", timestamp=datetime.utcnow(), carbon_intensity=150.0
        )

        assert data.zone == "DE"
        assert data.carbon_intensity == 150.0
        assert data.renewable_percentage is None
        assert data.fossil_fuel_percentage is None


class TestZoneInfo:
    """Test ZoneInfo model."""

    def test_zone_info_creation(self):
        """Test creating a ZoneInfo instance."""
        zone = ZoneInfo(
            zone="US",
            name="United States",
            country="United States",
            latitude=39.8283,
            longitude=-98.5795,
            timezone="America/New_York",
        )

        assert zone.zone == "US"
        assert zone.name == "United States"
        assert zone.country == "United States"
        assert zone.latitude == 39.8283
        assert zone.longitude == -98.5795
        assert zone.timezone == "America/New_York"


class TestAPIResponse:
    """Test APIResponse model."""

    def test_api_response_creation(self):
        """Test creating an APIResponse instance."""
        response = APIResponse(
            success=True, data={"test": "data"}, message="Test response"
        )

        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.message == "Test response"
        assert response.timestamp is not None

    def test_api_response_defaults(self):
        """Test APIResponse with default values."""
        response = APIResponse(success=False)

        assert response.success is False
        assert response.data is None
        assert response.message is None
        assert response.timestamp is not None
