"""
Health Check REST API endpoints for MAOS monitoring.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError
from .health_manager import HealthManager


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status: healthy, degraded, unhealthy, unknown")
    message: str = Field(..., description="Human-readable status message")
    timestamp: str = Field(..., description="ISO timestamp of the check")
    components: Optional[Dict[str, Any]] = Field(None, description="Component health details")
    summary: Optional[Dict[str, int]] = Field(None, description="Summary statistics")


class ComponentHealthResponse(BaseModel):
    """Individual component health response."""
    component: str = Field(..., description="Component name")
    health: Dict[str, Any] = Field(..., description="Health details")
    dependencies: Optional[list] = Field(None, description="Component dependencies")


class HealthMetricsResponse(BaseModel):
    """Health metrics response."""
    system_metrics: Dict[str, float] = Field(..., description="System-level metrics")
    component_metrics: Dict[str, float] = Field(..., description="Component-specific metrics")
    timestamp: str = Field(..., description="Metrics collection timestamp")


class HealthHistoryResponse(BaseModel):
    """Health history response."""
    time_range_hours: int = Field(..., description="Time range in hours")
    data_points: int = Field(..., description="Number of data points")
    history: list = Field(..., description="Historical health data")


def create_health_router(health_manager: HealthManager) -> APIRouter:
    """
    Create FastAPI router for health check endpoints.
    
    Args:
        health_manager: Health manager instance
        
    Returns:
        FastAPI router with health endpoints
    """
    router = APIRouter(prefix="/health", tags=["health"])
    logger = MAOSLogger("health_api")
    
    @router.get(
        "/",
        response_model=HealthResponse,
        summary="Get overall system health",
        description="Returns the current health status of all MAOS components"
    )
    async def get_system_health() -> HealthResponse:
        """Get overall system health status."""
        try:
            health_data = await health_manager.get_health_status()
            
            return HealthResponse(
                status=health_data["system_status"],
                message=health_data["system_message"],
                timestamp=health_data["timestamp"],
                components=health_data.get("components"),
                summary=health_data.get("summary")
            )
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_system_health"})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get system health: {str(e)}"
            )
    
    @router.get(
        "/live",
        summary="Kubernetes liveness probe endpoint",
        description="Simple endpoint for Kubernetes liveness checks"
    )
    async def liveness_probe() -> Dict[str, Any]:
        """Liveness probe - checks if the service is running."""
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "maos-monitoring"
        }
    
    @router.get(
        "/ready",
        summary="Kubernetes readiness probe endpoint", 
        description="Checks if the service is ready to serve requests"
    )
    async def readiness_probe() -> Dict[str, Any]:
        """Readiness probe - checks if the service is ready."""
        try:
            health_data = await health_manager.get_health_status()
            is_ready = health_data["system_status"] in ["healthy", "degraded"]
            
            if is_ready:
                return {
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "system_status": health_data["system_status"]
                }
            else:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "status": "not_ready",
                        "timestamp": datetime.utcnow().isoformat(),
                        "system_status": health_data["system_status"],
                        "message": health_data["system_message"]
                    }
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.log_error(e, {"operation": "readiness_probe"})
            raise HTTPException(
                status_code=503,
                detail=f"Readiness check failed: {str(e)}"
            )
    
    @router.get(
        "/components/{component_name}",
        response_model=ComponentHealthResponse,
        summary="Get specific component health",
        description="Returns health status for a specific MAOS component"
    )
    async def get_component_health(component_name: str) -> ComponentHealthResponse:
        """Get health status for a specific component."""
        try:
            health_data = await health_manager.get_health_status(component_name)
            
            return ComponentHealthResponse(
                component=health_data["component"],
                health=health_data["health"],
                dependencies=health_data.get("dependencies")
            )
            
        except MAOSError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.log_error(e, {"operation": "get_component_health", "component": component_name})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get component health: {str(e)}"
            )
    
    @router.get(
        "/components",
        summary="List all monitored components",
        description="Returns a list of all components being monitored"
    )
    async def list_components() -> Dict[str, Any]:
        """List all monitored components."""
        try:
            components = health_manager.get_registered_components()
            health_data = await health_manager.get_health_status()
            
            component_summary = {}
            for component in components:
                if component in health_data.get("components", {}):
                    comp_health = health_data["components"][component]
                    component_summary[component] = {
                        "status": comp_health["status"],
                        "message": comp_health["message"],
                        "last_check": comp_health["last_check"]
                    }
                else:
                    component_summary[component] = {
                        "status": "unknown",
                        "message": "No health data available"
                    }
            
            return {
                "total_components": len(components),
                "components": component_summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.log_error(e, {"operation": "list_components"})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list components: {str(e)}"
            )
    
    @router.get(
        "/dependencies/{component_name}",
        summary="Get component dependencies",
        description="Returns dependency health status for a component"
    )
    async def get_component_dependencies(component_name: str) -> Dict[str, Any]:
        """Get dependency status for a component."""
        try:
            dependency_data = await health_manager.get_dependency_status(component_name)
            return dependency_data
            
        except MAOSError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.log_error(e, {"operation": "get_component_dependencies", "component": component_name})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get component dependencies: {str(e)}"
            )
    
    @router.post(
        "/check",
        summary="Perform immediate health check",
        description="Triggers an immediate health check for all or specific components"
    )
    async def perform_health_check(component: Optional[str] = Query(None, description="Specific component to check")) -> Dict[str, Any]:
        """Perform immediate health check."""
        try:
            result = await health_manager.perform_health_check(component)
            return result
            
        except MAOSError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.log_error(e, {"operation": "perform_health_check", "component": component})
            raise HTTPException(
                status_code=500,
                detail=f"Health check failed: {str(e)}"
            )
    
    @router.get(
        "/metrics",
        response_model=HealthMetricsResponse,
        summary="Get health metrics",
        description="Returns aggregated health metrics from all components"
    )
    async def get_health_metrics() -> HealthMetricsResponse:
        """Get aggregated health metrics."""
        try:
            metrics = health_manager.get_health_metrics()
            
            return HealthMetricsResponse(
                system_metrics=metrics.get("system_metrics", {}),
                component_metrics=metrics.get("component_metrics", {}),
                timestamp=metrics.get("timestamp", datetime.utcnow().isoformat())
            )
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_health_metrics"})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get health metrics: {str(e)}"
            )
    
    @router.get(
        "/history",
        response_model=HealthHistoryResponse,
        summary="Get health history",
        description="Returns historical health data for analysis"
    )
    async def get_health_history(
        hours: int = Query(1, ge=1, le=168, description="Hours of history to retrieve (max 168 = 1 week)")
    ) -> HealthHistoryResponse:
        """Get health history."""
        try:
            history = health_manager.get_health_history(hours)
            
            return HealthHistoryResponse(
                time_range_hours=hours,
                data_points=len(history),
                history=history
            )
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_health_history"})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get health history: {str(e)}"
            )
    
    @router.get(
        "/report",
        summary="Export comprehensive health report",
        description="Generates and returns a comprehensive health report"
    )
    async def export_health_report(
        hours: int = Query(24, ge=1, le=168, description="Hours of data to include in report")
    ) -> Dict[str, Any]:
        """Export comprehensive health report."""
        try:
            report_json = await health_manager.export_health_report(hours)
            report_data = json.loads(report_json)
            
            return report_data
            
        except Exception as e:
            logger.log_error(e, {"operation": "export_health_report"})
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate health report: {str(e)}"
            )
    
    @router.get(
        "/status",
        summary="Simple status endpoint",
        description="Returns simple OK/ERROR status for external monitoring"
    )
    async def get_simple_status() -> Dict[str, Any]:
        """Get simple status for external monitoring systems."""
        try:
            health_data = await health_manager.get_health_status()
            system_status = health_data["system_status"]
            
            # Map to simple OK/ERROR
            if system_status == "healthy":
                status = "OK"
                http_code = 200
            elif system_status == "degraded":
                status = "DEGRADED"
                http_code = 200  # Still serving requests
            else:
                status = "ERROR"
                http_code = 503
            
            response = {
                "status": status,
                "message": health_data["system_message"],
                "timestamp": datetime.utcnow().isoformat(),
                "components_total": health_data.get("summary", {}).get("total_components", 0),
                "components_healthy": health_data.get("summary", {}).get("healthy", 0)
            }
            
            if http_code != 200:
                raise HTTPException(status_code=http_code, detail=response)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.log_error(e, {"operation": "get_simple_status"})
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "ERROR",
                    "message": f"Status check failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    return router