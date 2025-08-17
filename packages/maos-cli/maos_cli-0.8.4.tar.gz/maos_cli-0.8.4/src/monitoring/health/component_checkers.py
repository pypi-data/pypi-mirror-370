"""
Specific health checkers for different MAOS components.
"""

import asyncio
import aioredis
import psutil
from datetime import datetime
from typing import Dict, List, Optional, Any

from ...maos.core.orchestrator import Orchestrator
from ...maos.core.agent_manager import AgentManager
from ...communication.message_bus.core import MessageBus
from ...storage.redis_state.redis_state_manager import RedisStateManager
from .health_checker import HealthChecker, ComponentHealth, HealthStatus


class OrchestratorHealthChecker(HealthChecker):
    """Health checker for the MAOS orchestrator."""
    
    def __init__(self, orchestrator: Orchestrator, **kwargs):
        super().__init__("orchestrator", **kwargs)
        self.orchestrator = orchestrator
    
    async def check_health(self) -> ComponentHealth:
        """Check orchestrator health."""
        details = {}
        metrics = {}
        
        try:
            # Check orchestrator state
            is_running = self.orchestrator.is_running if hasattr(self.orchestrator, 'is_running') else True
            
            # Check task queue status
            pending_tasks = len(getattr(self.orchestrator, '_task_queue', []))
            active_tasks = len(getattr(self.orchestrator, '_active_tasks', {}))
            
            details.update({
                "is_running": is_running,
                "pending_tasks": pending_tasks,
                "active_tasks": active_tasks
            })
            
            metrics.update({
                "pending_tasks": float(pending_tasks),
                "active_tasks": float(active_tasks)
            })
            
            # Determine status
            if not is_running:
                status = HealthStatus.UNHEALTHY
                message = "Orchestrator is not running"
            elif pending_tasks > 100:  # Configurable threshold
                status = HealthStatus.DEGRADED
                message = f"High task queue depth: {pending_tasks} pending tasks"
            else:
                status = HealthStatus.HEALTHY
                message = "Orchestrator is operating normally"
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                message=message,
                details=details,
                metrics=metrics,
                dependencies=["message_bus", "agent_manager"]
            )
            
        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check orchestrator health: {str(e)}",
                details={"error": str(e)}
            )


class AgentHealthChecker(HealthChecker):
    """Health checker for agent manager and individual agents."""
    
    def __init__(self, agent_manager: AgentManager, **kwargs):
        super().__init__("agent_manager", **kwargs)
        self.agent_manager = agent_manager
    
    async def check_health(self) -> ComponentHealth:
        """Check agent manager and agents health."""
        details = {}
        metrics = {}
        
        try:
            # Get agent statistics
            total_agents = len(getattr(self.agent_manager, '_agents', {}))
            active_agents = 0
            idle_agents = 0
            failed_agents = 0
            
            agents_info = {}
            
            # Check individual agents (if we have access to them)
            if hasattr(self.agent_manager, '_agents'):
                for agent_id, agent in self.agent_manager._agents.items():
                    agent_status = getattr(agent, 'status', 'unknown')
                    agents_info[agent_id] = {
                        "status": agent_status,
                        "last_activity": getattr(agent, 'last_activity', None)
                    }
                    
                    if agent_status == 'active':
                        active_agents += 1
                    elif agent_status == 'idle':
                        idle_agents += 1
                    elif agent_status in ['failed', 'error']:
                        failed_agents += 1
            
            details.update({
                "total_agents": total_agents,
                "active_agents": active_agents,
                "idle_agents": idle_agents,
                "failed_agents": failed_agents,
                "agents": agents_info
            })
            
            metrics.update({
                "total_agents": float(total_agents),
                "active_agents": float(active_agents),
                "idle_agents": float(idle_agents),
                "failed_agents": float(failed_agents)
            })
            
            # Determine status
            if total_agents == 0:
                status = HealthStatus.DEGRADED
                message = "No agents are currently registered"
            elif failed_agents > total_agents * 0.2:  # More than 20% failed
                status = HealthStatus.DEGRADED
                message = f"{failed_agents} of {total_agents} agents have failed"
            elif failed_agents > 0:
                status = HealthStatus.DEGRADED
                message = f"{failed_agents} agents have failed"
            else:
                status = HealthStatus.HEALTHY
                message = f"All {total_agents} agents are healthy"
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                message=message,
                details=details,
                metrics=metrics,
                dependencies=["message_bus"]
            )
            
        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check agent health: {str(e)}",
                details={"error": str(e)}
            )


