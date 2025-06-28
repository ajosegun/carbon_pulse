#!/usr/bin/env python3
"""Minimal test script for ElectricityMapsClient."""

import sys
import os
import requests
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Mock the config module to avoid dependency issues
class MockSettings:
    electricity_maps_api_key = None
    electricity_maps_base_url = "https://api.electricitymap.org/v3"


# Mock the config module
sys.modules["carbon_pulse.config"] = type(
    "MockConfig", (), {"settings": MockSettings()}
)()


# Mock the logger module
class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")

    def success(self, msg):
        print(f"SUCCESS: {msg}")

    def error(self, msg):
        print(f"ERROR: {msg}")

    def warning(self, msg):
        print(f"WARNING: {msg}")

    def debug(self, msg):
        print(f"DEBUG: {msg}")

    def trace(self, msg):
        print(f"TRACE: {msg}")


sys.modules["carbon_pulse.logger"] = type("MockLogger", (), {"logger": MockLogger()})()

# Now import the client
from carbon_pulse.data.electricity_maps import ElectricityMapsClient


def test_basic_functionality():
    """Test basic functionality of the ElectricityMapsClient."""
    print("🧪 Testing Electricity Maps Client (Minimal)")
    print("=" * 50)

    client = ElectricityMapsClient()
    print(f"✅ Client initialized with base URL: {client.base_url}")

    try:
        # Test 1: Get zones
        print("\n📋 Testing zones retrieval...")
        zones = client.get_zones()
        print(f"✅ Retrieved {len(zones)} zones")

        # Show first few zones
        for zone in zones[:3]:
            print(f"  - {zone.zone}: {zone.name} ({zone.country})")

        # Test 2: Get carbon intensity for a specific zone
        print("\n⚡ Testing carbon intensity retrieval...")
        test_zone = "US"  # United States

        carbon_data = client.get_carbon_intensity(test_zone)
        print(f"✅ Retrieved carbon intensity for {test_zone}")
        print(f"  - Carbon Intensity: {carbon_data.carbon_intensity} gCO2eq/kWh")
        print(f"  - Renewable: {carbon_data.renewable_percentage}%")
        print(f"  - Fossil Fuel: {carbon_data.fossil_fuel_percentage}%")
        print(f"  - Nuclear: {carbon_data.nuclear_percentage}%")
        print(f"  - Timestamp: {carbon_data.timestamp}")

        # Test 3: Get carbon intensity history
        print("\n📈 Testing carbon intensity history...")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=1)

        history = client.get_carbon_intensity_history(test_zone, start_date, end_date)
        print(f"✅ Retrieved {len(history)} historical data points")

        if history:
            print(
                f"  - First entry: {history[0].carbon_intensity} gCO2eq/kWh at {history[0].timestamp}"
            )
            print(
                f"  - Last entry: {history[-1].carbon_intensity} gCO2eq/kWh at {history[-1].timestamp}"
            )

        # Test 4: Get power production breakdown
        print("\n🏭 Testing power production breakdown...")
        breakdown = client.get_power_production_breakdown(test_zone)
        print(f"✅ Retrieved power production breakdown for {test_zone}")

        if "production" in breakdown:
            production = breakdown["production"]
            print("  - Production breakdown:")
            for fuel_type, amount in production.items():
                if amount and amount > 0:
                    print(f"    * {fuel_type}: {amount} MW")

        print("\n🎉 All API tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 This might be due to:")
        print("   - Network connectivity issues")
        print("   - API service unavailability")
        print("   - Rate limiting (try with API key)")
        return False


def test_error_handling():
    """Test error handling with invalid requests."""
    print("\n🚨 Testing error handling...")

    client = ElectricityMapsClient()

    try:
        # Test with invalid zone
        print("Testing with invalid zone 'INVALID_ZONE'...")
        carbon_data = client.get_carbon_intensity("INVALID_ZONE")
        print("⚠️  Unexpected success with invalid zone")
    except Exception as e:
        print(f"✅ Properly handled invalid zone error: {type(e).__name__}")

    try:
        # Test with invalid datetime
        print("Testing with invalid datetime...")
        carbon_data = client.get_carbon_intensity("US", "invalid-datetime")
        print("⚠️  Unexpected success with invalid datetime")
    except Exception as e:
        print(f"✅ Properly handled invalid datetime error: {type(e).__name__}")


def main():
    """Main test function."""
    print("🧪 Electricity Maps Client Minimal Test Suite")
    print("=" * 50)

    # Test 1: Basic functionality
    success = test_basic_functionality()

    # Test 2: Error handling
    test_error_handling()

    if success:
        print("\n🎉 All tests completed!")
        print("\nNext steps:")
        print("1. Install dependencies: uv sync --dev")
        print("2. Run full test suite: uv run pytest tests/test_electricity_maps.py -v")
        print("3. Use the client in your application")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
