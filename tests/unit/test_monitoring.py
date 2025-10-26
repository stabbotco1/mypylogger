"""Tests for security status monitoring and alerting."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch
from urllib.error import URLError

from badges.monitoring import (
    AlertConfig,
    PerformanceMetrics,
    SecurityStatusMonitor,
    StatusUpdateMonitor,
    UptimeMetrics,
    get_default_monitor,
    get_default_update_monitor,
    run_monitoring_check,
)


class TestPerformanceMetrics:
    """Test PerformanceMetrics class."""

    def test_init_success_metrics(self) -> None:
        """Test initialization of successful metrics."""
        now = datetime.now(timezone.utc)
        metrics = PerformanceMetrics(
            response_time_ms=150.5,
            status_code=200,
            content_size_bytes=1024,
            timestamp=now,
            endpoint_url="https://example.com/api",
            success=True,
        )

        assert metrics.response_time_ms == 150.5
        assert metrics.status_code == 200
        assert metrics.content_size_bytes == 1024
        assert metrics.timestamp == now
        assert metrics.endpoint_url == "https://example.com/api"
        assert metrics.success is True
        assert metrics.error_message is None

    def test_init_failure_metrics(self) -> None:
        """Test initialization of failure metrics."""
        now = datetime.now(timezone.utc)
        metrics = PerformanceMetrics(
            response_time_ms=5000.0,
            status_code=0,
            content_size_bytes=0,
            timestamp=now,
            endpoint_url="https://example.com/api",
            success=False,
            error_message="Connection timeout",
        )

        assert metrics.success is False
        assert metrics.error_message == "Connection timeout"

    def test_to_dict(self) -> None:
        """Test converting metrics to dictionary."""
        now = datetime.now(timezone.utc)
        metrics = PerformanceMetrics(
            response_time_ms=200.0,
            status_code=200,
            content_size_bytes=512,
            timestamp=now,
            endpoint_url="https://example.com/api",
        )

        result = metrics.to_dict()

        assert result["response_time_ms"] == 200.0
        assert result["status_code"] == 200
        assert result["content_size_bytes"] == 512
        assert result["timestamp"] == now.isoformat()
        assert result["endpoint_url"] == "https://example.com/api"
        assert result["success"] is True

    def test_from_dict(self) -> None:
        """Test creating metrics from dictionary."""
        now = datetime.now(timezone.utc)
        data = {
            "response_time_ms": 300.0,
            "status_code": 404,
            "content_size_bytes": 256,
            "timestamp": now.isoformat(),
            "endpoint_url": "https://example.com/api",
            "success": False,
            "error_message": "Not found",
        }

        metrics = PerformanceMetrics.from_dict(data)

        assert metrics.response_time_ms == 300.0
        assert metrics.status_code == 404
        assert metrics.success is False
        assert metrics.error_message == "Not found"


class TestUptimeMetrics:
    """Test UptimeMetrics class."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        metrics = UptimeMetrics()

        assert metrics.total_checks == 0
        assert metrics.successful_checks == 0
        assert metrics.failed_checks == 0
        assert metrics.consecutive_failures == 0
        assert metrics.uptime_percentage == 100.0
        assert metrics.is_healthy is True

    def test_uptime_percentage_calculation(self) -> None:
        """Test uptime percentage calculation."""
        metrics = UptimeMetrics()
        metrics.total_checks = 10
        metrics.successful_checks = 8
        metrics.failed_checks = 2

        assert metrics.uptime_percentage == 80.0

    def test_is_healthy_good_uptime(self) -> None:
        """Test healthy status with good uptime."""
        metrics = UptimeMetrics()
        metrics.total_checks = 100
        metrics.successful_checks = 98
        metrics.failed_checks = 2
        metrics.consecutive_failures = 1

        assert metrics.is_healthy is True

    def test_is_healthy_low_uptime(self) -> None:
        """Test unhealthy status with low uptime."""
        metrics = UptimeMetrics()
        metrics.total_checks = 100
        metrics.successful_checks = 90
        metrics.failed_checks = 10

        assert metrics.is_healthy is False

    def test_is_healthy_consecutive_failures(self) -> None:
        """Test unhealthy status with consecutive failures."""
        metrics = UptimeMetrics()
        metrics.total_checks = 100
        metrics.successful_checks = 97
        metrics.failed_checks = 3
        metrics.consecutive_failures = 5

        assert metrics.is_healthy is False

    def test_record_success(self) -> None:
        """Test recording successful check."""
        metrics = UptimeMetrics()

        metrics.record_success(100.0)

        assert metrics.total_checks == 1
        assert metrics.successful_checks == 1
        assert metrics.failed_checks == 0
        assert metrics.consecutive_failures == 0
        assert metrics.average_response_time_ms == 100.0
        assert metrics.last_success_time is not None

    def test_record_success_running_average(self) -> None:
        """Test recording multiple successes with running average."""
        metrics = UptimeMetrics()

        metrics.record_success(100.0)
        metrics.record_success(200.0)

        assert metrics.successful_checks == 2
        assert metrics.average_response_time_ms == 150.0

    def test_record_failure(self) -> None:
        """Test recording failed check."""
        metrics = UptimeMetrics()

        metrics.record_failure()

        assert metrics.total_checks == 1
        assert metrics.successful_checks == 0
        assert metrics.failed_checks == 1
        assert metrics.consecutive_failures == 1
        assert metrics.last_failure_time is not None

    def test_to_dict(self) -> None:
        """Test converting metrics to dictionary."""
        now = datetime.now(timezone.utc)
        metrics = UptimeMetrics()
        metrics.total_checks = 100
        metrics.successful_checks = 98  # 98% uptime, above 95% threshold
        metrics.failed_checks = 2
        metrics.last_check_time = now

        result = metrics.to_dict()

        assert result["total_checks"] == 100
        assert result["successful_checks"] == 98
        assert result["uptime_percentage"] == 98.0
        assert result["is_healthy"] is True

    def test_from_dict(self) -> None:
        """Test creating metrics from dictionary."""
        now = datetime.now(timezone.utc)
        data = {
            "total_checks": 20,
            "successful_checks": 18,
            "failed_checks": 2,
            "last_check_time": now.isoformat(),
            "consecutive_failures": 1,
            "average_response_time_ms": 250.0,
        }

        metrics = UptimeMetrics.from_dict(data)

        assert metrics.total_checks == 20
        assert metrics.successful_checks == 18
        assert metrics.consecutive_failures == 1
        assert metrics.average_response_time_ms == 250.0