class CommunicationHealthChecker(HealthChecker):
    """Health checker for message bus and communication layer."""
    
    def __init__(self, message_bus: MessageBus, **kwargs):
        super().__init__("communication", **kwargs)
        self.message_bus = message_bus
    
    async def check_health(self) -> ComponentHealth:
        """Check communication layer health."""
        details = {}
        metrics = {}
        
        try:
            # Check message bus connection
            is_connected = getattr(self.message_bus, 'is_connected', True)
            
            # Get message statistics
            pending_messages = len(getattr(self.message_bus, '_pending_messages', []))
            processed_messages = getattr(self.message_bus, '_processed_count', 0)
            failed_messages = getattr(self.message_bus, '_failed_count', 0)
            
            # Check subscriber count
            subscriber_count = len(getattr(self.message_bus, '_subscribers', {}))
            
            details.update({
                "is_connected": is_connected,
                "pending_messages": pending_messages,
                "processed_messages": processed_messages,
                "failed_messages": failed_messages,
                "subscriber_count": subscriber_count
            })
            
            metrics.update({
                "pending_messages": float(pending_messages),
                "processed_messages": float(processed_messages),
                "failed_messages": float(failed_messages),
                "subscriber_count": float(subscriber_count)
            })
            
            # Calculate error rate
            total_messages = processed_messages + failed_messages
            error_rate = (failed_messages / total_messages * 100) if total_messages > 0 else 0
            metrics["error_rate_percentage"] = error_rate
            
            # Determine status
            if not is_connected:
                status = HealthStatus.UNHEALTHY
                message = "Message bus is disconnected"
            elif error_rate > 5.0:  # More than 5% error rate
                status = HealthStatus.DEGRADED
                message = f"High error rate: {error_rate:.1f}%"
            elif pending_messages > 1000:  # High message backlog
                status = HealthStatus.DEGRADED
                message = f"High message backlog: {pending_messages} pending"
            else:
                status = HealthStatus.HEALTHY
                message = "Communication layer is operating normally"
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                message=message,
                details=details,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check communication health: {str(e)}",
                details={"error": str(e)}
            )


class StorageHealthChecker(HealthChecker):
    """Health checker for Redis storage layer."""
    
    def __init__(self, redis_manager: RedisStateManager, **kwargs):
        super().__init__("storage", **kwargs)
        self.redis_manager = redis_manager
    
    async def check_health(self) -> ComponentHealth:
        """Check storage layer health."""
        details = {}
        metrics = {}
        
        try:
            redis_client = self.redis_manager.redis
            
            # Test basic connectivity
            ping_result = await redis_client.ping()
            
            # Get Redis info
            redis_info = await redis_client.info()
            
            # Extract key metrics
            memory_usage = redis_info.get('used_memory', 0)
            memory_max = redis_info.get('maxmemory', 0)
            connected_clients = redis_info.get('connected_clients', 0)
            ops_per_sec = redis_info.get('instantaneous_ops_per_sec', 0)
            hit_rate = 0
            
            # Calculate hit rate
            hits = redis_info.get('keyspace_hits', 0)
            misses = redis_info.get('keyspace_misses', 0)
            if hits + misses > 0:
                hit_rate = (hits / (hits + misses)) * 100
            
            # Memory usage percentage
            memory_usage_pct = (memory_usage / memory_max * 100) if memory_max > 0 else 0
            
            details.update({
                "ping_success": ping_result,
                "memory_usage_bytes": memory_usage,
                "memory_max_bytes": memory_max,
                "memory_usage_percentage": memory_usage_pct,
                "connected_clients": connected_clients,
                "operations_per_second": ops_per_sec,
                "hit_rate_percentage": hit_rate
            })
            
            metrics.update({
                "memory_usage_bytes": float(memory_usage),
                "memory_usage_percentage": float(memory_usage_pct),
                "connected_clients": float(connected_clients),
                "operations_per_second": float(ops_per_sec),
                "hit_rate_percentage": float(hit_rate)
            })
            
            # Determine status
            if not ping_result:
                status = HealthStatus.UNHEALTHY
                message = "Redis ping failed"
            elif memory_usage_pct > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {memory_usage_pct:.1f}%"
            elif memory_usage_pct > 80:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {memory_usage_pct:.1f}%"
            elif hit_rate < 70:
                status = HealthStatus.DEGRADED
                message = f"Low cache hit rate: {hit_rate:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = "Storage layer is operating normally"
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                message=message,
                details=details,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check storage health: {str(e)}",
                details={"error": str(e)}
            )


