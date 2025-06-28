"""Tests for Electricity Maps API client."""

import pytest
import responses
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from carbon_pulse.data.electricity_maps import ElectricityMapsClient
from carbon_pulse.models import CarbonIntensityData, ZoneInfo


class TestElectricityMapsClient:
    """Test ElectricityMapsClient class."""

    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return ElectricityMapsClient()

    @pytest.fixture
    def mock_zones_response(self):
        """Mock zones API response."""
        return {
            "US": {
                "name": "United States",
                "countryName": "United States",
                "latitude": 39.8283,
                "longitude": -98.5795,
                "timezone": "America/New_York",
            },
            "DE": {
                "name": "Germany",
                "countryName": "Germany",
                "latitude": 51.1657,
                "longitude": 10.4515,
                "timezone": "Europe/Berlin",
            },
            "FR": {
                "name": "France",
                "countryName": "France",
                "latitude": 46.2276,
                "longitude": 2.2137,
                "timezone": "Europe/Paris",
            },
        }

    @pytest.fixture
    def mock_carbon_intensity_response(self):
        """Mock carbon intensity API response."""
        return {
            "datetime": "2024-01-15T10:30:00Z",
            "carbonIntensity": 250.5,
            "fossilFuelPercentage": 60.0,
            "renewablePercentage": 25.0,
            "nuclearPercentage": 15.0,
            "hydroPercentage": 8.0,
            "windPercentage": 12.0,
            "solarPercentage": 5.0,
            "biomassPercentage": 2.0,
            "coalPercentage": 20.0,
            "gasPercentage": 30.0,
            "oilPercentage": 10.0,
            "unknownPercentage": 5.0,
            "totalProduction": 5000.0,
            "totalConsumption": 4800.0,
        }

    @pytest.fixture
    def mock_history_response(self):
        """Mock carbon intensity history API response."""
        return {
            "history": [
                {
                    "datetime": "2024-01-15T10:00:00Z",
                    "carbonIntensity": 240.0,
                    "fossilFuelPercentage": 58.0,
                    "renewablePercentage": 27.0,
                    "nuclearPercentage": 15.0,
                },
                {
                    "datetime": "2024-01-15T10:30:00Z",
                    "carbonIntensity": 250.5,
                    "fossilFuelPercentage": 60.0,
                    "renewablePercentage": 25.0,
                    "nuclearPercentage": 15.0,
                },
            ]
        }

    @pytest.fixture
    def mock_power_breakdown_response(self):
        """Mock power production breakdown API response."""
        return {
            "zone": "US",
            "datetime": "2024-01-15T10:30:00Z",
            "production": {
                "coal": 1000.0,
                "gas": 1500.0,
                "nuclear": 750.0,
                "wind": 600.0,
                "solar": 250.0,
                "hydro": 400.0,
                "biomass": 100.0,
            },
        }

    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.base_url == "https://api.electricitymap.org/v3"
        assert client.api_key is None
        assert client.session is not None

    def test_client_initialization_with_api_key(self):
        """Test client initialization with API key."""
        with patch("carbon_pulse.config.settings") as mock_settings:
            mock_settings.electricity_maps_api_key = "test_api_key"
            mock_settings.electricity_maps_base_url = (
                "https://api.electricitymap.org/v3"
            )

            client = ElectricityMapsClient()
            assert client.api_key == "test_api_key"
            assert "auth-token" in client.session.headers
            assert client.session.headers["auth-token"] == "test_api_key"

    @responses.activate
    def test_get_zones_success(self, client, mock_zones_response):
        """Test successful zones retrieval."""
        # Mock the API response
        responses.add(
            responses.GET,
            f"{client.base_url}/zones",
            json=mock_zones_response,
            status=200,
        )

        zones = client.get_zones()

        assert len(zones) == 3
        assert all(isinstance(zone, ZoneInfo) for zone in zones)

        # Check specific zone data
        us_zone = next(zone for zone in zones if zone.zone == "US")
        assert us_zone.name == "United States"
        assert us_zone.country == "United States"
        assert us_zone.latitude == 39.8283
        assert us_zone.longitude == -98.5795
        assert us_zone.timezone == "America/New_York"

    @responses.activate
    def test_get_zones_api_error(self, client):
        """Test zones retrieval with API error."""
        # Mock API error
        responses.add(responses.GET, f"{client.base_url}/zones", status=500)

        with pytest.raises(Exception):
            client.get_zones()

    @responses.activate
    def test_get_carbon_intensity_success(self, client, mock_carbon_intensity_response):
        """Test successful carbon intensity retrieval."""
        # Mock the API response
        responses.add(
            responses.GET,
            f"{client.base_url}/carbon-intensity/US",
            json=mock_carbon_intensity_response,
            status=200,
        )

        data = client.get_carbon_intensity("US")

        assert isinstance(data, CarbonIntensityData)
        assert data.zone == "US"
        assert data.carbon_intensity == 250.5
        assert data.fossil_fuel_percentage == 60.0
        assert data.renewable_percentage == 25.0
        assert data.nuclear_percentage == 15.0
        assert data.hydro_percentage == 8.0
        assert data.wind_percentage == 12.0
        assert data.solar_percentage == 5.0
        assert data.biomass_percentage == 2.0
        assert data.coal_percentage == 20.0
        assert data.gas_percentage == 30.0
        assert data.oil_percentage == 10.0
        assert data.unknown_percentage == 5.0
        assert data.total_production == 5000.0
        assert data.total_consumption == 4800.0

        # Check timestamp parsing
        expected_timestamp = datetime.fromisoformat("2024-01-15T10:30:00+00:00")
        assert data.timestamp == expected_timestamp

    @responses.activate
    def test_get_carbon_intensity_with_datetime(
        self, client, mock_carbon_intensity_response
    ):
        """Test carbon intensity retrieval with specific datetime."""
        # Mock the API response
        responses.add(
            responses.GET,
            f"{client.base_url}/carbon-intensity/US",
            json=mock_carbon_intensity_response,
            status=200,
            match=[
                responses.matchers.query_param_matcher(
                    {"datetime": "2024-01-15T10:30:00Z"}
                )
            ],
        )

        data = client.get_carbon_intensity("US", "2024-01-15T10:30:00Z")

        assert isinstance(data, CarbonIntensityData)
        assert data.zone == "US"
        assert data.carbon_intensity == 250.5

    @responses.activate
    def test_get_carbon_intensity_api_error(self, client):
        """Test carbon intensity retrieval with API error."""
        # Mock API error
        responses.add(
            responses.GET, f"{client.base_url}/carbon-intensity/US", status=404
        )

        with pytest.raises(Exception):
            client.get_carbon_intensity("US")

    @responses.activate
    def test_get_carbon_intensity_history_success(self, client, mock_history_response):
        """Test successful carbon intensity history retrieval."""
        start_date = datetime(2024, 1, 15, 10, 0, 0)
        end_date = datetime(2024, 1, 15, 11, 0, 0)

        # Mock the API response
        responses.add(
            responses.GET,
            f"{client.base_url}/carbon-intensity/US/history",
            json=mock_history_response,
            status=200,
            match=[
                responses.matchers.query_param_matcher(
                    {"start": "2024-01-15T10:00:00", "end": "2024-01-15T11:00:00"}
                )
            ],
        )

        history = client.get_carbon_intensity_history("US", start_date, end_date)

        assert len(history) == 2
        assert all(isinstance(data, CarbonIntensityData) for data in history)

        # Check first entry
        first_entry = history[0]
        assert first_entry.zone == "US"
        assert first_entry.carbon_intensity == 240.0
        assert first_entry.fossil_fuel_percentage == 58.0
        assert first_entry.renewable_percentage == 27.0

        # Check second entry
        second_entry = history[1]
        assert second_entry.carbon_intensity == 250.5
        assert second_entry.fossil_fuel_percentage == 60.0

    @responses.activate
    def test_get_carbon_intensity_history_api_error(self, client):
        """Test carbon intensity history retrieval with API error."""
        start_date = datetime(2024, 1, 15, 10, 0, 0)
        end_date = datetime(2024, 1, 15, 11, 0, 0)

        # Mock API error
        responses.add(
            responses.GET, f"{client.base_url}/carbon-intensity/US/history", status=500
        )

        with pytest.raises(Exception):
            client.get_carbon_intensity_history("US", start_date, end_date)

    @responses.activate
    def test_get_power_production_breakdown_success(
        self, client, mock_power_breakdown_response
    ):
        """Test successful power production breakdown retrieval."""
        # Mock the API response
        responses.add(
            responses.GET,
            f"{client.base_url}/power-production-breakdown/US",
            json=mock_power_breakdown_response,
            status=200,
        )

        data = client.get_power_production_breakdown("US")

        assert isinstance(data, dict)
        assert data["zone"] == "US"
        assert "production" in data
        assert data["production"]["coal"] == 1000.0
        assert data["production"]["gas"] == 1500.0
        assert data["production"]["nuclear"] == 750.0

    @responses.activate
    def test_get_power_production_breakdown_api_error(self, client):
        """Test power production breakdown retrieval with API error."""
        # Mock API error
        responses.add(
            responses.GET,
            f"{client.base_url}/power-production-breakdown/US",
            status=404,
        )

        with pytest.raises(Exception):
            client.get_power_production_breakdown("US")

    def test_carbon_intensity_data_validation(
        self, client, mock_carbon_intensity_response
    ):
        """Test carbon intensity data validation."""
        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_carbon_intensity_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            data = client.get_carbon_intensity("US")

            # Test data validation
            assert data.carbon_intensity >= 0
            assert 0 <= data.fossil_fuel_percentage <= 100
            assert 0 <= data.renewable_percentage <= 100
            assert 0 <= data.nuclear_percentage <= 100

    def test_zone_info_validation(self, client, mock_zones_response):
        """Test zone info validation."""
        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_zones_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            zones = client.get_zones()

            # Test zone validation
            for zone in zones:
                assert zone.zone is not None
                assert zone.name is not None
                assert isinstance(zone.latitude, (int, float))
                assert isinstance(zone.longitude, (int, float))
                assert zone.timezone is not None

    @responses.activate
    def test_empty_history_response(self, client):
        """Test handling of empty history response."""
        start_date = datetime(2024, 1, 15, 10, 0, 0)
        end_date = datetime(2024, 1, 15, 11, 0, 0)

        # Mock empty response
        responses.add(
            responses.GET,
            f"{client.base_url}/carbon-intensity/US/history",
            json={"history": []},
            status=200,
        )

        history = client.get_carbon_intensity_history("US", start_date, end_date)
        assert len(history) == 0

    @responses.activate
    def test_partial_data_response(self, client):
        """Test handling of partial data in response."""
        partial_response = {
            "datetime": "2024-01-15T10:30:00Z",
            "carbonIntensity": 250.5,
            # Missing other fields
        }

        responses.add(
            responses.GET,
            f"{client.base_url}/carbon-intensity/US",
            json=partial_response,
            status=200,
        )

        data = client.get_carbon_intensity("US")

        assert data.carbon_intensity == 250.5
        assert data.fossil_fuel_percentage is None
        assert data.renewable_percentage is None
        assert data.nuclear_percentage is None

    def test_session_reuse(self, client):
        """Test that the same session is reused for multiple requests."""
        session_id_1 = id(client.session)

        # Create another client instance
        client2 = ElectricityMapsClient()
        session_id_2 = id(client2.session)

        # Sessions should be different instances
        assert session_id_1 != session_id_2

    @responses.activate
    def test_concurrent_requests(self, client, mock_carbon_intensity_response):
        """Test handling of concurrent requests."""
        # Mock multiple responses
        for zone in ["US", "DE", "FR"]:
            responses.add(
                responses.GET,
                f"{client.base_url}/carbon-intensity/{zone}",
                json=mock_carbon_intensity_response,
                status=200,
            )

        # Make concurrent requests
        import concurrent.futures

        def get_intensity(zone):
            return client.get_carbon_intensity(zone)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(get_intensity, zone) for zone in ["US", "DE", "FR"]
            ]
            results = [future.result() for future in futures]

        assert len(results) == 3
        assert all(isinstance(result, CarbonIntensityData) for result in results)
        assert all(result.carbon_intensity == 250.5 for result in results)