class TestAlertConfig:
    """Test AlertConfig class."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        config = AlertConfig()

        assert config.response_time_threshold_ms == 1000.0
        assert config.uptime_threshold_percentage == 95.0
        assert config.consecutive_failure_threshold == 3
        assert config.alert_cooldown_minutes == 60
        assert config.enabled is True

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values."""
        config = AlertConfig(
            response_time_threshold_ms=500.0,
            uptime_threshold_percentage=99.0,
            consecutive_failure_threshold=5,
            alert_cooldown_minutes=30,
            enabled=False,
        )

        assert config.response_time_threshold_ms == 500.0
        assert config.uptime_threshold_percentage == 99.0
        assert config.consecutive_failure_threshold == 5
        assert config.alert_cooldown_minutes == 30
        assert config.enabled is False

    def test_to_dict(self) -> None:
        """Test converting config to dictionary."""
        config = AlertConfig(response_time_threshold_ms=750.0)

        result = config.to_dict()

        assert result["response_time_threshold_ms"] == 750.0
        assert result["enabled"] is True

    def test_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "response_time_threshold_ms": 2000.0,
            "uptime_threshold_percentage": 90.0,
            "enabled": False,
        }

        config = AlertConfig.from_dict(data)

        assert config.response_time_threshold_ms == 2000.0
        assert config.uptime_threshold_percentage == 90.0
        assert config.enabled is False


