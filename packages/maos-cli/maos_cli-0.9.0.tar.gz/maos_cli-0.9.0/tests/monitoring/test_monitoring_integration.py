"""
Integration tests for MAOS monitoring system.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from src.monitoring.monitoring_service import MonitoringService
from src.monitoring.health.health_manager import HealthManager
from src.monitoring.health.health_checker import HealthStatus, ComponentHealth
from src.monitoring.metrics.prometheus_collector import PrometheusCollector
from src.monitoring.alerts.alert_manager import AlertManager, Alert, AlertRule, AlertSeverity
from src.monitoring.dashboard.monitoring_dashboard import MonitoringDashboard


class TestMonitoringIntegration:
    """Integration tests for the complete monitoring system."""
    
    @pytest.fixture
    async def monitoring_service(self):
        """Create monitoring service for testing."""
        config = {
            "notifications": {
                "webhook": {
                    "url": "http://localhost:8080/webhook",
                    "headers": {"Authorization": "Bearer test-token"}
                }
            }
        }
        
        service = MonitoringService(
            config=config,
            health_check_interval=1.0,
            metrics_collection_interval=1.0,
            alert_evaluation_interval=1.0,
            dashboard_update_interval=1.0
        )
        
        yield service
        
        # Cleanup
        if service._running:
            await service.stop()
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator."""
        orchestrator = Mock()
        orchestrator.is_running = True
        orchestrator._task_queue = [Mock() for _ in range(5)]
        orchestrator._active_tasks = {f"task_{i}": Mock() for i in range(3)}
        return orchestrator
    
    @pytest.fixture
    def mock_agent_manager(self):
        """Create mock agent manager."""
        agent_manager = Mock()
        
        # Mock agents
        agents = {}
        for i in range(4):
            agent = Mock()
            agent.status = "active" if i < 2 else "idle"
            agent.last_activity = datetime.utcnow()
            agent.utilization = 75.0 if i < 2 else 0.0
            agents[f"agent_{i}"] = agent
        
        agent_manager._agents = agents
        return agent_manager
    
    @pytest.fixture
    def mock_message_bus(self):
        """Create mock message bus."""
        message_bus = Mock()
        message_bus.is_connected = True
        message_bus._pending_messages = [Mock() for _ in range(10)]
        message_bus._processed_count = 1000
        message_bus._failed_count = 50
        message_bus._subscribers = {f"sub_{i}": Mock() for i in range(5)}
        message_bus._connections = {f"conn_{i}": Mock() for i in range(3)}
        return message_bus
    
    @pytest.fixture
    def mock_redis_manager(self):
        """Create mock Redis manager."""
        redis_manager = Mock()
        
        # Mock Redis client
        redis_client = AsyncMock()
        
        # Mock Redis info
        redis_info = {
            "used_memory": 1024 * 1024 * 100,  # 100MB
            "maxmemory": 1024 * 1024 * 1024,   # 1GB
            "connected_clients": 10,
            "instantaneous_ops_per_sec": 150,
            "keyspace_hits": 9000,
            "keyspace_misses": 1000,
            "evicted_keys": 5,
            "used_cpu_sys": 15.5,
            "total_net_input_bytes": 1024 * 1024 * 50,
            "total_net_output_bytes": 1024 * 1024 * 30
        }
        
        redis_client.ping.return_value = True
        redis_client.info.return_value = redis_info
        
        redis_manager.redis = redis_client
        return redis_manager
    
    @pytest.mark.asyncio
    async def test_full_system_initialization(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_agent_manager,
        mock_message_bus,
        mock_redis_manager
    ):
        """Test complete monitoring system initialization."""
        # Initialize with all components
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            agent_manager=mock_agent_manager,
            message_bus=mock_message_bus,
            redis_manager=mock_redis_manager,
            external_dependencies={
                "test_service": {
                    "type": "http",
                    "url": "http://localhost:8080/health",
                    "timeout": 5.0
                }
            }
        )
        
        # Verify components are registered
        assert "orchestrator" in monitoring_service._registered_components
        assert "agent_manager" in monitoring_service._registered_components
        assert "message_bus" in monitoring_service._registered_components
        assert "redis_manager" in monitoring_service._registered_components
        
        # Verify health checkers are registered
        registered_components = monitoring_service.health_manager.get_registered_components()
        assert "orchestrator" in registered_components
        assert "agent_manager" in registered_components
        assert "communication" in registered_components
        assert "storage" in registered_components
        assert "dependencies" in registered_components
        
        # Verify alert rules are configured
        alert_stats = monitoring_service.alert_manager.get_alert_statistics()
        assert alert_stats["total_rules"] > 0
        assert alert_stats["enabled_rules"] > 0
    
    @pytest.mark.asyncio
    async def test_monitoring_service_lifecycle(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test monitoring service start/stop lifecycle."""
        # Initialize
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            redis_manager=mock_redis_manager
        )
        
        # Start monitoring
        await monitoring_service.start()
        
        # Verify service is running
        assert monitoring_service._running
        assert monitoring_service._startup_time is not None
        
        # Get status
        status = monitoring_service.get_status()
        assert status["service_running"]
        assert status["uptime_seconds"] >= 0
        assert len(status["registered_components"]) > 0
        
        # Stop monitoring
        await monitoring_service.stop()
        
        # Verify service is stopped
        assert not monitoring_service._running
    
    @pytest.mark.asyncio
    async def test_health_check_workflow(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test complete health check workflow."""
        # Initialize and start
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            redis_manager=mock_redis_manager
        )
        await monitoring_service.start()
        
        # Wait a bit for initial health checks
        await asyncio.sleep(1.5)
        
        # Get health status
        health_data = await monitoring_service.health_manager.get_health_status()
        
        # Verify health data structure
        assert "system_status" in health_data
        assert "components" in health_data
        assert "summary" in health_data
        
        # Verify components are present
        components = health_data["components"]
        assert "orchestrator" in components
        assert "storage" in components
        
        # Verify component health structure
        orchestrator_health = components["orchestrator"]
        assert "status" in orchestrator_health
        assert "message" in orchestrator_health
        assert "check_duration_ms" in orchestrator_health
        
        await monitoring_service.stop()
    
    @pytest.mark.asyncio
    async def test_metrics_collection_workflow(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test metrics collection workflow."""
        # Initialize and start
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            redis_manager=mock_redis_manager
        )
        await monitoring_service.start()
        
        # Wait for metrics collection
        await asyncio.sleep(1.5)
        
        # Get metrics
        metrics_text = monitoring_service.metrics_collector.get_metrics()
        
        # Verify metrics format
        assert isinstance(metrics_text, str)
        assert "maos_system_health_status" in metrics_text
        assert "maos_component_health_status" in metrics_text
        
        # Test metric recording
        monitoring_service.metrics_collector.record_task_completion(
            "test_task", "test_type", 1.5, True
        )
        
        monitoring_service.metrics_collector.record_latency("test_operation", 0.05)
        
        await monitoring_service.stop()
    
    @pytest.mark.asyncio
    async def test_alert_workflow(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test complete alert workflow."""
        # Initialize with mock webhook notification
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful webhook response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            await monitoring_service.initialize(
                orchestrator=mock_orchestrator,
                redis_manager=mock_redis_manager
            )
            await monitoring_service.start()
            
            # Create test alert rule
            test_rule = AlertRule(
                name="test_alert",
                description="Test alert for integration testing",
                metric_name="test_metric",
                condition="gt",
                threshold=50.0,
                severity=AlertSeverity.HIGH,
                component="test"
            )
            
            monitoring_service.alert_manager.add_alert_rule(test_rule)
            
            # Mock metric value to trigger alert
            with patch.object(
                monitoring_service.alert_manager,
                '_get_metric_value',
                return_value=75.0
            ):
                # Wait for alert evaluation
                await asyncio.sleep(1.5)
                
                # Check for active alerts
                active_alerts = monitoring_service.alert_manager.get_active_alerts()
                assert len(active_alerts) > 0
                
                # Find our test alert
                test_alert = None
                for alert in active_alerts:
                    if alert.name == "test_alert":
                        test_alert = alert
                        break
                
                assert test_alert is not None
                assert test_alert.severity == AlertSeverity.HIGH
                assert test_alert.metric_value == 75.0
                
                # Test alert acknowledgment
                success = await monitoring_service.alert_manager.acknowledge_alert(
                    test_alert.id, "test_user"
                )
                assert success
                
                # Verify acknowledgment
                updated_alert = monitoring_service.alert_manager._active_alerts[test_alert.id]
                assert updated_alert.acknowledged_by == "test_user"
            
            await monitoring_service.stop()
    
    @pytest.mark.asyncio
    async def test_dashboard_integration(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_agent_manager,
        mock_redis_manager
    ):
        """Test dashboard integration with all components."""
        # Initialize and start
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            agent_manager=mock_agent_manager,
            redis_manager=mock_redis_manager
        )
        await monitoring_service.start()
        
        # Wait for data collection
        await asyncio.sleep(2.0)
        
        # Get dashboard data
        dashboard_data = monitoring_service.dashboard.get_dashboard_data()
        
        # Verify dashboard data structure
        assert "timestamp" in dashboard_data
        assert "system_overview" in dashboard_data
        assert "health_status" in dashboard_data
        assert "performance_metrics" in dashboard_data
        assert "agent_status" in dashboard_data
        assert "alert_summary" in dashboard_data
        
        # Verify system overview
        system_overview = dashboard_data["system_overview"]
        assert "status" in system_overview
        assert "components_total" in system_overview
        assert "components_healthy" in system_overview
        
        # Verify agent status
        agent_status = dashboard_data["agent_status"]
        assert "total_agents" in agent_status
        assert "active_agents" in agent_status
        assert "idle_agents" in agent_status
        
        # Test dashboard configuration
        config = monitoring_service.dashboard.get_dashboard_config()
        assert "refresh_rate_seconds" in config
        
        # Update configuration
        new_config = {"refresh_rate_seconds": 10.0}
        monitoring_service.dashboard.update_dashboard_config(new_config)
        
        updated_config = monitoring_service.dashboard.get_dashboard_config()
        assert updated_config["refresh_rate_seconds"] == 10.0
        
        await monitoring_service.stop()
    
    @pytest.mark.asyncio
    async def test_fastapi_integration(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test FastAPI integration and endpoints."""
        # Initialize
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            redis_manager=mock_redis_manager
        )
        
        # Create FastAPI app
        app = monitoring_service.create_fastapi_app()
        
        # Verify app is created
        assert app is not None
        assert app.title == "MAOS Monitoring API"
        
        # Test that routes are added
        route_paths = [route.path for route in app.routes]
        
        # Check for expected endpoints
        expected_paths = [
            "/health/",
            "/info",
            "/alerts/",
            "/dashboard/"
        ]
        
        for path in expected_paths:
            assert any(path in route_path for route_path in route_paths)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test error handling and recovery scenarios."""
        # Initialize and start
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            redis_manager=mock_redis_manager
        )
        await monitoring_service.start()
        
        # Simulate Redis connection failure
        mock_redis_manager.redis.ping.side_effect = Exception("Connection failed")
        
        # Wait for health check to detect failure
        await asyncio.sleep(1.5)
        
        # Check that storage health reflects the failure
        health_data = await monitoring_service.health_manager.get_health_status()
        storage_health = health_data["components"]["storage"]
        assert storage_health["status"] == "unhealthy"
        
        # Simulate recovery
        mock_redis_manager.redis.ping.side_effect = None
        mock_redis_manager.redis.ping.return_value = True
        
        # Wait for recovery detection
        await asyncio.sleep(1.5)
        
        # Check that health recovers
        health_data = await monitoring_service.health_manager.get_health_status()
        storage_health = health_data["components"]["storage"]
        assert storage_health["status"] == "healthy"
        
        await monitoring_service.stop()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(
        self,
        monitoring_service,
        mock_orchestrator,
        mock_redis_manager
    ):
        """Test monitoring system performance under load."""
        # Initialize with faster intervals for stress testing
        monitoring_service.health_manager.check_interval = 0.1
        monitoring_service.metrics_collector.collection_interval = 0.1
        monitoring_service.alert_manager.evaluation_interval = 0.1
        
        await monitoring_service.initialize(
            orchestrator=mock_orchestrator,
            redis_manager=mock_redis_manager
        )
        await monitoring_service.start()
        
        # Let it run for a short time under load
        await asyncio.sleep(2.0)
        
        # Check performance metrics
        dashboard_perf = monitoring_service.dashboard.get_performance_stats()
        
        assert "average_update_time_seconds" in dashboard_perf
        assert "total_updates" in dashboard_perf
        assert dashboard_perf["total_updates"] > 0
        
        # Verify system is still responsive
        health_data = await monitoring_service.health_manager.get_health_status()
        assert health_data is not None
        assert "system_status" in health_data
        
        await monitoring_service.stop()


