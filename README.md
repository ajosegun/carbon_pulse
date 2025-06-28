# 🌱 Carbon Pulse

A modular, observable, production-grade pipeline and dashboard to monitor real-time carbon intensity data from the Electricity Maps API.

## 🎯 Overview

Carbon Pulse provides real-time monitoring of carbon intensity across different geographic zones, helping users understand the environmental impact of electricity generation. The system includes:

- **Real-time data ingestion** from Electricity Maps API
- **Data validation** using Great Expectations
- **Data transformation** with dbt
- **REST API** built with FastAPI
- **Interactive dashboard** built with Streamlit
- **Monitoring** with Prometheus and Grafana
- **CI/CD** with GitHub Actions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Electricity   │    │   Apache        │    │   DuckDB        │
│   Maps API      │───▶│   Airflow       │───▶│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Great         │    │   dbt           │
                       │   Expectations  │    │   Models        │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   FastAPI       │    │   Streamlit     │
                       │   REST API      │    │   Dashboard     │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Prometheus    │    │   Grafana       │
                       │   Metrics       │    │   Cloud         │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Electricity Maps API key (optional, for higher rate limits)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/carbon-pulse.git
   cd carbon-pulse
   ```

2. **Install dependencies**

   ```bash
   uv sync --dev
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**

   ```bash
   uv run python -c "from carbon_pulse.data.database import DatabaseManager; DatabaseManager()"
   ```

5. **Run the API**

   ```bash
   uv run carbon-pulse-api
   ```

6. **Run the dashboard**
   ```bash
   uv run carbon-pulse-dashboard
   ```

## 📊 Features

### Data Ingestion

- **Hourly data collection** from Electricity Maps API
- **Automatic zone discovery** and metadata storage
- **Robust error handling** and retry logic
- **Data validation** with Great Expectations

### Data Storage

- **DuckDB** for fast analytical queries
- **Optimized schema** with proper indexing
- **Data retention** and archival policies

### Data Transformation

- **dbt models** for clean, tested data
- **Staging, marts, and core** layers
- **Data quality tests** and documentation

### API

- **RESTful endpoints** for data access
- **Real-time carbon intensity** by zone
- **Historical data** with time range queries
- **Average calculations** and statistics
- **Prometheus metrics** for monitoring

### Dashboard

- **Real-time visualization** of carbon intensity
- **Interactive charts** with Plotly
- **Zone comparison** and analysis
- **Energy mix breakdown** over time
- **Responsive design** for all devices

### Monitoring

- **Prometheus metrics** collection
- **Grafana Cloud** integration
- **Health checks** and alerting
- **Performance monitoring**

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Database Configuration
DATABASE_URL=duckdb:///data/carbon_pulse.duckdb

# Electricity Maps API
ELECTRICITY_MAPS_API_KEY=your_api_key_here
ELECTRICITY_MAPS_BASE_URL=https://api.electricitymap.org/v3

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_CLOUD_URL=your_grafana_url
GRAFANA_CLOUD_TOKEN=your_grafana_token

# Airflow
AIRFLOW_DAGS_FOLDER=dags

# Data Validation
GE_DATA_DIR=great_expectations
```

### API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `GET /zones` - List all zones
- `GET /zones/{zone}/carbon-intensity` - Current carbon intensity
- `GET /zones/{zone}/carbon-intensity/history` - Historical data
- `GET /zones/{zone}/carbon-intensity/average` - Average over time
- `GET /metrics` - Prometheus metrics

## 🧪 Testing

### Run Tests

```bash
uv run pytest tests/ -v
```

### Run Linting

```bash
uv run black .
uv run isort .
uv run flake8 .
uv run mypy carbon_pulse/
```

### Run Data Validation

```bash
uv run dbt test
uv run great_expectations checkpoint run carbon_intensity_data_quality
```

## 📈 Monitoring

### Prometheus Metrics

The API exposes metrics at `/metrics` endpoint:

- Request count and latency
- Database connection status
- Data ingestion success/failure rates

### Grafana Dashboards

Pre-configured dashboards for:

- Carbon intensity trends
- API performance
- Data quality metrics
- System health

## 🚀 Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# Or run individually
uv run carbon-pulse-api &
uv run carbon-pulse-dashboard &
```

### Production

```bash
# Build and deploy
docker build -t carbon-pulse .
docker run -p 8000:8000 carbon-pulse
```

### Streamlit Cloud

The dashboard can be deployed to Streamlit Cloud for public access.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
uv sync --dev

# Set up pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run linting
uv run black --check .
uv run isort --check-only .
uv run flake8 .
uv run mypy carbon_pulse/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Electricity Maps](https://electricitymaps.com/) for providing the carbon intensity data
- [DuckDB](https://duckdb.org/) for fast analytical database
- [dbt](https://www.getdbt.com/) for data transformation
- [Great Expectations](https://greatexpectations.io/) for data validation
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Streamlit](https://streamlit.io/) for the dashboard

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Join our Discord community
- Email: support@carbonpulse.com

---

**🌱 Making carbon intensity data accessible and actionable for everyone.**
