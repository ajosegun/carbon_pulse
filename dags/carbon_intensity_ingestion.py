"""Airflow DAG for carbon intensity data ingestion."""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carbon_pulse.data.electricity_maps import ElectricityMapsClient
from carbon_pulse.data.database import DatabaseManager
from carbon_pulse.logger import logger
from carbon_pulse.models import CarbonIntensityData, ZoneInfo


default_args = {
    "owner": "carbon-pulse",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "carbon_intensity_ingestion",
    default_args=default_args,
    description="Ingest carbon intensity data from Electricity Maps API",
    schedule_interval="@hourly",
    catchup=False,
    tags=["carbon-intensity", "data-ingestion"],
)


def fetch_and_store_zones():
    """Fetch zones from Electricity Maps API and store in database."""
    try:
        client = ElectricityMapsClient()
        zones = client.get_zones()

        with DatabaseManager() as db:
            for zone in zones:
                db.insert_zone(zone)

        logger.info(f"Successfully fetched and stored {len(zones)} zones")
        return True
    except Exception as e:
        logger.error(f"Error fetching zones: {e}")
        raise


def fetch_and_store_carbon_intensity():
    """Fetch carbon intensity data for major zones and store in database."""
    major_zones = [
        "US",
        "DE",
        "FR",
        "GB",
        "CA",
        "AU",
        "JP",
        "CN",
        "IN",
        "BR",
        "IT",
        "ES",
        "NL",
        "SE",
        "NO",
        "DK",
        "FI",
        "CH",
        "AT",
        "BE",
    ]

    try:
        client = ElectricityMapsClient()

        with DatabaseManager() as db:
            for zone in major_zones:
                try:
                    # Fetch current carbon intensity
                    carbon_data = client.get_carbon_intensity(zone)
                    db.insert_carbon_intensity(carbon_data)
                    logger.info(f"Successfully stored carbon intensity data for {zone}")
                except Exception as e:
                    logger.error(f"Error fetching data for zone {zone}: {e}")
                    continue

        logger.info("Carbon intensity data ingestion completed")
        return True
    except Exception as e:
        logger.error(f"Error in carbon intensity ingestion: {e}")
        raise


def validate_data():
    """Validate ingested data using Great Expectations."""
    try:
        # This would integrate with Great Expectations
        # For now, we'll just check if data exists
        with DatabaseManager() as db:
            zones = db.get_zones()
            if not zones:
                raise Exception("No zones found in database")

            # Check if we have recent carbon intensity data
            recent_data = db.get_latest_carbon_intensity("US")
            if not recent_data:
                raise Exception("No recent carbon intensity data found")

        logger.info("Data validation passed")
        return True
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise


# Define tasks
fetch_zones_task = PythonOperator(
    task_id="fetch_zones",
    python_callable=fetch_and_store_zones,
    dag=dag,
)

fetch_carbon_intensity_task = PythonOperator(
    task_id="fetch_carbon_intensity",
    python_callable=fetch_and_store_carbon_intensity,
    dag=dag,
)

validate_data_task = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
    dag=dag,
)

# Define task dependencies
fetch_zones_task >> fetch_carbon_intensity_task >> validate_data_task
