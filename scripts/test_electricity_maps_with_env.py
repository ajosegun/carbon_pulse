#!/usr/bin/env python3
"""Test script for ElectricityMapsClient with proper environment loading."""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Now import the actual modules (not mocked)
from carbon_pulse.data.electricity_maps import ElectricityMapsClient
from carbon_pulse.logger import logger


def test_with_api_key():
    """Test ElectricityMapsClient with API key from environment."""
    print("🧪 Testing Electricity Maps Client with API Key")
    print("=" * 50)

    # Check if API key is loaded
    api_key = os.getenv("ELECTRICITY_MAPS_API_KEY")
    if not api_key:
        print("❌ No API key found in environment variables")
        print(
            "💡 Make sure your .env file contains: ELECTRICITY_MAPS_API_KEY=your_key_here"
        )
        return False

    print(
        f"✅ API key found: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}"
    )

    client = ElectricityMapsClient()
    print(f"✅ Client initialized with base URL: {client.base_url}")

    try:
        # Test 1: Get zones (should work without API key)
        print("\n📋 Testing zones retrieval...")
        zones = client.get_zones()
        print(f"✅ Retrieved {len(zones)} zones")

        # Show first few zones
        for zone in zones[:3]:
            print(f"  - {zone.zone}: {zone.name} ({zone.country})")

        # Test 2: Get carbon intensity for a specific zone (requires API key)
        print("\n⚡ Testing carbon intensity retrieval...")
        test_zone = "FR"  # France

        carbon_data = client.get_latest_carbon_intensity(test_zone)
        print(f"✅ Retrieved latest carbon intensity for {test_zone}")
        print(f"  - Carbon Intensity: {carbon_data.carbon_intensity} gCO2eq/kWh")
        print(f"  - Renewable: {carbon_data.renewable_percentage}%")
        print(f"  - Fossil Fuel: {carbon_data.fossil_fuel_percentage}%")
        print(f"  - Nuclear: {carbon_data.nuclear_percentage}%")
        print(f"  - Timestamp: {carbon_data.timestamp}")

        # Test 3: Get carbon intensity history (requires API key)
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

        # Test 4: Get power production breakdown (requires API key)
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
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - API service unavailability")
        print("   - Rate limiting")
        return False


def test_multiple_zones():
    """Test carbon intensity for multiple zones."""
    print("\n🌍 Testing multiple zones...")

    client = ElectricityMapsClient()
    test_zones = ["FR", "FR-COR"]  # France, Corsica

    for zone in test_zones:
        try:
            carbon_data = client.get_latest_carbon_intensity(zone)
            print(
                f"✅ {zone}: {carbon_data.carbon_intensity} gCO2eq/kWh ({carbon_data.renewable_percentage}% renewable)"
            )
        except Exception as e:
            print(f"❌ {zone}: Failed - {e}")


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
    print("🧪 Electricity Maps Client Test Suite (with API Key)")
    print("=" * 50)

    # Test 1: Basic functionality with API key
    success = test_with_api_key()

    if success:
        # Test 2: Multiple zones
        test_multiple_zones()

        # Test 3: Error handling
        test_error_handling()

        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Run full test suite: uv run pytest tests/test_electricity_maps.py -v")
        print("2. Start the API server: uv run python -m carbon_pulse.api.main")
        print(
            "3. Start the dashboard: uv run streamlit run carbon_pulse/dashboard/main.py"
        )
    else:
        print("\n⚠️  Tests failed. Check the logs above for details.")
        print("\nTroubleshooting:")
        print("1. Verify your API key is correct")
        print("2. Check your .env file format: ELECTRICITY_MAPS_API_KEY=your_key_here")
        print("3. Ensure you have network connectivity")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
