"""Tests for Azure Telemetry Wrapper."""

import unittest
from unittest.mock import patch, MagicMock
import os
from ntt_ai_observability_exporter import configure_telemetry

class TestTelemetry(unittest.TestCase):
    """Test cases for the Azure Telemetry Wrapper."""

    @patch("ntt_ai_observability_exporter.telemetry.configure_azure_monitor")
    def test_configure_telemetry_with_params(self, mock_configure):
        """Test configuring telemetry with explicit parameters."""
        # Arrange
        mock_configure.return_value = True
        
        # Act
        result = configure_telemetry(
            connection_string="test-connection-string",
            customer_name="test-customer",
            agent_name="test-agent"
        )
        
        # Assert
        self.assertTrue(result)
        mock_configure.assert_called_once()
        # Check that resource was created with correct attributes
        resource = mock_configure.call_args[1]["resource"]
        self.assertEqual(resource.attributes["service.name"], "test-customer")
        self.assertEqual(resource.attributes["service.instance.id"], "test-agent")
        
        # Check default tracing environment variables
        self.assertEqual(os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"], "true")
        self.assertEqual(os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"], "all")
        self.assertEqual(os.environ["ENABLE_AZURE_MONITOR_TRACING"], "true")

    @patch("ntt_ai_observability_exporter.telemetry.configure_azure_monitor")
    def test_configure_telemetry_with_custom_tracing_params(self, mock_configure):
        """Test configuring telemetry with custom tracing parameters."""
        # Arrange
        mock_configure.return_value = True
        
        # Act
        result = configure_telemetry(
            connection_string="test-connection-string",
            customer_name="test-customer",
            agent_name="test-agent",
            enable_content_recording=False,
            content_recording_mode="sanitized",
            enable_azure_monitor_tracing=False
        )
        
        # Assert
        self.assertTrue(result)
        mock_configure.assert_called_once()
        
        # Check custom tracing environment variables
        self.assertEqual(os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"], "false")
        self.assertEqual(os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_MODE"], "sanitized")
        self.assertEqual(os.environ["ENABLE_AZURE_MONITOR_TRACING"], "false")

    @patch("ntt_ai_observability_exporter.telemetry.configure_azure_monitor")
    def test_configure_telemetry_with_env_vars(self, mock_configure):
        """Test configuring telemetry with environment variables."""
        # Arrange
        mock_configure.return_value = True
        os.environ["AZURE_MONITOR_CONNECTION_STRING"] = "env-connection-string"
        os.environ["CUSTOMER_NAME"] = "env-customer"
        os.environ["AGENT_NAME"] = "env-agent"
        
        try:
            # Act
            result = configure_telemetry()
            
            # Assert
            self.assertTrue(result)
            mock_configure.assert_called_once()
            # Check that resource was created with correct attributes
            resource = mock_configure.call_args[1]["resource"]
            self.assertEqual(resource.attributes["service.name"], "env-customer")
            self.assertEqual(resource.attributes["service.instance.id"], "env-agent")
        finally:
            # Clean up
            del os.environ["AZURE_MONITOR_CONNECTION_STRING"]
            del os.environ["CUSTOMER_NAME"]
            del os.environ["AGENT_NAME"]

    @patch("ntt_ai_observability_exporter.telemetry.configure_azure_monitor")
    def test_configure_telemetry_missing_required_params(self, mock_configure):
        """Test that missing required parameters raise appropriate errors."""
        # Don't configure the mock in this test - we want to see the errors
        mock_configure.side_effect = Exception("This should not be called")
        
        # Test missing connection string
        result = configure_telemetry(customer_name="test", agent_name="test")
        self.assertFalse(result)
        
        # Test missing customer name
        result = configure_telemetry(connection_string="test", agent_name="test")
        self.assertFalse(result)
        
        # Test missing agent name
        result = configure_telemetry(connection_string="test", customer_name="test")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()