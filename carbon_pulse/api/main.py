"""FastAPI application for Carbon Pulse."""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from carbon_pulse.config import settings
from carbon_pulse.data.database import DatabaseManager
from carbon_pulse.data.electricity_maps import ElectricityMapsClient
from carbon_pulse.logger import logger
from carbon_pulse.models import APIResponse, CarbonIntensityData, ZoneInfo

# Prometheus metrics
REQUEST_COUNT = Counter(
    "carbon_pulse_requests_total", "Total requests", ["endpoint", "method"]
)
REQUEST_LATENCY = Histogram(
    "carbon_pulse_request_duration_seconds", "Request latency", ["endpoint"]
)

# Initialize FastAPI app
app = FastAPI(
    title="Carbon Pulse API",
    description="Real-time carbon intensity monitoring API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
electricity_maps_client = ElectricityMapsClient()


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint."""
    REQUEST_COUNT.labels(endpoint="/", method="GET").inc()
    logger.info("Root endpoint accessed")
    return APIResponse(
        success=True,
        message="Carbon Pulse API is running",
        data={"version": "0.1.0", "status": "healthy"},
    )


@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint."""
    REQUEST_COUNT.labels(endpoint="/health", method="GET").inc()
    try:
        # Test database connection
        with DatabaseManager() as db:
            zones = db.get_zones()

        logger.info("Health check passed - database connected")
        return APIResponse(
            success=True,
            message="Service is healthy",
            data={"database": "connected", "zones_count": len(zones)},
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/zones", response_model=APIResponse)
async def get_zones():
    """Get all available zones."""
    REQUEST_COUNT.labels(endpoint="/zones", method="GET").inc()

    with REQUEST_LATENCY.labels(endpoint="/zones").time():
        try:
            with DatabaseManager() as db:
                zones = db.get_zones()

            logger.info(f"Retrieved {len(zones)} zones")
            return APIResponse(
                success=True,
                data={"zones": [zone.dict() for zone in zones]},
                message=f"Retrieved {len(zones)} zones",
            )
        except Exception as e:
            logger.error(f"Failed to get zones: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve zones")


@app.get("/zones/{zone}/carbon-intensity", response_model=APIResponse)
async def get_carbon_intensity(
    zone: str,
    datetime_str: Optional[str] = Query(None, description="ISO datetime string"),
):
    """Get carbon intensity for a specific zone."""
    REQUEST_COUNT.labels(endpoint="/zones/{zone}/carbon-intensity", method="GET").inc()

    with REQUEST_LATENCY.labels(endpoint="/zones/{zone}/carbon-intensity").time():
        try:
            # First try to get from database
            with DatabaseManager() as db:
                if datetime_str:
                    # Parse datetime and get specific time
                    dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                    end_dt = dt + timedelta(hours=1)
                    history = db.get_carbon_intensity_history(zone, dt, end_dt)
                    if history:
                        data = history[0]
                    else:
                        # Fetch from API if not in database
                        data = electricity_maps_client.get_carbon_intensity(
                            zone, datetime_str
                        )
                        db.insert_carbon_intensity(data)
                else:
                    # Get latest from database
                    data = db.get_latest_carbon_intensity(zone)
                    if not data:
                        # Fetch from API if not in database
                        data = electricity_maps_client.get_carbon_intensity(zone)
                        db.insert_carbon_intensity(data)

            logger.info(
                f"Retrieved carbon intensity for zone {zone}: {data.carbon_intensity} gCO2eq/kWh"
            )
            return APIResponse(
                success=True,
                data={"carbon_intensity": data.dict()},
                message=f"Carbon intensity data for {zone}",
            )
        except Exception as e:
            logger.error(f"Failed to get carbon intensity for zone {zone}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve carbon intensity for {zone}",
            )


@app.get("/zones/{zone}/carbon-intensity/history", response_model=APIResponse)
async def get_carbon_intensity_history(
    zone: str,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
):
    """Get carbon intensity history for a zone."""
    REQUEST_COUNT.labels(
        endpoint="/zones/{zone}/carbon-intensity/history", method="GET"
    ).inc()

    with REQUEST_LATENCY.labels(
        endpoint="/zones/{zone}/carbon-intensity/history"
    ).time():
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            with DatabaseManager() as db:
                history = db.get_carbon_intensity_history(zone, start_dt, end_dt)

            logger.info(
                f"Retrieved {len(history)} historical data points for zone {zone}"
            )
            return APIResponse(
                success=True,
                data={"history": [data.dict() for data in history]},
                message=f"Carbon intensity history for {zone}",
            )
        except Exception as e:
            logger.error(f"Failed to get carbon intensity history for zone {zone}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to retrieve history for {zone}"
            )


@app.get("/zones/{zone}/carbon-intensity/average", response_model=APIResponse)
async def get_average_carbon_intensity(
    zone: str, hours: int = Query(24, description="Number of hours to average")
):
    """Get average carbon intensity for the last N hours."""
    REQUEST_COUNT.labels(
        endpoint="/zones/{zone}/carbon-intensity/average", method="GET"
    ).inc()

    with REQUEST_LATENCY.labels(
        endpoint="/zones/{zone}/carbon-intensity/average"
    ).time():
        try:
            with DatabaseManager() as db:
                avg_intensity = db.get_average_carbon_intensity(zone, hours)

            if avg_intensity is None:
                logger.warning(
                    f"No data available for average calculation for zone {zone}"
                )
                raise HTTPException(
                    status_code=404, detail=f"No data available for {zone}"
                )

            logger.info(
                f"Calculated average carbon intensity for zone {zone} over {hours} hours: {avg_intensity:.2f} gCO2eq/kWh"
            )
            return APIResponse(
                success=True,
                data={
                    "zone": zone,
                    "average_carbon_intensity": avg_intensity,
                    "hours": hours,
                },
                message=f"Average carbon intensity for {zone} over {hours} hours",
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get average carbon intensity for zone {zone}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to calculate average for {zone}"
            )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    REQUEST_COUNT.labels(endpoint="/metrics", method="GET").inc()
    logger.debug("Metrics endpoint accessed")
    return generate_latest()


def main():
    """Run the FastAPI application."""
    import uvicorn

    logger.info(f"Starting Carbon Pulse API on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "carbon_pulse.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )


if __name__ == "__main__":
    main()
