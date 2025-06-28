"""Streamlit dashboard for Carbon Pulse."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="Carbon Pulse Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .carbon-low { color: #2ca02c; }
    .carbon-medium { color: #ff7f0e; }
    .carbon-high { color: #d62728; }
</style>
""",
    unsafe_allow_html=True,
)

# API configuration
API_BASE_URL = "http://localhost:8000"


def get_carbon_intensity_color(intensity: float) -> str:
    """Get color class based on carbon intensity."""
    if intensity < 200:
        return "carbon-low"
    elif intensity < 400:
        return "carbon-medium"
    else:
        return "carbon-high"


def fetch_api_data(endpoint: str) -> Optional[Dict]:
    """Fetch data from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Failed to fetch data from API: {e}")
        return None


def main():
    """Main dashboard function."""

    # Header
    st.markdown(
        '<h1 class="main-header">🌱 Carbon Pulse Dashboard</h1>', unsafe_allow_html=True
    )

    # Sidebar
    st.sidebar.title("Settings")

    # Check API health
    health_data = fetch_api_data("/health")
    if health_data and health_data.get("success"):
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.error(
            "Cannot connect to Carbon Pulse API. Please ensure the API is running."
        )
        return

    # Get zones
    zones_data = fetch_api_data("/zones")
    if not zones_data or not zones_data.get("success"):
        st.error("Failed to load zones")
        return

    zones = zones_data["data"]["zones"]
    zone_names = [zone["name"] for zone in zones]
    zone_codes = [zone["zone"] for zone in zones]

    # Zone selection
    selected_zone_name = st.sidebar.selectbox(
        "Select Zone",
        zone_names,
        index=zone_names.index("United States") if "United States" in zone_names else 0,
    )
    selected_zone_code = zone_codes[zone_names.index(selected_zone_name)]

    # Time range selection
    st.sidebar.subheader("Time Range")
    time_range = st.sidebar.selectbox(
        "Select Time Range", ["Last 24 hours", "Last 7 days", "Last 30 days", "Custom"]
    )

    if time_range == "Custom":
        start_date = st.sidebar.date_input(
            "Start Date", datetime.now() - timedelta(days=7)
        )
        end_date = st.sidebar.date_input("End Date", datetime.now())
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
    else:
        end_datetime = datetime.now()
        if time_range == "Last 24 hours":
            start_datetime = end_datetime - timedelta(days=1)
        elif time_range == "Last 7 days":
            start_datetime = end_datetime - timedelta(days=7)
        else:  # Last 30 days
            start_datetime = end_datetime - timedelta(days=30)

    # Main content
    col1, col2, col3 = st.columns(3)

    # Current carbon intensity
    current_data = fetch_api_data(f"/zones/{selected_zone_code}/carbon-intensity")
    if current_data and current_data.get("success"):
        current_intensity = current_data["data"]["carbon_intensity"]["carbon_intensity"]
        color_class = get_carbon_intensity_color(current_intensity)

        with col1:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>Current Carbon Intensity</h3>
                <p class="{color_class}" style="font-size: 2rem; font-weight: bold;">
                    {current_intensity:.1f} gCO₂eq/kWh
                </p>
                <p>Last updated: {current_data["data"]["carbon_intensity"]["timestamp"]}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Average carbon intensity
    avg_data = fetch_api_data(
        f"/zones/{selected_zone_code}/carbon-intensity/average?hours=24"
    )
    if avg_data and avg_data.get("success"):
        avg_intensity = avg_data["data"]["average_carbon_intensity"]
        color_class = get_carbon_intensity_color(avg_intensity)

        with col2:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>24h Average</h3>
                <p class="{color_class}" style="font-size: 2rem; font-weight: bold;">
                    {avg_intensity:.1f} gCO₂eq/kWh
                </p>
                <p>Last 24 hours</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Energy mix (if available)
    if current_data and current_data.get("success"):
        energy_data = current_data["data"]["carbon_intensity"]
        renewable_pct = energy_data.get("renewable_percentage", 0)
        fossil_pct = energy_data.get("fossil_fuel_percentage", 0)
        nuclear_pct = energy_data.get("nuclear_percentage", 0)

        with col3:
            st.markdown(
                f"""
            <div class="metric-card">
                <h3>Energy Mix</h3>
                <p style="color: #2ca02c; font-size: 1.5rem; font-weight: bold;">
                    {renewable_pct:.1f}% Renewable
                </p>
                <p style="color: #d62728; font-size: 1.2rem;">
                    {fossil_pct:.1f}% Fossil
                </p>
                <p style="color: #ff7f0e; font-size: 1.2rem;">
                    {nuclear_pct:.1f}% Nuclear
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Historical data chart
    st.subheader("Historical Carbon Intensity")

    history_data = fetch_api_data(
        f"/zones/{selected_zone_code}/carbon-intensity/history"
        f"?start_date={start_datetime.isoformat()}&end_date={end_datetime.isoformat()}"
    )

    if history_data and history_data.get("success"):
        history = history_data["data"]["history"]

        if history:
            # Create DataFrame
            df = pd.DataFrame(history)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

            # Create chart
            fig = px.line(
                df,
                x="timestamp",
                y="carbon_intensity",
                title=f"Carbon Intensity Over Time - {selected_zone_name}",
                labels={
                    "carbon_intensity": "Carbon Intensity (gCO₂eq/kWh)",
                    "timestamp": "Time",
                },
            )

            # Add color zones
            fig.add_hline(
                y=200,
                line_dash="dash",
                line_color="green",
                annotation_text="Low Carbon",
            )
            fig.add_hline(
                y=400, line_dash="dash", line_color="red", annotation_text="High Carbon"
            )

            fig.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Time",
                yaxis_title="Carbon Intensity (gCO₂eq/kWh)",
            )

            st.plotly_chart(fig, use_container_width=True)

            # Energy mix breakdown over time
            st.subheader("Energy Mix Breakdown")

            # Prepare energy mix data
            energy_columns = [
                "renewable_percentage",
                "fossil_fuel_percentage",
                "nuclear_percentage",
                "hydro_percentage",
                "wind_percentage",
                "solar_percentage",
            ]

            energy_df = df[["timestamp"] + energy_columns].copy()
            energy_df = energy_df.melt(
                id_vars=["timestamp"],
                value_vars=energy_columns,
                var_name="energy_type",
                value_name="percentage",
            )

            # Clean up energy type names
            energy_df["energy_type"] = (
                energy_df["energy_type"].str.replace("_percentage", "").str.title()
            )

            # Create stacked area chart
            fig_energy = px.area(
                energy_df,
                x="timestamp",
                y="percentage",
                color="energy_type",
                title=f"Energy Mix Over Time - {selected_zone_name}",
                labels={"percentage": "Percentage (%)", "timestamp": "Time"},
            )

            fig_energy.update_layout(
                height=400, xaxis_title="Time", yaxis_title="Percentage (%)"
            )

            st.plotly_chart(fig_energy, use_container_width=True)

        else:
            st.warning("No historical data available for the selected time range.")
    else:
        st.error("Failed to load historical data.")

    # Zone comparison
    st.subheader("Zone Comparison")

    # Get current data for top zones
    top_zones = ["US", "DE", "FR", "GB", "CA"]  # Popular zones
    comparison_data = []

    for zone_code in top_zones:
        if zone_code in zone_codes:
            zone_data = fetch_api_data(f"/zones/{zone_code}/carbon-intensity")
            if zone_data and zone_data.get("success"):
                intensity = zone_data["data"]["carbon_intensity"]["carbon_intensity"]
                zone_name = next(z["name"] for z in zones if z["zone"] == zone_code)
                comparison_data.append(
                    {"Zone": zone_name, "Carbon Intensity": intensity}
                )

    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values("Carbon Intensity")

        fig_comparison = px.bar(
            comparison_df,
            x="Zone",
            y="Carbon Intensity",
            title="Carbon Intensity Comparison",
            color="Carbon Intensity",
            color_continuous_scale="RdYlGn_r",
        )

        fig_comparison.update_layout(height=400)
        st.plotly_chart(fig_comparison, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "🌱 **Carbon Pulse** - Real-time carbon intensity monitoring. "
        "Data provided by [Electricity Maps](https://electricitymaps.com/)."
    )


if __name__ == "__main__":
    main()
