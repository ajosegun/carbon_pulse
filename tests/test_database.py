"""Tests for database layer."""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from carbon_pulse.data.database import DatabaseManager
from carbon_pulse.models import CarbonIntensityData, ZoneInfo


class TestDatabaseManager:
    """Test DatabaseManager class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
            db_path = f.name

        # Override the database URL for testing
        original_url = DatabaseManager.__init__.__defaults__

        try:
            yield db_path
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_database_initialization(self, temp_db):
        """Test database initialization."""
        with DatabaseManager() as db:
            assert db.connection is not None

            # Check if tables were created
            result = db.connection.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('zones', 'carbon_intensity')
            """).fetchall()

            table_names = [row[0] for row in result]
            assert "zones" in table_names
            assert "carbon_intensity" in table_names

    def test_insert_and_get_zone(self, temp_db):
        """Test inserting and retrieving zone data."""
        zone_info = ZoneInfo(
            zone="TEST",
            name="Test Zone",
            country="Test Country",
            latitude=0.0,
            longitude=0.0,
            timezone="UTC",
        )

        with DatabaseManager() as db:
            # Insert zone
            success = db.insert_zone(zone_info)
            assert success is True

            # Get zones
            zones = db.get_zones()
            assert len(zones) == 1
            assert zones[0].zone == "TEST"
            assert zones[0].name == "Test Zone"

    def test_insert_and_get_carbon_intensity(self, temp_db):
        """Test inserting and retrieving carbon intensity data."""
        carbon_data = CarbonIntensityData(
            zone="TEST",
            timestamp=datetime.utcnow(),
            carbon_intensity=250.0,
            renewable_percentage=30.0,
            fossil_fuel_percentage=50.0,
        )

        with DatabaseManager() as db:
            # Insert carbon intensity data
            success = db.insert_carbon_intensity(carbon_data)
            assert success is True

            # Get latest carbon intensity
            latest = db.get_latest_carbon_intensity("TEST")
            assert latest is not None
            assert latest.zone == "TEST"
            assert latest.carbon_intensity == 250.0
            assert latest.renewable_percentage == 30.0

    def test_get_carbon_intensity_history(self, temp_db):
        """Test retrieving carbon intensity history."""
        now = datetime.utcnow()

        # Create multiple data points
        data_points = [
            CarbonIntensityData(
                zone="TEST", timestamp=now - timedelta(hours=2), carbon_intensity=200.0
            ),
            CarbonIntensityData(
                zone="TEST", timestamp=now - timedelta(hours=1), carbon_intensity=250.0
            ),
            CarbonIntensityData(zone="TEST", timestamp=now, carbon_intensity=300.0),
        ]

        with DatabaseManager() as db:
            # Insert data points
            for data in data_points:
                db.insert_carbon_intensity(data)

            # Get history
            start_time = now - timedelta(hours=3)
            end_time = now + timedelta(hours=1)
            history = db.get_carbon_intensity_history("TEST", start_time, end_time)

            assert len(history) == 3
            assert history[0].carbon_intensity == 200.0
            assert history[1].carbon_intensity == 250.0
            assert history[2].carbon_intensity == 300.0

    def test_get_average_carbon_intensity(self, temp_db):
        """Test calculating average carbon intensity."""
        now = datetime.utcnow()

        # Create data points with known average
        data_points = [
            CarbonIntensityData(
                zone="TEST", timestamp=now - timedelta(hours=2), carbon_intensity=100.0
            ),
            CarbonIntensityData(
                zone="TEST", timestamp=now - timedelta(hours=1), carbon_intensity=200.0
            ),
            CarbonIntensityData(zone="TEST", timestamp=now, carbon_intensity=300.0),
        ]

        with DatabaseManager() as db:
            # Insert data points
            for data in data_points:
                db.insert_carbon_intensity(data)

            # Get average (should be 200.0)
            avg = db.get_average_carbon_intensity("TEST", hours=3)
            assert avg == 200.0

    def test_duplicate_insert_handling(self, temp_db):
        """Test handling of duplicate inserts."""
        carbon_data = CarbonIntensityData(
            zone="TEST", timestamp=datetime.utcnow(), carbon_intensity=250.0
        )

        with DatabaseManager() as db:
            # Insert same data twice
            success1 = db.insert_carbon_intensity(carbon_data)
            success2 = db.insert_carbon_intensity(carbon_data)

            assert success1 is True
            assert success2 is True  # Should use INSERT OR REPLACE

            # Should only have one record
            history = db.get_carbon_intensity_history(
                "TEST",
                carbon_data.timestamp - timedelta(minutes=1),
                carbon_data.timestamp + timedelta(minutes=1),
            )
            assert len(history) == 1
