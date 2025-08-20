"""
Tests for Certificate Monitor Command

Tests certificate expiry checks, health monitoring, alert setup, and auto-renewal.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

from mcp_proxy_adapter.commands.cert_monitor_command import CertMonitorCommand, CertMonitorResult
from mcp_proxy_adapter.commands.result import CommandResult


class TestCertMonitorResult:
    """Test CertMonitorResult class."""
    
    def test_cert_monitor_result_initialization(self):
        """Test CertMonitorResult initialization."""
        result = CertMonitorResult(
            cert_path="/path/to/cert.pem",
            check_type="expiry",
            status="healthy",
            expiry_date="2024-12-31T23:59:59",
            days_until_expiry=30,
            health_score=95,
            alerts=["Certificate is healthy"],
            auto_renewal_status="enabled"
        )
        
        assert result.cert_path == "/path/to/cert.pem"
        assert result.check_type == "expiry"
        assert result.status == "healthy"
        assert result.expiry_date == "2024-12-31T23:59:59"
        assert result.days_until_expiry == 30
        assert result.health_score == 95
        assert result.alerts == ["Certificate is healthy"]
        assert result.auto_renewal_status == "enabled"
        assert result.error is None
    
    def test_cert_monitor_result_to_dict(self):
        """Test CertMonitorResult to_dict method."""
        result = CertMonitorResult(
            cert_path="/path/to/cert.pem",
            check_type="health",
            status="healthy",
            expiry_date="2024-12-31T23:59:59",
            days_until_expiry=30,
            health_score=95,
            alerts=["Certificate is healthy"],
            auto_renewal_status="enabled"
        )
        
        data = result.to_dict()
        
        assert data["cert_path"] == "/path/to/cert.pem"
        assert data["check_type"] == "health"
        assert data["status"] == "healthy"
        assert data["expiry_date"] == "2024-12-31T23:59:59"
        assert data["days_until_expiry"] == 30
        assert data["health_score"] == 95
        assert data["alerts"] == ["Certificate is healthy"]
        assert data["auto_renewal_status"] == "enabled"
    
    def test_cert_monitor_result_get_schema(self):
        """Test CertMonitorResult get_schema method."""
        result = CertMonitorResult(
            cert_path="/path/to/cert.pem",
            check_type="expiry",
            status="healthy"
        )
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "cert_path" in schema["properties"]
        assert "check_type" in schema["properties"]
        assert "status" in schema["properties"]
        assert "expiry_date" in schema["properties"]
        assert "health_score" in schema["properties"]


class TestCertMonitorCommand:
    """Test CertMonitorCommand class."""
    
    @pytest.fixture
    def monitor_command(self):
        """Create CertMonitorCommand instance."""
        return CertMonitorCommand()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_cert_file(self, temp_dir):
        """Create mock certificate file."""
        cert_file = os.path.join(temp_dir, "test.crt")
        
        # Create mock file
        with open(cert_file, 'w') as f:
            f.write("MOCK CERTIFICATE")
        
        return cert_file
    
    @pytest.mark.asyncio
    async def test_cert_expiry_check_missing_file(self, monitor_command):
        """Test certificate expiry check with missing file."""
        result = await monitor_command.cert_expiry_check("/nonexistent/cert.pem")
        
        assert result.to_dict()["success"] is False
        assert "Certificate file not found" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_no_cert_info(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with no certificate info."""
        # Mock certificate utils to return None
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = None
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Could not read certificate information" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_no_expiry_date(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with no expiry date."""
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com"
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Could not determine certificate expiry date" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_invalid_date_format(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with invalid date format."""
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com",
            "expiry_date": "invalid-date"
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Invalid expiry date format" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_expired(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with expired certificate."""
        # Mock certificate utils
        mock_utils = Mock()
        # Set expiry date to yesterday
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com",
            "expiry_date": yesterday
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["is_expired"] is True
        assert result.data["monitor_result"]["health_status"] == "expired"
        assert result.data["monitor_result"]["days_until_expiry"] < 0
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_critical(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with critical status."""
        # Mock certificate utils
        mock_utils = Mock()
        # Set expiry date to 5 days from now (critical threshold)
        critical_date = (datetime.now() + timedelta(days=5)).isoformat()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com",
            "expiry_date": critical_date
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file, warning_days=30, critical_days=7)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["is_expired"] is False
        assert result.data["monitor_result"]["health_status"] == "critical"
        assert result.data["monitor_result"]["days_until_expiry"] <= 7
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_warning(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with warning status."""
        # Mock certificate utils
        mock_utils = Mock()
        # Set expiry date to 15 days from now (warning threshold)
        warning_date = (datetime.now() + timedelta(days=15)).isoformat()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com",
            "expiry_date": warning_date
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file, warning_days=30, critical_days=7)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["is_expired"] is False
        assert result.data["monitor_result"]["health_status"] == "warning"
        assert result.data["monitor_result"]["days_until_expiry"] <= 30
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_expiry_check_healthy(self, mock_cert_utils, monitor_command, mock_cert_file):
        """Test certificate expiry check with healthy status."""
        # Mock certificate utils
        mock_utils = Mock()
        # Set expiry date to 60 days from now (healthy)
        healthy_date = (datetime.now() + timedelta(days=60)).isoformat()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com",
            "expiry_date": healthy_date
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_expiry_check(mock_cert_file, warning_days=30, critical_days=7)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["is_expired"] is False
        assert result.data["monitor_result"]["health_status"] == "healthy"
        assert result.data["monitor_result"]["days_until_expiry"] > 30
    
    @pytest.mark.asyncio
    async def test_cert_health_check_missing_file(self, monitor_command):
        """Test certificate health check with missing file."""
        result = await monitor_command.cert_health_check("/nonexistent/cert.pem")
        
        assert result.to_dict()["success"] is False
        assert "Certificate file not found" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.AuthValidator')
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_health_check_success(self, mock_cert_utils, mock_auth_validator, monitor_command, mock_cert_file):
        """Test successful certificate health check."""
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com"
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        # Mock successful validation
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_certificate.return_value = mock_validation_result
        mock_auth_validator.return_value = mock_validator
        monitor_command.auth_validator = mock_validator
        
        result = await monitor_command.cert_health_check(mock_cert_file)
        
        assert result.to_dict()["success"] is True
        assert "monitor_result" in result.data
        assert "health_checks" in result.data
        assert result.data["overall_status"] == "healthy"
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.AuthValidator')
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_health_check_validation_failed(self, mock_cert_utils, mock_auth_validator, monitor_command, mock_cert_file):
        """Test certificate health check with validation failure."""
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com"
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        # Mock validation failure
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validator.validate_certificate.return_value = mock_validation_result
        mock_auth_validator.return_value = mock_validator
        monitor_command.auth_validator = mock_validator
        
        result = await monitor_command.cert_health_check(mock_cert_file)
        
        assert result.to_dict()["success"] is True
        assert result.data["overall_status"] == "critical"
        assert result.data["health_checks"]["validation"]["passed"] is False
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_missing_file(self, monitor_command):
        """Test alert setup with missing file."""
        alert_config = {"enabled": True, "warning_days": 30}
        
        result = await monitor_command.cert_alert_setup("/nonexistent/cert.pem", alert_config)
        
        assert result.to_dict()["success"] is False
        assert "Certificate file not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_invalid_config(self, monitor_command, mock_cert_file):
        """Test alert setup with invalid configuration."""
        result = await monitor_command.cert_alert_setup(mock_cert_file, "invalid_config")
        
        assert result.to_dict()["success"] is False
        assert "must be a dictionary" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_disabled(self, monitor_command, mock_cert_file):
        """Test alert setup with alerts disabled."""
        alert_config = {"enabled": False}
        
        result = await monitor_command.cert_alert_setup(mock_cert_file, alert_config)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["alerts_enabled"] is False
        assert "Alerts disabled" in result.data["message"]
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_invalid_warning_days(self, monitor_command, mock_cert_file):
        """Test alert setup with invalid warning days."""
        alert_config = {
            "enabled": True,
            "warning_days": 0,
            "critical_days": 7,
            "notification_channels": ["email"]
        }
        
        result = await monitor_command.cert_alert_setup(mock_cert_file, alert_config)
        
        assert result.to_dict()["success"] is False
        assert "must be positive" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_invalid_critical_days(self, monitor_command, mock_cert_file):
        """Test alert setup with invalid critical days."""
        alert_config = {
            "enabled": True,
            "warning_days": 30,
            "critical_days": 0,
            "notification_channels": ["email"]
        }
        
        result = await monitor_command.cert_alert_setup(mock_cert_file, alert_config)
        
        assert result.to_dict()["success"] is False
        assert "must be positive" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_warning_less_than_critical(self, monitor_command, mock_cert_file):
        """Test alert setup with warning days less than critical days."""
        alert_config = {
            "enabled": True,
            "warning_days": 5,
            "critical_days": 10,
            "notification_channels": ["email"]
        }
        
        result = await monitor_command.cert_alert_setup(mock_cert_file, alert_config)
        
        assert result.to_dict()["success"] is False
        assert "Warning days must be greater than critical days" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_no_channels(self, monitor_command, mock_cert_file):
        """Test alert setup with no notification channels."""
        alert_config = {
            "enabled": True,
            "warning_days": 30,
            "critical_days": 7,
            "notification_channels": []
        }
        
        result = await monitor_command.cert_alert_setup(mock_cert_file, alert_config)
        
        assert result.to_dict()["success"] is False
        assert "At least one notification channel must be specified" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_success(self, monitor_command, mock_cert_file):
        """Test successful alert setup."""
        alert_config = {
            "enabled": True,
            "warning_days": 30,
            "critical_days": 7,
            "email_recipients": ["admin@example.com"],
            "webhook_url": "https://example.com/webhook",
            "notification_channels": ["email", "webhook"]
        }
        
        result = await monitor_command.cert_alert_setup(mock_cert_file, alert_config)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["alerts_enabled"] is True
        assert "Alerts configured successfully" in result.data["message"]
        assert "alert_config" in result.data
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_missing_file(self, monitor_command):
        """Test auto-renewal setup with missing file."""
        renewal_config = {"enabled": True, "renewal_days": 30}
        
        result = await monitor_command.cert_auto_renew("/nonexistent/cert.pem", renewal_config)
        
        assert result.to_dict()["success"] is False
        assert "Certificate file not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_invalid_config(self, monitor_command, mock_cert_file):
        """Test auto-renewal setup with invalid configuration."""
        result = await monitor_command.cert_auto_renew(mock_cert_file, "invalid_config")
        
        assert result.to_dict()["success"] is False
        assert "must be a dictionary" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_disabled(self, monitor_command, mock_cert_file):
        """Test auto-renewal setup with auto-renewal disabled."""
        renewal_config = {"enabled": False}
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, renewal_config)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["auto_renewal_enabled"] is False
        assert "Auto-renewal disabled" in result.data["message"]
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_invalid_renewal_days(self, monitor_command, mock_cert_file):
        """Test auto-renewal setup with invalid renewal days."""
        renewal_config = {
            "enabled": True,
            "renew_before_days": 0,
            "ca_cert_path": "/path/to/ca.crt",
            "ca_key_path": "/path/to/ca.key",
            "output_dir": "/tmp"
        }
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, renewal_config)
        
        assert result.to_dict()["success"] is False
        assert "must be positive" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_missing_ca_cert(self, monitor_command, mock_cert_file):
        """Test auto-renewal setup with missing CA certificate."""
        renewal_config = {
            "enabled": True,
            "renew_before_days": 30,
            "ca_cert_path": "/nonexistent/ca.crt",
            "ca_key_path": "/path/to/ca.key",
            "output_dir": "/tmp"
        }
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, renewal_config)
        
        assert result.to_dict()["success"] is False
        assert "CA certificate not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_missing_ca_key(self, monitor_command, mock_cert_file, temp_dir):
        """Test auto-renewal setup with missing CA key."""
        # Create mock CA cert file
        ca_cert_path = os.path.join(temp_dir, "ca.crt")
        with open(ca_cert_path, 'w') as f:
            f.write("MOCK CA CERT")
        
        renewal_config = {
            "enabled": True,
            "renew_before_days": 30,
            "ca_cert_path": ca_cert_path,
            "ca_key_path": "/nonexistent/ca.key",
            "output_dir": "/tmp"
        }
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, renewal_config)
        
        assert result.to_dict()["success"] is False
        assert "CA private key not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_missing_output_dir(self, monitor_command, mock_cert_file, temp_dir):
        """Test auto-renewal setup with missing output directory."""
        # Create mock CA files
        ca_cert_path = os.path.join(temp_dir, "ca.crt")
        ca_key_path = os.path.join(temp_dir, "ca.key")
        with open(ca_cert_path, 'w') as f:
            f.write("MOCK CA CERT")
        with open(ca_key_path, 'w') as f:
            f.write("MOCK CA KEY")
        
        renewal_config = {
            "enabled": True,
            "renew_before_days": 30,
            "ca_cert_path": ca_cert_path,
            "ca_key_path": ca_key_path
        }
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, renewal_config)
        
        assert result.to_dict()["success"] is False
        assert "Output directory must be specified" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.cert_monitor_command.CertificateUtils')
    async def test_cert_auto_renew_success(self, mock_cert_utils, monitor_command, mock_cert_file, temp_dir):
        """Test successful auto-renewal setup."""
        # Create mock CA files
        ca_cert_path = os.path.join(temp_dir, "ca.crt")
        ca_key_path = os.path.join(temp_dir, "ca.key")
        with open(ca_cert_path, 'w') as f:
            f.write("MOCK CA CERT")
        with open(ca_key_path, 'w') as f:
            f.write("MOCK CA KEY")
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com",
            "roles": ["admin"]
        }
        mock_cert_utils.return_value = mock_utils
        monitor_command.certificate_utils = mock_utils
        
        renewal_config = {
            "enabled": True,
            "renew_before_days": 30,
            "ca_cert_path": ca_cert_path,
            "ca_key_path": ca_key_path,
            "output_dir": temp_dir
        }
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, renewal_config)
        
        assert result.to_dict()["success"] is True
        assert result.data["monitor_result"]["auto_renewal_enabled"] is True
        assert "Auto-renewal configured successfully" in result.data["message"]
        assert "auto_renew_config" in result.data
    
    @pytest.mark.asyncio
    async def test_cert_expiry_check_exception_handling(self, monitor_command):
        """Test certificate expiry check exception handling."""
        # Create a temporary file to pass the file existence check
        with tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False) as f:
            f.write("MOCK CERT")
            temp_cert_path = f.name
        
        try:
            with patch.object(monitor_command, 'certificate_utils') as mock_utils:
                mock_utils.get_certificate_info.side_effect = Exception("Test exception")
                result = await monitor_command.cert_expiry_check(temp_cert_path)
                
                assert result.to_dict()["success"] is False
                assert "Certificate expiry check failed" in result.error
        finally:
            os.unlink(temp_cert_path)
    
    @pytest.mark.asyncio
    async def test_cert_health_check_exception_handling(self, monitor_command):
        """Test certificate health check exception handling."""
        # Create a temporary file to pass the file existence check
        with tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False) as f:
            f.write("MOCK CERT")
            temp_cert_path = f.name
        
        try:
            with patch.object(monitor_command, 'certificate_utils') as mock_utils:
                mock_utils.get_certificate_info.side_effect = Exception("Test exception")
                result = await monitor_command.cert_health_check(temp_cert_path)
                
                assert result.to_dict()["success"] is False
                assert "Certificate health check failed" in result.error
        finally:
            os.unlink(temp_cert_path)
    
    @pytest.mark.asyncio
    async def test_cert_alert_setup_exception_handling(self, monitor_command, mock_cert_file):
        """Test alert setup exception handling."""
        with patch.object(monitor_command, '_test_alert_config', side_effect=Exception("Test exception")):
            result = await monitor_command.cert_alert_setup(mock_cert_file, {
                "enabled": True, 
                "warning_days": 30,
                "critical_days": 7,
                "notification_channels": ["email"]
            })
            
            assert result.to_dict()["success"] is False
            assert "Alert setup failed" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_auto_renew_exception_handling(self, monitor_command, mock_cert_file, temp_dir):
        """Test auto-renewal setup exception handling."""
        # Create mock CA files
        ca_cert_path = os.path.join(temp_dir, "ca.crt")
        ca_key_path = os.path.join(temp_dir, "ca.key")
        with open(ca_cert_path, 'w') as f:
            f.write("MOCK CA CERT")
        with open(ca_key_path, 'w') as f:
            f.write("MOCK CA KEY")
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.get_certificate_info.side_effect = Exception("Test exception")
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command.cert_auto_renew(mock_cert_file, {
            "enabled": True, 
            "renew_before_days": 30,
            "ca_cert_path": ca_cert_path,
            "ca_key_path": ca_key_path,
            "output_dir": temp_dir
        })
        
        assert result.to_dict()["success"] is False
        assert "Renewal configuration test failed" in result.error
    
    @pytest.mark.asyncio
    async def test_test_alert_config_success(self, monitor_command):
        """Test internal alert configuration test success."""
        alert_config = {
            "email_recipients": ["admin@example.com"],
            "webhook_url": "https://example.com/webhook"
        }
        
        result = await monitor_command._test_alert_config(alert_config)
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_test_alert_config_failure(self, monitor_command):
        """Test internal alert configuration test failure."""
        # Test with invalid email recipients
        alert_config = {
            "email_recipients": []  # Empty list should fail validation
        }
        
        result = await monitor_command._test_alert_config(alert_config)
        
        assert result["success"] is False
        assert "Invalid email recipients" in result["error"]
    
    @pytest.mark.asyncio
    async def test_test_renewal_config_success(self, monitor_command, mock_cert_file, temp_dir):
        """Test internal renewal configuration test success."""
        # Create mock CA files
        ca_cert_path = os.path.join(temp_dir, "ca.crt")
        ca_key_path = os.path.join(temp_dir, "ca.key")
        
        with open(ca_cert_path, 'w') as f:
            f.write("MOCK CA CERT")
        with open(ca_key_path, 'w') as f:
            f.write("MOCK CA KEY")
        
        renewal_config = {
            "ca_cert_path": ca_cert_path,
            "ca_key_path": ca_key_path,
            "output_dir": temp_dir
        }
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test.example.com"
        }
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command._test_renewal_config(mock_cert_file, renewal_config)
        
        assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_test_renewal_config_no_cert_info(self, monitor_command, mock_cert_file):
        """Test internal renewal configuration test with no certificate info."""
        renewal_config = {
            "ca_cert_path": "/path/to/ca.crt",
            "ca_key_path": "/path/to/ca.key",
            "output_dir": "/tmp"
        }
        
        with patch.object(monitor_command, 'certificate_utils') as mock_utils:
            mock_utils.get_certificate_info.return_value = None
            
            result = await monitor_command._test_renewal_config(mock_cert_file, renewal_config)
            
            assert result["success"] is False
            assert "Could not read certificate information" in result["error"]
    
    @pytest.mark.asyncio
    async def test_test_renewal_config_missing_ca_cert(self, monitor_command, mock_cert_file):
        """Test internal renewal configuration test with missing CA certificate."""
        renewal_config = {
            "ca_cert_path": "/nonexistent/ca.crt",
            "ca_key_path": "/path/to/ca.key",
            "output_dir": "/tmp"
        }
        
        with patch.object(monitor_command, 'certificate_utils') as mock_utils:
            mock_utils.get_certificate_info.return_value = {
                "type": "server",
                "common_name": "test.example.com"
            }
            
            result = await monitor_command._test_renewal_config(mock_cert_file, renewal_config)
            
            assert result["success"] is False
            assert "CA certificate not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_test_renewal_config_exception_handling(self, monitor_command, mock_cert_file):
        """Test internal renewal configuration test exception handling."""
        renewal_config = {
            "ca_cert_path": "/path/to/ca.crt",
            "ca_key_path": "/path/to/ca.key",
            "output_dir": "/tmp"
        }
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.get_certificate_info.side_effect = Exception("Test exception")
        monitor_command.certificate_utils = mock_utils
        
        result = await monitor_command._test_renewal_config(mock_cert_file, renewal_config)
        
        assert result["success"] is False
        assert "Test exception" in result["error"] 