class DependencyHealthChecker(HealthChecker):
    """Health checker for external dependencies (PostgreSQL, external APIs, etc.)."""
    
    def __init__(self, dependencies: Dict[str, Dict[str, Any]], **kwargs):
        super().__init__("dependencies", **kwargs)
        self.dependencies = dependencies
    
    async def check_health(self) -> ComponentHealth:
        """Check external dependencies health."""
        details = {}
        metrics = {}
        failed_deps = []
        degraded_deps = []
        
        try:
            for dep_name, dep_config in self.dependencies.items():
                dep_status = await self._check_dependency(dep_name, dep_config)
                details[dep_name] = dep_status
                
                if dep_status["status"] == "unhealthy":
                    failed_deps.append(dep_name)
                elif dep_status["status"] == "degraded":
                    degraded_deps.append(dep_name)
                
                # Add metrics
                metrics[f"{dep_name}_response_time_ms"] = dep_status.get("response_time_ms", 0)
            
            # Overall status
            total_deps = len(self.dependencies)
            failed_count = len(failed_deps)
            degraded_count = len(degraded_deps)
            
            metrics.update({
                "total_dependencies": float(total_deps),
                "failed_dependencies": float(failed_count),
                "degraded_dependencies": float(degraded_count),
                "healthy_dependencies": float(total_deps - failed_count - degraded_count)
            })
            
            if failed_count > 0:
                status = HealthStatus.UNHEALTHY
                message = f"{failed_count} dependencies are failing: {', '.join(failed_deps)}"
            elif degraded_count > 0:
                status = HealthStatus.DEGRADED
                message = f"{degraded_count} dependencies are degraded: {', '.join(degraded_deps)}"
            else:
                status = HealthStatus.HEALTHY
                message = f"All {total_deps} dependencies are healthy"
            
            return ComponentHealth(
                component_name=self.component_name,
                status=status,
                message=message,
                details=details,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to check dependencies: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _check_dependency(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check individual dependency."""
        import time
        start_time = time.time()
        
        try:
            dep_type = config.get("type", "unknown")
            
            if dep_type == "redis":
                return await self._check_redis_dependency(config)
            elif dep_type == "postgresql":
                return await self._check_postgresql_dependency(config)
            elif dep_type == "http":
                return await self._check_http_dependency(config)
            else:
                return {
                    "status": "unknown",
                    "message": f"Unknown dependency type: {dep_type}",
                    "response_time_ms": 0
                }
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "message": f"Dependency check failed: {str(e)}",
                "error": str(e),
                "response_time_ms": response_time
            }
    
    async def _check_redis_dependency(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check Redis dependency."""
        import time
        start_time = time.time()
        
        redis_url = config.get("url", "redis://localhost:6379")
        redis = aioredis.from_url(redis_url)
        
        try:
            await redis.ping()
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "message": "Redis is responding",
                "response_time_ms": response_time
            }
        finally:
            await redis.close()
    
    async def _check_postgresql_dependency(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check PostgreSQL dependency."""
        import time
        start_time = time.time()
        
        # Would need asyncpg or similar
        # For now, return a placeholder
        response_time = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy",  # Placeholder
            "message": "PostgreSQL check not implemented",
            "response_time_ms": response_time
        }
    
    async def _check_http_dependency(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check HTTP dependency."""
        import time
        import aiohttp
        
        start_time = time.time()
        url = config.get("url")
        timeout = config.get("timeout", 5.0)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    return {
                        "status": "healthy",
                        "message": f"HTTP endpoint responding (status: {response.status})",
                        "response_time_ms": response_time
                    }
                elif 200 <= response.status < 400:
                    return {
                        "status": "degraded",
                        "message": f"HTTP endpoint responding with status {response.status}",
                        "response_time_ms": response_time
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"HTTP endpoint returned status {response.status}",
                        "response_time_ms": response_time
                    }