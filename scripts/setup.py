#!/usr/bin/env python3
"""Setup script for Carbon Pulse."""

import os
import sys
import subprocess
from pathlib import Path

from loguru import logger


def run_command(command, description):
    """Run a command and handle errors."""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        logger.success(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False


def check_prerequisites():
    """Check if prerequisites are installed."""
    logger.info("🔍 Checking prerequisites...")

    # Check Python version
    if sys.version_info < (3, 11):
        logger.error("❌ Python 3.11+ is required")
        return False

    logger.success(
        f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected"
    )

    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        logger.success("✅ uv is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error(
            "❌ uv is not installed. Please install it from https://github.com/astral-sh/uv"
        )
        return False

    return True


def setup_environment():
    """Set up environment variables."""
    logger.info("🔧 Setting up environment...")

    env_file = Path(".env")
    env_example = Path("env.example")

    if not env_file.exists() and env_example.exists():
        logger.info("📝 Creating .env file from template...")
        os.system(f"cp env.example .env")
        logger.success("✅ .env file created. Please edit it with your configuration.")
    elif env_file.exists():
        logger.success("✅ .env file already exists")
    else:
        logger.warning("⚠️  No .env file or template found")


def install_dependencies():
    """Install project dependencies."""
    logger.info("📦 Installing dependencies...")

    if not run_command("uv sync --dev", "Installing dependencies"):
        return False

    return True


def initialize_database():
    """Initialize the database."""
    logger.info("🗄️  Initializing database...")

    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Initialize database
    if not run_command(
        'uv run python -c "from carbon_pulse.data.database import DatabaseManager; DatabaseManager()"',
        "Creating database tables",
    ):
        return False

    return True


def setup_dbt():
    """Set up dbt."""
    logger.info("🔧 Setting up dbt...")

    if not run_command("uv run dbt deps", "Installing dbt dependencies"):
        return False

    return True


def setup_great_expectations():
    """Set up Great Expectations."""
    logger.info("🔧 Setting up Great Expectations...")

    # Create necessary directories
    ge_dirs = [
        "great_expectations/expectations",
        "great_expectations/checkpoints",
        "great_expectations/plugins",
        "great_expectations/uncommitted",
    ]

    for dir_path in ge_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    logger.success("✅ Great Expectations directories created")
    return True


def run_tests():
    """Run tests to verify setup."""
    logger.info("🧪 Running tests...")

    if not run_command("uv run pytest tests/ -v", "Running tests"):
        return False

    return True


def main():
    """Main setup function."""
    # Configure loguru for setup script
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
    )

    logger.info("🌱 Welcome to Carbon Pulse Setup!")
    logger.info("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        logger.error(
            "\n❌ Prerequisites check failed. Please install required dependencies."
        )
        sys.exit(1)

    # Setup environment
    setup_environment()

    # Install dependencies
    if not install_dependencies():
        logger.error("\n❌ Failed to install dependencies.")
        sys.exit(1)

    # Initialize database
    if not initialize_database():
        logger.error("\n❌ Failed to initialize database.")
        sys.exit(1)

    # Setup dbt
    if not setup_dbt():
        logger.error("\n❌ Failed to setup dbt.")
        sys.exit(1)

    # Setup Great Expectations
    if not setup_great_expectations():
        logger.error("\n❌ Failed to setup Great Expectations.")
        sys.exit(1)

    # Run tests
    if not run_tests():
        logger.error("\n❌ Tests failed.")
        sys.exit(1)

    logger.success("\n🎉 Setup completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Edit .env file with your configuration")
    logger.info("2. Run the API: uv run carbon-pulse-api")
    logger.info("3. Run the dashboard: uv run carbon-pulse-dashboard")
    logger.info("4. Or use Docker: docker-compose up -d")
    logger.info("\n📚 For more information, see the README.md file")


if __name__ == "__main__":
    main()
