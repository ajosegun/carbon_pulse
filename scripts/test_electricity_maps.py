#!/usr/bin/env python3
"""Test script for ElectricityMapsClient."""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carbon_pulse.data.electricity_maps import ElectricityMapsClient
from carbon_pulse.logger import logger


def test_real_api_calls():
    """Test real API calls to Electricity Maps (if API key is available)."""
    logger.info("🌐 Testing Electricity Maps API Client")
    logger.info("=" * 50)

    client = ElectricityMapsClient()

    try:
        # Test 1: Get zones
        logger.info("📋 Testing zones retrieval...")
        zones = client.get_zones()
        logger.success(f"✅ Retrieved {len(zones)} zones")

        # Show first few zones
        for zone in zones[:5]:
            logger.info(f"  - {zone.zone}: {zone.name} ({zone.country})")

        # Test 2: Get carbon intensity for a specific zone
        logger.info("\n⚡ Testing carbon intensity retrieval...")
        test_zone = "US"  # United States

        carbon_data = client.get_carbon_intensity(test_zone)
        logger.success(f"✅ Retrieved carbon intensity for {test_zone}")
        logger.info(f"  - Carbon Intensity: {carbon_data.carbon_intensity} gCO2eq/kWh")
        logger.info(f"  - Renewable: {carbon_data.renewable_percentage}%")
        logger.info(f"  - Fossil Fuel: {carbon_data.fossil_fuel_percentage}%")
        logger.info(f"  - Nuclear: {carbon_data.nuclear_percentage}%")
        logger.info(f"  - Timestamp: {carbon_data.timestamp}")

        # Test 3: Get carbon intensity history
        logger.info("\n📈 Testing carbon intensity history...")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=2)

        history = client.get_carbon_intensity_history(test_zone, start_date, end_date)
        logger.success(f"✅ Retrieved {len(history)} historical data points")

        if history:
            logger.info(
                f"  - First entry: {history[0].carbon_intensity} gCO2eq/kWh at {history[0].timestamp}"
            )
            logger.info(
                f"  - Last entry: {history[-1].carbon_intensity} gCO2eq/kWh at {history[-1].timestamp}"
            )

        # Test 4: Get power production breakdown
        logger.info("\n🏭 Testing power production breakdown...")
        breakdown = client.get_power_production_breakdown(test_zone)
        logger.success(f"✅ Retrieved power production breakdown for {test_zone}")

        if "production" in breakdown:
            production = breakdown["production"]
            logger.info("  - Production breakdown:")
            for fuel_type, amount in production.items():
                if amount and amount > 0:
                    logger.info(f"    * {fuel_type}: {amount} MW")

        logger.success("\n🎉 All API tests completed successfully!")

    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        logger.info("💡 This might be due to:")
        logger.info("   - Missing API key (optional, but provides higher rate limits)")
        logger.info("   - Network connectivity issues")
        logger.info("   - API service unavailability")
        return False

    return True


def test_without_api_key():
    """Test client behavior without API key."""
    logger.info("\n🔑 Testing client without API key...")

    # Temporarily remove API key
    original_api_key = os.environ.get("ELECTRICITY_MAPS_API_KEY")
    if original_api_key:
        del os.environ["ELECTRICITY_MAPS_API_KEY"]

    try:
        client = ElectricityMapsClient()
        logger.info("✅ Client initialized without API key")

        # Try to get zones (should work without API key)
        zones = client.get_zones()
        logger.success(f"✅ Retrieved {len(zones)} zones without API key")

    except Exception as e:
        logger.error(f"❌ Test without API key failed: {e}")
    finally:
        # Restore API key if it existed
        if original_api_key:
            os.environ["ELECTRICITY_MAPS_API_KEY"] = original_api_key


def test_error_handling():
    """Test error handling with invalid requests."""
    logger.info("\n🚨 Testing error handling...")

    client = ElectricityMapsClient()

    try:
        # Test with invalid zone
        logger.info("Testing with invalid zone 'INVALID_ZONE'...")
        carbon_data = client.get_carbon_intensity("INVALID_ZONE")
        logger.warning("⚠️  Unexpected success with invalid zone")
    except Exception as e:
        logger.success(f"✅ Properly handled invalid zone error: {type(e).__name__}")

    try:
        # Test with invalid datetime
        logger.info("Testing with invalid datetime...")
        carbon_data = client.get_carbon_intensity("US", "invalid-datetime")
        logger.warning("⚠️  Unexpected success with invalid datetime")
    except Exception as e:
        logger.success(
            f"✅ Properly handled invalid datetime error: {type(e).__name__}"
        )


def main():
    """Main test function."""
    logger.info("🧪 Electricity Maps Client Test Suite")
    logger.info("=" * 50)

    # Test 1: Real API calls
    success = test_real_api_calls()

    # Test 2: Without API key
    test_without_api_key()

    # Test 3: Error handling
    test_error_handling()

    if success:
        logger.success("\n🎉 All tests completed!")
        logger.info("\nNext steps:")
        logger.info(
            "1. Run pytest for comprehensive test suite: uv run pytest tests/test_electricity_maps.py -v"
        )
        logger.info("2. Check the logs for detailed information")
        logger.info("3. Use the client in your application")
    else:
        logger.warning("\n⚠️  Some tests failed. Check the logs above for details.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
