#!/usr/bin/env python3
"""
MAOS Backend API Developer Example

This example demonstrates how to use the MAOS orchestration system as a backend API
for building scalable, distributed applications with multi-agent coordination.

Features demonstrated:
1. System initialization and configuration
2. RESTful API server setup
3. Task orchestration patterns
4. Agent lifecycle management
5. Resource allocation strategies
6. Error handling and monitoring
7. Claude Code integration
8. Production deployment patterns
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uvicorn import run as uvicorn_run

# MAOS imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from maos.core.orchestrator import Orchestrator
from maos.core.task_planner import TaskPlanner, DecompositionStrategy
from maos.core.agent_manager import AgentManager
from maos.core.resource_allocator import ResourceAllocator
from maos.interfaces.state_manager import InMemoryStateManager
from maos.utils.message_bus import InMemoryMessageBus
from maos.api.schemas import (
    TaskSubmissionRequest, TaskResponse, AgentCreateRequest, AgentResponse,
    SystemStatusResponse, MetricsResponse, TaskStatusAPI, AgentCapabilityAPI
)
from maos.api.claude_integration import ClaudeTaskIntegration
from maos.models.task import TaskPriority, Task
from maos.models.agent import AgentCapability
from maos.utils.logging_config import MAOSLogger
from maos.utils.exceptions import MAOSError, TaskError, OrchestrationError

# Configuration
class APIConfig:
    """API configuration settings."""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8000
        self.debug = False
        self.workers = 4
        self.max_agents = 100
        self.max_concurrent_tasks = 1000
        self.enable_cors = True
        self.cors_origins = ["*"]
        self.api_prefix = "/api/v1"
        self.docs_url = "/docs"
        self.redoc_url = "/redoc"
        
        # MAOS configuration
        self.orchestrator_config = {
            "max_execution_plans": 1000,
            "cleanup_interval": 300,
            "health_check_interval": 60,
        }
        
        # Task configuration
        self.default_task_timeout = 300
        self.max_task_timeout = 3600
        self.default_max_retries = 3
        
        # Resource limits
        self.default_resources = {
            "cpu_cores": 100.0,
            "memory_mb": 32768.0,
            "disk_mb": 102400.0,
            "network_mbps": 1000.0
        }


# Global instances
orchestrator: Orchestrator = None
logger: MAOSLogger = None
config = APIConfig()
claude_integration: ClaudeTaskIntegration = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await startup_orchestrator()
    logger.logger.info("MAOS API Server started successfully")
    
    yield
    
    # Shutdown
    await shutdown_orchestrator()
    logger.logger.info("MAOS API Server shut down gracefully")


async def startup_orchestrator():
    """Initialize and start the MAOS orchestrator."""
    global orchestrator, logger, claude_integration
    
    try:
        # Initialize logger
        logger = MAOSLogger("maos_api", "backend_api_example")
        logger.logger.info("Initializing MAOS orchestrator...")
        
        # Create components
        state_manager = InMemoryStateManager()
        message_bus = InMemoryMessageBus()
        
        task_planner = TaskPlanner(
            state_manager=state_manager,
            message_bus=message_bus
        )
        
        agent_manager = AgentManager(
            state_manager=state_manager,
            message_bus=message_bus,
            max_agents=config.max_agents
        )
        
        resource_allocator = ResourceAllocator(
            state_manager=state_manager,
            message_bus=message_bus
        )
        
        # Create orchestrator
        orchestrator = Orchestrator(
            task_planner=task_planner,
            agent_manager=agent_manager,
            resource_allocator=resource_allocator,
            state_manager=state_manager,
            message_bus=message_bus,
            **config.orchestrator_config
        )
        
        # Start orchestrator
        await orchestrator.start()
        
        # Initialize default resources
        for resource_type, capacity in config.default_resources.items():
            await resource_allocator.add_resource(
                resource_type=resource_type,
                capacity=capacity,
                metadata={"source": "default_pool"}
            )
        
        # Create Claude Code integration
        claude_integration = ClaudeTaskIntegration(orchestrator)
        
        # Create some default agents
        await create_default_agents()
        
        logger.logger.info("MAOS orchestrator initialized successfully")
        
    except Exception as e:
        logger.log_error(e, {"operation": "startup_orchestrator"})
        raise


async def shutdown_orchestrator():
    """Shutdown the MAOS orchestrator gracefully."""
    global orchestrator
    
    try:
        if orchestrator:
            await orchestrator.stop()
            logger.logger.info("Orchestrator stopped gracefully")
    except Exception as e:
        logger.log_error(e, {"operation": "shutdown_orchestrator"})


async def create_default_agents():
    """Create default agents for common task types."""
    
    default_agents = [
        {
            "agent_type": "data_processor",
            "capabilities": {AgentCapability.DATA_PROCESSING, AgentCapability.COMPUTATION},
            "count": 3
        },
        {
            "agent_type": "api_handler", 
            "capabilities": {AgentCapability.API_INTEGRATION, AgentCapability.COMMUNICATION},
            "count": 2
        },
        {
            "agent_type": "file_operator",
            "capabilities": {AgentCapability.FILE_OPERATIONS},
            "count": 2
        },
        {
            "agent_type": "coordinator",
            "capabilities": {AgentCapability.COORDINATION, AgentCapability.MONITORING},
            "count": 1
        },
        {
            "agent_type": "general_purpose",
            "capabilities": {AgentCapability.TASK_EXECUTION},
            "count": 5
        }
    ]
    
    for agent_spec in default_agents:
        for i in range(agent_spec["count"]):
            try:
                await orchestrator.create_agent(
                    agent_type=f"{agent_spec['agent_type']}_{i+1}",
                    capabilities=agent_spec["capabilities"],
                    configuration={"auto_created": True}
                )
            except Exception as e:
                logger.log_error(e, {
                    "operation": "create_default_agent",
                    "agent_type": agent_spec["agent_type"]
                })


# FastAPI app creation
app = FastAPI(
    title="MAOS Orchestration API",
    description="Multi-Agent Orchestration System REST API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=config.docs_url,
    redoc_url=config.redoc_url
)

# Add CORS middleware
if config.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Dependency injection
async def get_orchestrator() -> Orchestrator:
    """Get orchestrator instance."""
    if not orchestrator:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Orchestrator not initialized"
        )
    return orchestrator


async def get_claude_integration() -> ClaudeTaskIntegration:
    """Get Claude integration instance."""
    if not claude_integration:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Claude integration not initialized"
        )
    return claude_integration


# Error handlers
@app.exception_handler(MAOSError)
async def maos_error_handler(request, exc: MAOSError):
    """Handle MAOS-specific errors."""
    logger.log_error(exc, {"request_path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": str(exc),
            "error_type": type(exc).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_error_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.log_error(exc, {"request_path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_type": type(exc).__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MAOS API"
    }


@app.get("/health/detailed")
async def detailed_health_check(
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Detailed health check with component status."""
    try:
        health = await orchestrator.get_component_health()
        status = await orchestrator.get_system_status()
        
        return {
            "status": "healthy" if all(h["healthy"] for h in health.values()) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": status["uptime_seconds"],
            "components": health,
            "active_executions": status["active_executions"]
        }
    except Exception as e:
        logger.log_error(e, {"operation": "detailed_health_check"})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed"
        )