class TestSecurityStatusMonitor:
    """Test SecurityStatusMonitor class."""

    def test_init_default_config(self) -> None:
        """Test initialization with default configuration."""
        monitor = SecurityStatusMonitor()

        assert "github.io" in monitor.base_url
        assert monitor.metrics_file == Path("monitoring/metrics.json")
        assert isinstance(monitor.alert_config, AlertConfig)
        assert isinstance(monitor.uptime_metrics, UptimeMetrics)

    def test_init_custom_config(self) -> None:
        """Test initialization with custom configuration."""
        base_url = "https://custom.github.io/repo"
        metrics_file = Path("/custom/metrics.json")
        alert_config = AlertConfig(enabled=False)

        monitor = SecurityStatusMonitor(base_url, metrics_file, alert_config)

        assert monitor.base_url == base_url
        assert monitor.metrics_file == metrics_file
        assert monitor.alert_config.enabled is False

    @patch("badges.monitoring.urlopen")
    def test_check_api_availability_success(self, mock_urlopen: Mock) -> None:
        """Test successful API availability check."""
        # Mock successful response
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status": "ok"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        monitor = SecurityStatusMonitor()
        metrics = monitor.check_api_availability()

        assert metrics.success is True
        assert metrics.status_code == 200
        assert metrics.content_size_bytes == len(b'{"status": "ok"}')
        assert metrics.response_time_ms > 0
        assert monitor.uptime_metrics.successful_checks == 1

    @patch("badges.monitoring.urlopen")
    def test_check_api_availability_failure(self, mock_urlopen: Mock) -> None:
        """Test failed API availability check."""
        # Mock URLError
        mock_urlopen.side_effect = URLError("Connection failed")

        monitor = SecurityStatusMonitor()
        metrics = monitor.check_api_availability()

        assert metrics.success is False
        assert metrics.status_code == 0
        assert "Connection failed" in metrics.error_message
        assert monitor.uptime_metrics.failed_checks == 1

    @patch("badges.monitoring.urlopen")
    def test_check_api_availability_invalid_json(self, mock_urlopen: Mock) -> None:
        """Test API check with invalid JSON response."""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        monitor = SecurityStatusMonitor()
        metrics = monitor.check_api_availability()

        assert metrics.success is False
        assert "Invalid JSON response" in metrics.error_message

    def test_run_monitoring_check_success(self) -> None:
        """Test successful monitoring check."""
        monitor = SecurityStatusMonitor()

        # Mock check_api_availability
        with patch.object(monitor, "check_api_availability") as mock_check:
            mock_metrics = PerformanceMetrics(
                response_time_ms=100.0,
                status_code=200,
                content_size_bytes=512,
                timestamp=datetime.now(timezone.utc),
                endpoint_url="https://example.com/api",
                success=True,
            )
            mock_check.return_value = mock_metrics

            # Mock save_metrics
            with patch.object(monitor, "_save_metrics"):
                result = monitor.run_monitoring_check()

        assert result["success"] is True
        assert "metrics" in result
        assert "uptime" in result
        assert "alerts" in result

    def test_run_monitoring_check_failure(self) -> None:
        """Test monitoring check with exception."""
        monitor = SecurityStatusMonitor()

        # Mock check_api_availability to raise exception
        with patch.object(monitor, "check_api_availability") as mock_check:
            mock_check.side_effect = RuntimeError("Check failed")

            result = monitor.run_monitoring_check()

        assert result["success"] is False
        assert "Check failed" in result["error"]

    def test_get_monitoring_summary(self) -> None:
        """Test getting monitoring summary."""
        monitor = SecurityStatusMonitor()

        # Add some test metrics
        now = datetime.now(timezone.utc)
        test_metrics = PerformanceMetrics(
            response_time_ms=200.0,
            status_code=200,
            content_size_bytes=1024,
            timestamp=now,
            endpoint_url="https://example.com/api",
        )
        monitor.performance_history.append(test_metrics)
        monitor.uptime_metrics.record_success(200.0)

        summary = monitor.get_monitoring_summary()

        assert "uptime" in summary
        assert "recent_performance" in summary
        assert "alert_config" in summary
        assert summary["service_status"] == "healthy"

    def test_check_alerts_high_response_time(self) -> None:
        """Test alert generation for high response time."""
        config = AlertConfig(response_time_threshold_ms=100.0)
        monitor = SecurityStatusMonitor(alert_config=config)

        # Create metrics with high response time
        metrics = PerformanceMetrics(
            response_time_ms=500.0,
            status_code=200,
            content_size_bytes=512,
            timestamp=datetime.now(timezone.utc),
            endpoint_url="https://example.com/api",
            success=True,
        )

        alerts = monitor._check_alerts(metrics)

        assert len(alerts) == 1
        assert alerts[0]["type"] == "high_response_time"
        assert alerts[0]["severity"] == "warning"

    def test_check_alerts_consecutive_failures(self) -> None:
        """Test alert generation for consecutive failures."""
        config = AlertConfig(consecutive_failure_threshold=2)
        monitor = SecurityStatusMonitor(alert_config=config)

        # Set up consecutive failures
        monitor.uptime_metrics.consecutive_failures = 3

        # Create failure metrics
        metrics = PerformanceMetrics(
            response_time_ms=0.0,
            status_code=0,
            content_size_bytes=0,
            timestamp=datetime.now(timezone.utc),
            endpoint_url="https://example.com/api",
            success=False,
            error_message="Connection failed",
        )

        alerts = monitor._check_alerts(metrics)

        assert len(alerts) >= 1
        alert_types = [alert["type"] for alert in alerts]
        assert "consecutive_failures" in alert_types

    def test_check_alerts_disabled(self) -> None:
        """Test no alerts when alerting is disabled."""
        config = AlertConfig(enabled=False)
        monitor = SecurityStatusMonitor(alert_config=config)

        # Create metrics that would normally trigger alerts
        metrics = PerformanceMetrics(
            response_time_ms=5000.0,
            status_code=0,
            content_size_bytes=0,
            timestamp=datetime.now(timezone.utc),
            endpoint_url="https://example.com/api",
            success=False,
        )

        alerts = monitor._check_alerts(metrics)

        assert len(alerts) == 0

    def test_should_send_alert_cooldown(self) -> None:
        """Test alert cooldown functionality."""
        config = AlertConfig(alert_cooldown_minutes=30)
        monitor = SecurityStatusMonitor(alert_config=config)

        now = datetime.now(timezone.utc)

        # First alert should be sent
        assert monitor._should_send_alert("test_alert", now) is True

        # Record the alert
        monitor.last_alerts["test_alert"] = now

        # Alert within cooldown period should not be sent
        soon = now + timedelta(minutes=15)
        assert monitor._should_send_alert("test_alert", soon) is False

        # Alert after cooldown period should be sent
        later = now + timedelta(minutes=35)
        assert monitor._should_send_alert("test_alert", later) is True

    def test_load_metrics_no_file(self) -> None:
        """Test loading metrics when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metrics_file = temp_path / "nonexistent.json"

            monitor = SecurityStatusMonitor(metrics_file=metrics_file)

            # Should not raise exception and use default values
            assert monitor.uptime_metrics.total_checks == 0

    def test_load_metrics_success(self) -> None:
        """Test successful metrics loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metrics_file = temp_path / "metrics.json"

            # Create test data
            now = datetime.now(timezone.utc)
            test_data = {
                "uptime_metrics": {
                    "total_checks": 10,
                    "successful_checks": 8,
                    "failed_checks": 2,
                    "consecutive_failures": 1,
                    "average_response_time_ms": 150.0,
                },
                "performance_history": [],
                "last_alerts": {
                    "test_alert": now.isoformat(),
                },
            }

            # Write test data
            with metrics_file.open("w") as f:
                json.dump(test_data, f)

            monitor = SecurityStatusMonitor(metrics_file=metrics_file)

            assert monitor.uptime_metrics.total_checks == 10
            assert monitor.uptime_metrics.successful_checks == 8
            assert "test_alert" in monitor.last_alerts

    def test_save_metrics_success(self) -> None:
        """Test successful metrics saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metrics_file = temp_path / "metrics.json"

            monitor = SecurityStatusMonitor(metrics_file=metrics_file)
            monitor.uptime_metrics.record_success(100.0)

            monitor._save_metrics()

            assert metrics_file.exists()

            # Verify saved data
            with metrics_file.open("r") as f:
                data = json.load(f)
            assert data["uptime_metrics"]["total_checks"] == 1


class TestStatusUpdateMonitor:
    """Test StatusUpdateMonitor class."""

    def test_init_default_components(self) -> None:
        """Test initialization with default components."""
        monitor = StatusUpdateMonitor()

        assert monitor.status_manager is not None
        assert monitor.pages_generator is not None
        assert isinstance(monitor.alert_config, AlertConfig)

    def test_init_custom_components(self) -> None:
        """Test initialization with custom components."""
        status_manager = Mock()
        pages_generator = Mock()
        alert_config = AlertConfig(enabled=False)

        monitor = StatusUpdateMonitor(status_manager, pages_generator, alert_config)

        assert monitor.status_manager == status_manager
        assert monitor.pages_generator == pages_generator
        assert monitor.alert_config.enabled is False

    def test_monitor_status_update_success(self) -> None:
        """Test successful status update monitoring."""
        # Mock components
        mock_status_manager = Mock()
        mock_pages_generator = Mock()

        monitor = StatusUpdateMonitor(mock_status_manager, mock_pages_generator)

        # Mock successful operations
        with patch.object(monitor, "_test_status_manager_update") as mock_sm_test:
            with patch.object(monitor, "_test_pages_generator_update") as mock_pg_test:
                mock_sm_test.return_value = {"success": True, "duration_ms": 100}
                mock_pg_test.return_value = {"success": True, "duration_ms": 200}

                result = monitor.monitor_status_update()

        assert result["success"] is True
        assert result["total_time_ms"] > 0
        assert len(result["alerts"]) == 0

    def test_monitor_status_update_failure(self) -> None:
        """Test status update monitoring with failure."""
        # Mock components
        mock_status_manager = Mock()
        mock_pages_generator = Mock()
        alert_config = AlertConfig(enabled=True)

        monitor = StatusUpdateMonitor(mock_status_manager, mock_pages_generator, alert_config)

        # Mock failed operations
        with patch.object(monitor, "_test_status_manager_update") as mock_sm_test:
            with patch.object(monitor, "_test_pages_generator_update") as mock_pg_test:
                mock_sm_test.return_value = {"success": False, "error": "SM failed"}
                mock_pg_test.return_value = {"success": True, "duration_ms": 200}

                result = monitor.monitor_status_update()

        assert result["success"] is False
        assert len(result["alerts"]) == 1
        assert result["alerts"][0]["type"] == "status_update_failure"

    def test_test_status_manager_update_success(self) -> None:
        """Test successful status manager update test."""
        mock_status_manager = Mock()
        mock_status = Mock()
        mock_status.security_grade = "A"
        mock_status.vulnerability_summary.total = 0

        mock_status_manager.get_current_status.return_value = mock_status
        mock_status_manager.update_status.return_value = mock_status

        monitor = StatusUpdateMonitor(mock_status_manager)
        result = monitor._test_status_manager_update()

        assert result["success"] is True
        assert result["updated_status_grade"] == "A"
        assert result["vulnerability_count"] == 0

    def test_test_status_manager_update_failure(self) -> None:
        """Test failed status manager update test."""
        mock_status_manager = Mock()
        mock_status_manager.update_status.side_effect = RuntimeError("Update failed")

        monitor = StatusUpdateMonitor(mock_status_manager)
        result = monitor._test_status_manager_update()

        assert result["success"] is False
        assert "Update failed" in result["error"]

    def test_test_pages_generator_update_success(self) -> None:
        """Test successful pages generator update test."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            mock_pages_generator = Mock()
            mock_pages_generator.pages_dir = temp_path

            # Create mock files
            (temp_path / "index.json").touch()
            (temp_path / "index.html").touch()

            monitor = StatusUpdateMonitor(pages_generator=mock_pages_generator)
            result = monitor._test_pages_generator_update()

            assert result["success"] is True
            assert result["api_file_exists"] is True
            assert result["html_file_exists"] is True

    def test_test_pages_generator_update_failure(self) -> None:
        """Test failed pages generator update test."""
        mock_pages_generator = Mock()
        mock_pages_generator.generate_api_endpoint.side_effect = RuntimeError("Generation failed")

        monitor = StatusUpdateMonitor(pages_generator=mock_pages_generator)
        result = monitor._test_pages_generator_update()

        assert result["success"] is False
        assert "Generation failed" in result["error"]


class TestModuleFunctions:
    """Test module-level functions."""

    def test_get_default_monitor(self) -> None:
        """Test getting default monitor."""
        monitor = get_default_monitor()

        assert isinstance(monitor, SecurityStatusMonitor)

    def test_get_default_update_monitor(self) -> None:
        """Test getting default update monitor."""
        monitor = get_default_update_monitor()

        assert isinstance(monitor, StatusUpdateMonitor)

    @patch("badges.monitoring.SecurityStatusMonitor")
    def test_run_monitoring_check(self, mock_monitor_class: Mock) -> None:
        """Test run_monitoring_check function."""
        mock_monitor = Mock()
        mock_result = {"success": True}
        mock_monitor.run_monitoring_check.return_value = mock_result
        mock_monitor_class.return_value = mock_monitor

        base_url = "https://custom.github.io/repo"
        metrics_file = Path("/custom/metrics.json")
        alert_config = AlertConfig()

        result = run_monitoring_check(base_url, metrics_file, alert_config)

        mock_monitor_class.assert_called_once_with(base_url, metrics_file, alert_config)
        mock_monitor.run_monitoring_check.assert_called_once()
        assert result == mock_result