class TestMonitoringComponents:
    """Test individual monitoring components."""
    
    @pytest.mark.asyncio
    async def test_health_manager_standalone(self):
        """Test health manager independently."""
        health_manager = HealthManager(check_interval=0.5)
        
        # Create mock health checker
        mock_checker = AsyncMock()
        mock_checker.component_name = "test_component"
        mock_checker.dependencies = []
        
        # Mock health check result
        health_result = ComponentHealth(
            component_name="test_component",
            status=HealthStatus.HEALTHY,
            message="Component is healthy"
        )
        mock_checker.perform_health_check.return_value = health_result
        mock_checker.get_current_health.return_value = health_result
        
        # Register checker
        health_manager.register_checker(mock_checker)
        
        # Start monitoring
        await health_manager.start_monitoring()
        
        # Wait for health checks
        await asyncio.sleep(1.0)
        
        # Get health status
        health_data = await health_manager.get_health_status()
        
        assert health_data["system_status"] == "healthy"
        assert "test_component" in health_data["components"]
        
        # Stop monitoring
        await health_manager.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_alert_manager_standalone(self):
        """Test alert manager independently."""
        alert_manager = AlertManager(evaluation_interval=0.5)
        
        # Add test rule
        rule = AlertRule(
            name="test_rule",
            description="Test rule",
            metric_name="test_metric",
            condition="gt",
            threshold=10.0,
            severity=AlertSeverity.MEDIUM,
            component="test"
        )
        alert_manager.add_alert_rule(rule)
        
        # Mock metric source
        with patch.object(alert_manager, '_get_metric_value', return_value=15.0):
            # Start evaluation
            await alert_manager.start_evaluation()
            
            # Wait for evaluation
            await asyncio.sleep(1.0)
            
            # Check for alerts
            active_alerts = alert_manager.get_active_alerts()
            assert len(active_alerts) > 0
            
            alert = active_alerts[0]
            assert alert.name == "test_rule"
            assert alert.metric_value == 15.0
            
            # Stop evaluation
            await alert_manager.stop_evaluation()
    
    def test_prometheus_metrics_collection(self):
        """Test Prometheus metrics collection."""
        collector = PrometheusCollector(collection_interval=1.0)
        
        # Record some metrics
        collector.record_task_completion("test_task", "test", 1.5, True)
        collector.record_latency("test_operation", 0.1)
        collector.record_storage_operation("get", 0.05, True)
        
        # Get metrics
        metrics = collector.get_metrics()
        
        # Verify format
        assert isinstance(metrics, str)
        assert "maos_tasks_total" in metrics
        assert "maos_latency_seconds" in metrics
        assert "maos_storage_operations_total" in metrics
        
        # Verify content type
        content_type = collector.get_content_type()
        assert "text/plain" in content_type