# Task management endpoints
@app.post(f"{config.api_prefix}/tasks", response_model=TaskResponse)
async def submit_task(
    request: TaskSubmissionRequest,
    background_tasks: BackgroundTasks,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Submit a new task for orchestration."""
    try:
        # Validate timeout
        if request.timeout_seconds > config.max_task_timeout:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Timeout exceeds maximum allowed ({config.max_task_timeout}s)"
            )
        
        # Create task
        task = Task(
            name=request.name,
            description=request.description,
            priority=TaskPriority[request.priority.upper()],
            parameters=request.parameters,
            timeout_seconds=request.timeout_seconds,
            max_retries=request.max_retries,
            resource_requirements=request.resource_requirements,
            tags=request.tags,
            metadata=request.metadata
        )
        
        # Submit to orchestrator
        execution_plan = await orchestrator.submit_task(
            task=task,
            decomposition_strategy=request.decomposition_strategy or "hierarchical"
        )
        
        # Convert to API schema
        from maos.api.schemas import TaskSchema
        task_schema = TaskSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            status=TaskStatusAPI(task.status.value),
            priority=request.priority,
            agent_id=task.agent_id,
            parent_task_id=task.parent_task_id,
            dependencies=[],
            subtasks=task.subtasks,
            parameters=task.parameters,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            updated_at=task.updated_at,
            timeout_seconds=task.timeout_seconds,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            resource_requirements=task.resource_requirements,
            tags=task.tags,
            metadata=task.metadata
        )
        
        logger.logger.info(
            f"Task submitted successfully",
            extra={
                "task_id": str(task.id),
                "execution_plan_id": str(execution_plan.id)
            }
        )
        
        return TaskResponse(
            task=task_schema,
            execution_plan_id=execution_plan.id,
            message="Task submitted successfully"
        )
        
    except Exception as e:
        logger.log_error(e, {
            "operation": "submit_task",
            "task_name": request.name
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit task"
        )


@app.get(f"{config.api_prefix}/tasks/{{task_id}}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get task by ID."""
    try:
        from uuid import UUID
        task_uuid = UUID(task_id)
        
        task = await orchestrator.get_task(task_uuid)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Convert to API schema
        from maos.api.schemas import TaskSchema
        task_schema = TaskSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            status=TaskStatusAPI(task.status.value),
            priority=task.priority.name.lower(),
            agent_id=task.agent_id,
            parent_task_id=task.parent_task_id,
            dependencies=[],
            subtasks=task.subtasks,
            parameters=task.parameters,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            updated_at=task.updated_at,
            timeout_seconds=task.timeout_seconds,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            resource_requirements=task.resource_requirements,
            tags=task.tags,
            metadata=task.metadata
        )
        
        return TaskResponse(
            task=task_schema,
            message="Task retrieved successfully"
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    except Exception as e:
        logger.log_error(e, {
            "operation": "get_task",
            "task_id": task_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task"
        )


@app.delete(f"{config.api_prefix}/tasks/{{task_id}}")
async def cancel_task(
    task_id: str,
    reason: str = "Cancelled via API",
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Cancel a task."""
    try:
        from uuid import UUID
        task_uuid = UUID(task_id)
        
        success = await orchestrator.cancel_task(task_uuid, reason)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or cannot be cancelled"
            )
        
        return {
            "message": "Task cancelled successfully",
            "task_id": task_id,
            "reason": reason
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID format"
        )
    except Exception as e:
        logger.log_error(e, {
            "operation": "cancel_task",
            "task_id": task_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel task"
        )


# Agent management endpoints
@app.post(f"{config.api_prefix}/agents", response_model=AgentResponse)
async def create_agent(
    request: AgentCreateRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Create a new agent."""
    try:
        # Convert API capabilities to model capabilities
        capabilities = {AgentCapability[cap.value.upper()] for cap in request.capabilities}
        
        agent = await orchestrator.create_agent(
            agent_type=request.agent_type,
            capabilities=capabilities,
            configuration=request.configuration
        )
        
        # Convert to API schema
        from maos.api.schemas import AgentSchema, AgentMetricsSchema
        agent_schema = AgentSchema(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            status=agent.status.value,
            capabilities={AgentCapabilityAPI(cap.value.lower()) for cap in agent.capabilities},
            current_task_id=agent.current_task_id,
            task_queue=agent.task_queue,
            max_concurrent_tasks=agent.max_concurrent_tasks,
            resource_limits=agent.resource_limits,
            configuration=agent.configuration,
            metadata=agent.metadata,
            created_at=agent.created_at,
            started_at=agent.started_at,
            last_seen=agent.last_seen,
            metrics=AgentMetricsSchema(
                tasks_completed=agent.metrics.tasks_completed,
                tasks_failed=agent.metrics.tasks_failed,
                total_execution_time=agent.metrics.total_execution_time,
                average_execution_time=agent.metrics.average_execution_time,
                cpu_usage_percent=agent.metrics.cpu_usage_percent,
                memory_usage_mb=agent.metrics.memory_usage_mb,
                success_rate=agent.metrics.success_rate,
                last_heartbeat=agent.metrics.last_heartbeat,
                health_score=agent.metrics.health_score
            ),
            tags=agent.tags,
            health_check_interval=agent.health_check_interval,
            heartbeat_timeout=agent.heartbeat_timeout
        )
        
        return AgentResponse(
            agent=agent_schema,
            message="Agent created successfully"
        )
        
    except Exception as e:
        logger.log_error(e, {
            "operation": "create_agent",
            "agent_type": request.agent_type
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent"
        )


# System monitoring endpoints
@app.get(f"{config.api_prefix}/system/status", response_model=SystemStatusResponse)
async def get_system_status(
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get system status."""
    try:
        status = await orchestrator.get_system_status()
        
        return SystemStatusResponse(
            running=status["running"],
            uptime_seconds=status["uptime_seconds"],
            startup_time=status.get("startup_time"),
            components=status["components"],
            active_executions=status["active_executions"],
            execution_plans=status["execution_plans"],
            total_tasks=status["total_tasks"],
            total_agents=status["total_agents"],
            total_resources=status["total_resources"]
        )
        
    except Exception as e:
        logger.log_error(e, {"operation": "get_system_status"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system status"
        )


@app.get(f"{config.api_prefix}/system/metrics", response_model=MetricsResponse)
async def get_system_metrics(
    orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Get system metrics."""
    try:
        metrics = await orchestrator.get_system_metrics()
        
        return MetricsResponse(
            orchestrator=metrics["orchestrator"],
            task_planner=metrics["task_planner"],
            agent_manager=metrics["agent_manager"],
            resource_allocator=metrics["resource_allocator"],
            state_manager=metrics["state_manager"],
            message_bus=metrics["message_bus"]
        )
        
    except Exception as e:
        logger.log_error(e, {"operation": "get_system_metrics"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics"
        )


# Claude Code integration endpoints
@app.post(f"{config.api_prefix}/claude/tasks")
async def submit_claude_task(
    task_spec: Dict[str, Any],
    background_tasks: BackgroundTasks,
    claude_integration: ClaudeTaskIntegration = Depends(get_claude_integration)
):
    """Submit a task from Claude Code."""
    try:
        # Submit task to Claude integration
        claude_task_id = await claude_integration.submit_task(task_spec)
        
        return {
            "claude_task_id": claude_task_id,
            "message": "Claude task submitted successfully",
            "submitted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.log_error(e, {
            "operation": "submit_claude_task",
            "task_spec": task_spec
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit Claude task"
        )


@app.get(f"{config.api_prefix}/claude/tasks/{{claude_task_id}}")
async def get_claude_task_status(
    claude_task_id: str,
    claude_integration: ClaudeTaskIntegration = Depends(get_claude_integration)
):
    """Get Claude task status."""
    try:
        status = await claude_integration.get_task_status(claude_task_id)
        return status
        
    except TaskError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.log_error(e, {
            "operation": "get_claude_task_status",
            "claude_task_id": claude_task_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Claude task status"
        )


@app.get(f"{config.api_prefix}/claude/orchestrator/status")
async def get_claude_orchestrator_status(
    claude_integration: ClaudeTaskIntegration = Depends(get_claude_integration)
):
    """Get orchestrator status for Claude Code."""
    try:
        status = await claude_integration.get_orchestrator_status()
        return status
        
    except Exception as e:
        logger.log_error(e, {"operation": "get_claude_orchestrator_status"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get orchestrator status"
        )


# Background task cleanup
async def cleanup_task():
    """Periodic cleanup task."""
    try:
        if claude_integration:
            # Clean up old completed tasks
            cleaned_count = await claude_integration.cleanup_completed_tasks(max_age_hours=24)
            logger.logger.info(f"Cleaned up {cleaned_count} completed tasks")
        
        if orchestrator:
            # Perform orchestrator cleanup
            await orchestrator._cleanup_completed_executions()
            logger.logger.debug("Performed orchestrator cleanup")
            
    except Exception as e:
        logger.log_error(e, {"operation": "cleanup_task"})


# Signal handlers
async def shutdown_handler():
    """Handle shutdown signals."""
    logger.logger.info("Received shutdown signal, stopping server...")
    await shutdown_orchestrator()


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        asyncio.create_task(shutdown_handler())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MAOS Backend API Server")
    parser.add_argument("--host", default=config.host, help="Server host")
    parser.add_argument("--port", type=int, default=config.port, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--workers", type=int, default=config.workers, help="Number of workers")
    args = parser.parse_args()
    
    # Update config
    config.host = args.host
    config.port = args.port
    config.debug = args.debug
    config.workers = args.workers
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Run server
    uvicorn_run(
        "backend_api_example:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        workers=1,  # Use 1 worker for development
        log_level="info" if not config.debug else "debug"
    )
