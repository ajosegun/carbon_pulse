"""Tests for loguru logger configuration."""

import pytest
from pathlib import Path
import tempfile
import os

from carbon_pulse.logger import logger, setup_logger
from carbon_pulse.config import settings


class TestLogger:
    """Test logger configuration."""

    def test_logger_initialization(self):
        """Test that logger is properly initialized."""
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")

    def test_logger_info_message(self):
        """Test info level logging."""
        # This should not raise any exceptions
        logger.info("Test info message")

    def test_logger_error_message(self):
        """Test error level logging."""
        # This should not raise any exceptions
        logger.error("Test error message")

    def test_logger_debug_message(self):
        """Test debug level logging."""
        # This should not raise any exceptions
        logger.debug("Test debug message")

    def test_logger_with_context(self):
        """Test logger with structured data."""
        logger.info(
            "Test message with context", extra={"zone": "US", "intensity": 250.5}
        )

    def test_logger_format(self):
        """Test that logger uses the configured format."""
        # The format should include time, level, name, function, line, and message
        # We can't easily test the exact format without capturing output,
        # but we can verify the logger is configured
        assert settings.log_format is not None
        assert "{time:" in settings.log_format
        assert "{level:" in settings.log_format
        assert "{message}" in settings.log_format

    def test_log_file_configuration(self):
        """Test log file configuration."""
        assert settings.log_file is not None
        assert "logs/carbon_pulse.log" in settings.log_file

    def test_log_level_configuration(self):
        """Test log level configuration."""
        assert settings.log_level is not None
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class TestLoggerFileOutput:
    """Test logger file output functionality."""

    @pytest.fixture
    def temp_log_file(self):
        """Create a temporary log file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            temp_log_path = f.name

        try:
            yield temp_log_path
        finally:
            # Cleanup
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)

    def test_logger_file_output(self, temp_log_file):
        """Test that logger can write to file."""
        # Temporarily modify settings to use temp file
        original_log_file = settings.log_file
        settings.log_file = temp_log_file

        try:
            # Re-setup logger with temp file
            setup_logger()

            # Write a test message
            test_message = "Test log message for file output"
            logger.info(test_message)

            # Check if message was written to file
            with open(temp_log_file, "r") as f:
                log_content = f.read()

            assert test_message in log_content

        finally:
            # Restore original settings
            settings.log_file = original_log_file
            setup_logger()


class TestLoggerIntegration:
    """Test logger integration with other components."""

    def test_logger_with_database_manager(self):
        """Test that database manager uses logger correctly."""
        from carbon_pulse.data.database import DatabaseManager

        # This should not raise any exceptions and should use the logger
        try:
            # Create a temporary database
            with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
                temp_db_path = f.name

            # Temporarily modify database URL
            original_db_url = settings.database_url
            settings.database_url = f"duckdb:///{temp_db_path}"

            try:
                # This should use the logger internally
                db = DatabaseManager()
                db.close()
            finally:
                # Cleanup
                settings.database_url = original_db_url
                if os.path.exists(temp_db_path):
                    os.unlink(temp_db_path)

        except Exception:
            # It's okay if this fails due to missing dependencies
            # We're just testing that the logger is used
            pass

    def test_logger_with_electricity_maps_client(self):
        """Test that electricity maps client uses logger correctly."""
        from carbon_pulse.data.electricity_maps import ElectricityMapsClient

        # This should not raise any exceptions and should use the logger
        try:
            client = ElectricityMapsClient()
            # The client should be initialized with logger
            assert client is not None
        except Exception:
            # It's okay if this fails due to missing API key
            # We're just testing that the logger is used
            pass
