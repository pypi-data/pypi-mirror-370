"""
REST API implementation for MAOS orchestration system.
"""

import asyncio
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError
import uvicorn

from ..core.orchestrator import Orchestrator
from ..models.task import TaskStatus, TaskPriority
from ..models.agent import AgentCapability
from ..models.resource import ResourceType
from ..utils.exceptions import MAOSError, TaskError, AgentError, ResourceError
from ..utils.logging_config import MAOSLogger

from .schemas import (
    TaskSubmissionRequest, TaskResponse, TaskSchema, TaskStatusAPI, TaskPriorityAPI,
    AgentCreateRequest, AgentResponse, AgentSchema, AgentStatusAPI, AgentCapabilityAPI,
    ResourceCreateRequest, ResourceResponse, ResourceSchema, ResourceTypeAPI,
    ResourceAllocationRequest, AllocationResponse,
    SystemStatusResponse, MetricsResponse, CheckpointResponse, CheckpointSchema,
    ErrorResponse, PaginationParams, PaginatedTaskResponse, PaginatedAgentResponse, PaginatedResourceResponse,
    TaskFilterParams, AgentFilterParams, ResourceFilterParams,
    BulkTaskOperation, BulkOperationResponse, HealthCheckResponse,
    ComponentConfig, ConfigurationResponse
)


class MAOSRestAPI:
    """
    REST API server for MAOS orchestration system.
    
    Provides RESTful endpoints for all orchestration operations including:
    - Task management (submit, monitor, control)
    - Agent management (create, monitor, control)
    - Resource management (create, allocate, monitor)
    - System monitoring and administration
    """
    
    def __init__(
        self,
        orchestrator: Orchestrator,
        title: str = "MAOS Orchestration API",
        version: str = "1.0.0",
        cors_origins: List[str] = None,
        trusted_hosts: List[str] = None
    ):
        """Initialize the REST API server."""
        self.orchestrator = orchestrator
        self.logger = MAOSLogger("rest_api", str(uuid4()))
        
        # Create FastAPI application
        self.app = FastAPI(
            title=title,
            version=version,
            description="Multi-Agent Orchestration System REST API",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Add middleware
        if cors_origins:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"]
            )
        
        if trusted_hosts:
            self.app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=trusted_hosts
            )
        
        # Setup exception handlers
        self._setup_exception_handlers()
        
        # Register routes
        self._register_routes()
    
    def _setup_exception_handlers(self) -> None:
        """Setup custom exception handlers."""
        
        @self.app.exception_handler(ValidationError)
        async def validation_exception_handler(request, exc):
            self.logger.logger.warning(f"Validation error: {exc}")
            return JSONResponse(
                status_code=422,
                content=ErrorResponse(
                    error="Validation failed",
                    details={"validation_errors": exc.errors()}
                ).dict()
            )
        
        @self.app.exception_handler(MAOSError)
        async def maos_exception_handler(request, exc):
            self.logger.logger.error(f"MAOS error: {exc}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error=str(exc),
                    error_code=getattr(exc, 'error_code', None),
                    details=getattr(exc, 'context', {})
                ).dict()
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request, exc):
            self.logger.log_error(exc, {'endpoint': str(request.url)})
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Internal server error",
                    error_code="INTERNAL_ERROR"
                ).dict()
            )
    
    def _register_routes(self) -> None:
        """Register all API routes."""
        
        # Health and status endpoints
        @self.app.get("/health", response_model=HealthCheckResponse)
        async def health_check():
            """Get system health status."""
            try:
                status = await self.orchestrator.get_system_status()
                health = await self.orchestrator.get_component_health()
                
                overall_status = "healthy"
                if not status['running']:
                    overall_status = "unhealthy"
                elif any(h != "healthy" for h in health.values()):
                    overall_status = "degraded"
                
                return HealthCheckResponse(
                    status=overall_status,
                    components=health,
                    uptime_seconds=status['uptime_seconds'],
                    version="1.0.0"
                )
            except Exception as e:
                raise HTTPException(status_code=503, detail=str(e))
        
        @self.app.get("/status", response_model=SystemStatusResponse)
        async def get_system_status():
            """Get detailed system status."""
            try:
                status = await self.orchestrator.get_system_status()
                
                # Get counts
                all_tasks = await self.orchestrator.state_manager.get_objects('tasks')
                all_agents = await self.orchestrator.state_manager.get_objects('agents') 
                all_resources = await self.orchestrator.state_manager.get_objects('resources')
                
                return SystemStatusResponse(
                    **status,
                    total_tasks=len(all_tasks),
                    total_agents=len(all_agents),
                    total_resources=len(all_resources)
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/metrics", response_model=MetricsResponse)
        async def get_system_metrics():
            """Get system performance metrics."""
            try:
                metrics = await self.orchestrator.get_system_metrics()
                return MetricsResponse(**metrics)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Task management endpoints
        @self.app.post("/tasks", response_model=TaskResponse, status_code=201)
        async def submit_task(request: TaskSubmissionRequest):
            """Submit a new task for execution."""
            try:
                from ..models.task import Task, TaskPriority as ModelTaskPriority
                
                # Convert API enums to model enums
                priority_map = {
                    TaskPriorityAPI.LOW: ModelTaskPriority.LOW,
                    TaskPriorityAPI.MEDIUM: ModelTaskPriority.MEDIUM,
                    TaskPriorityAPI.HIGH: ModelTaskPriority.HIGH,
                    TaskPriorityAPI.CRITICAL: ModelTaskPriority.CRITICAL
                }
                
                task = Task(
                    name=request.name,
                    description=request.description or "",
                    priority=priority_map[request.priority],
                    parameters=request.parameters,
                    timeout_seconds=request.timeout_seconds,
                    max_retries=request.max_retries,
                    resource_requirements=request.resource_requirements,
                    tags=request.tags,
                    metadata=request.metadata
                )
                
                execution_plan = await self.orchestrator.submit_task(
                    task=task,
                    decomposition_strategy=request.decomposition_strategy
                )
                
                # Convert to API schema
                task_schema = self._convert_task_to_schema(task)
                
                return TaskResponse(
                    task=task_schema,
                    execution_plan_id=execution_plan.id,
                    message="Task submitted successfully"
                )
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'submit_task'})
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/tasks/{task_id}", response_model=TaskResponse)
        async def get_task(task_id: UUID = Path(..., description="Task ID")):
            """Get task details by ID."""
            try:
                task = await self.orchestrator.get_task(task_id)
                if not task:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                task_schema = self._convert_task_to_schema(task)
                return TaskResponse(task=task_schema)
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks", response_model=PaginatedTaskResponse)
        async def list_tasks(
            pagination: PaginationParams = Depends(),
            filters: TaskFilterParams = Depends()
        ):
            """List tasks with filtering and pagination."""
            try:
                all_tasks = await self.orchestrator.state_manager.get_objects('tasks')
                
                # Apply filters
                filtered_tasks = self._apply_task_filters(all_tasks, filters)
                
                # Apply pagination
                total_items = len(filtered_tasks)
                total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
                start_idx = (pagination.page - 1) * pagination.page_size
                end_idx = start_idx + pagination.page_size
                page_tasks = filtered_tasks[start_idx:end_idx]
                
                # Convert to schemas
                task_schemas = [self._convert_task_to_schema(task) for task in page_tasks]
                
                return PaginatedTaskResponse(
                    items=task_schemas,
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_items=total_items,
                    total_pages=total_pages,
                    has_next=pagination.page < total_pages,
                    has_previous=pagination.page > 1
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/tasks/{task_id}/cancel")
        async def cancel_task(
            task_id: UUID = Path(..., description="Task ID"),
            reason: str = Body(default="Manual cancellation", embed=True)
        ):
            """Cancel a running task."""
            try:
                success = await self.orchestrator.cancel_task(task_id, reason)
                if not success:
                    raise HTTPException(status_code=400, detail="Task could not be cancelled")
                
                return {"message": "Task cancelled successfully", "task_id": str(task_id)}
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/tasks/{task_id}/retry")
        async def retry_task(task_id: UUID = Path(..., description="Task ID")):
            """Retry a failed task."""
            try:
                success = await self.orchestrator.retry_task(task_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Task cannot be retried")
                
                return {"message": "Task retry initiated", "task_id": str(task_id)}
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks/{task_id}/results")
        async def get_task_results(task_id: UUID = Path(..., description="Task ID")):
            """Get task execution results."""
            try:
                results = await self.orchestrator.get_task_results(task_id)
                if results is None:
                    raise HTTPException(status_code=404, detail="Task results not available")
                
                return {"task_id": str(task_id), "results": results}
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Agent management endpoints
        @self.app.post("/agents", response_model=AgentResponse, status_code=201)
        async def create_agent(request: AgentCreateRequest):
            """Create a new agent."""
            try:
                from ..models.agent import AgentCapability as ModelAgentCapability
                
                # Convert API capabilities to model capabilities
                capability_map = {
                    AgentCapabilityAPI.TASK_EXECUTION: ModelAgentCapability.TASK_EXECUTION,
                    AgentCapabilityAPI.DATA_PROCESSING: ModelAgentCapability.DATA_PROCESSING,
                    AgentCapabilityAPI.API_INTEGRATION: ModelAgentCapability.API_INTEGRATION,
                    AgentCapabilityAPI.FILE_OPERATIONS: ModelAgentCapability.FILE_OPERATIONS,
                    AgentCapabilityAPI.COMPUTATION: ModelAgentCapability.COMPUTATION,
                    AgentCapabilityAPI.COMMUNICATION: ModelAgentCapability.COMMUNICATION,
                    AgentCapabilityAPI.MONITORING: ModelAgentCapability.MONITORING,
                    AgentCapabilityAPI.COORDINATION: ModelAgentCapability.COORDINATION
                }
                
                model_capabilities = {
                    capability_map[cap] for cap in request.capabilities
                    if cap in capability_map
                }
                
                agent = await self.orchestrator.create_agent(
                    agent_type=request.agent_type,
                    capabilities=model_capabilities,
                    configuration=request.configuration
                )
                
                # Set additional properties
                if request.max_concurrent_tasks != 1:
                    agent.max_concurrent_tasks = request.max_concurrent_tasks
                if request.resource_limits:
                    agent.resource_limits = request.resource_limits
                if request.tags:
                    agent.tags = request.tags
                
                agent_schema = self._convert_agent_to_schema(agent)
                
                return AgentResponse(
                    agent=agent_schema,
                    message="Agent created successfully"
                )
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'create_agent'})
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/agents/{agent_id}", response_model=AgentResponse)
        async def get_agent(agent_id: UUID = Path(..., description="Agent ID")):
            """Get agent details by ID."""
            try:
                agent = await self.orchestrator.get_agent(agent_id)
                if not agent:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                agent_schema = self._convert_agent_to_schema(agent)
                return AgentResponse(agent=agent_schema)
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents", response_model=PaginatedAgentResponse)
        async def list_agents(
            pagination: PaginationParams = Depends(),
            filters: AgentFilterParams = Depends()
        ):
            """List agents with filtering and pagination."""
            try:
                if filters.available_only:
                    all_agents = await self.orchestrator.get_available_agents()
                else:
                    all_agents = await self.orchestrator.state_manager.get_objects('agents')
                
                # Apply additional filters
                filtered_agents = self._apply_agent_filters(all_agents, filters)
                
                # Apply pagination
                total_items = len(filtered_agents)
                total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
                start_idx = (pagination.page - 1) * pagination.page_size
                end_idx = start_idx + pagination.page_size
                page_agents = filtered_agents[start_idx:end_idx]
                
                # Convert to schemas
                agent_schemas = [self._convert_agent_to_schema(agent) for agent in page_agents]
                
                return PaginatedAgentResponse(
                    items=agent_schemas,
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_items=total_items,
                    total_pages=total_pages,
                    has_next=pagination.page < total_pages,
                    has_previous=pagination.page > 1
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/agents/{agent_id}")
        async def terminate_agent(
            agent_id: UUID = Path(..., description="Agent ID"),
            reason: str = Body(default="Manual termination", embed=True)
        ):
            """Terminate an agent."""
            try:
                success = await self.orchestrator.terminate_agent(agent_id, reason)
                if not success:
                    raise HTTPException(status_code=400, detail="Agent could not be terminated")
                
                return {"message": "Agent terminated successfully", "agent_id": str(agent_id)}
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Resource management endpoints
        @self.app.post("/resources", response_model=ResourceResponse, status_code=201)
        async def create_resource(request: ResourceCreateRequest):
            """Create a new resource."""
            try:
                from ..models.resource import ResourceType as ModelResourceType
                
                # Convert API resource type to model resource type
                type_map = {
                    ResourceTypeAPI.CPU: ModelResourceType.CPU,
                    ResourceTypeAPI.MEMORY: ModelResourceType.MEMORY,
                    ResourceTypeAPI.DISK: ModelResourceType.DISK,
                    ResourceTypeAPI.NETWORK: ModelResourceType.NETWORK,
                    ResourceTypeAPI.GPU: ModelResourceType.GPU,
                    ResourceTypeAPI.CUSTOM: ModelResourceType.CUSTOM
                }
                
                model_resource_type = type_map[request.resource_type]
                
                configuration = {
                    'name': request.name,
                    'unit': request.unit,
                    'location': request.location,
                    'cost_per_unit': request.cost_per_unit,
                    'metadata': request.metadata,
                    'tags': request.tags
                }
                
                if request.minimum_allocation is not None:
                    configuration['minimum_allocation'] = request.minimum_allocation
                if request.maximum_allocation is not None:
                    configuration['maximum_allocation'] = request.maximum_allocation
                
                resource = await self.orchestrator.create_resource(
                    resource_type=model_resource_type,
                    capacity=request.capacity,
                    configuration=configuration
                )
                
                resource_schema = self._convert_resource_to_schema(resource)
                
                return ResourceResponse(
                    resource=resource_schema,
                    message="Resource created successfully"
                )
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'create_resource'})
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/resources/{resource_id}", response_model=ResourceResponse)
        async def get_resource(resource_id: UUID = Path(..., description="Resource ID")):
            """Get resource details by ID."""
            try:
                resource = await self.orchestrator.get_resource(resource_id)
                if not resource:
                    raise HTTPException(status_code=404, detail="Resource not found")
                
                resource_schema = self._convert_resource_to_schema(resource)
                return ResourceResponse(resource=resource_schema)
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/resources", response_model=PaginatedResourceResponse)
        async def list_resources(
            pagination: PaginationParams = Depends(),
            filters: ResourceFilterParams = Depends()
        ):
            """List resources with filtering and pagination."""
            try:
                all_resources = await self.orchestrator.state_manager.get_objects('resources')
                
                # Apply filters
                filtered_resources = self._apply_resource_filters(all_resources, filters)
                
                # Apply pagination
                total_items = len(filtered_resources)
                total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
                start_idx = (pagination.page - 1) * pagination.page_size
                end_idx = start_idx + pagination.page_size
                page_resources = filtered_resources[start_idx:end_idx]
                
                # Convert to schemas
                resource_schemas = [self._convert_resource_to_schema(resource) for resource in page_resources]
                
                return PaginatedResourceResponse(
                    items=resource_schemas,
                    page=pagination.page,
                    page_size=pagination.page_size,
                    total_items=total_items,
                    total_pages=total_pages,
                    has_next=pagination.page < total_pages,
                    has_previous=pagination.page > 1
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/resources/allocate", response_model=AllocationResponse)
        async def allocate_resources(request: ResourceAllocationRequest):
            """Allocate resources for a requester."""
            try:
                from ..models.task import TaskPriority as ModelTaskPriority
                
                # Convert API priority to model priority
                priority_map = {
                    TaskPriorityAPI.LOW: ModelTaskPriority.LOW,
                    TaskPriorityAPI.MEDIUM: ModelTaskPriority.MEDIUM,
                    TaskPriorityAPI.HIGH: ModelTaskPriority.HIGH,
                    TaskPriorityAPI.CRITICAL: ModelTaskPriority.CRITICAL
                }
                
                requester_id = uuid4()  # Generate requester ID
                
                request_id = await self.orchestrator.request_resources(
                    requester_id=requester_id,
                    resource_requirements=request.resource_requirements,
                    priority=priority_map[request.priority]
                )
                
                # Wait briefly for allocation processing
                await asyncio.sleep(0.1)
                
                return AllocationResponse(
                    request_id=request_id,
                    status="requested",
                    message="Resource allocation requested"
                )
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'allocate_resources'})
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.delete("/resources/allocations/{requester_id}")
        async def release_resources(requester_id: UUID = Path(..., description="Requester ID")):
            """Release allocated resources for a requester."""
            try:
                released_amount = await self.orchestrator.release_resources(requester_id)
                
                return {
                    "message": "Resources released successfully",
                    "requester_id": str(requester_id),
                    "released_amount": released_amount
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Checkpoint management endpoints
        @self.app.post("/checkpoints", response_model=CheckpointResponse, status_code=201)
        async def create_checkpoint(name: str = Body(default="api_checkpoint", embed=True)):
            """Create a system checkpoint."""
            try:
                checkpoint_id = await self.orchestrator.create_checkpoint(name)
                
                # Get checkpoint details
                checkpoints = await self.orchestrator.list_checkpoints()
                checkpoint_data = next(
                    (cp for cp in checkpoints if cp['id'] == str(checkpoint_id)),
                    None
                )
                
                if checkpoint_data:
                    checkpoint_schema = CheckpointSchema(**checkpoint_data)
                    return CheckpointResponse(
                        checkpoint=checkpoint_schema,
                        message="Checkpoint created successfully"
                    )
                else:
                    return CheckpointResponse(
                        message="Checkpoint created but details not available"
                    )
                
            except Exception as e:
                self.logger.log_error(e, {'operation': 'create_checkpoint'})
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/checkpoints", response_model=CheckpointResponse)
        async def list_checkpoints():
            """List all available checkpoints."""
            try:
                checkpoints_data = await self.orchestrator.list_checkpoints()
                checkpoint_schemas = [CheckpointSchema(**cp) for cp in checkpoints_data]
                
                return CheckpointResponse(
                    checkpoints=checkpoint_schemas,
                    message=f"Found {len(checkpoint_schemas)} checkpoints"
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/checkpoints/{checkpoint_id}/restore")
        async def restore_checkpoint(checkpoint_id: UUID = Path(..., description="Checkpoint ID")):
            """Restore system state from a checkpoint."""
            try:
                success = await self.orchestrator.restore_checkpoint(checkpoint_id)
                if not success:
                    raise HTTPException(status_code=400, detail="Checkpoint could not be restored")
                
                return {"message": "Checkpoint restored successfully", "checkpoint_id": str(checkpoint_id)}
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    # Helper methods for data conversion
    def _convert_task_to_schema(self, task) -> TaskSchema:
        """Convert task model to API schema."""
        from ..models.task import TaskStatus as ModelTaskStatus, TaskPriority as ModelTaskPriority
        
        # Convert model enums to API enums
        status_map = {
            ModelTaskStatus.PENDING: TaskStatusAPI.PENDING,
            ModelTaskStatus.READY: TaskStatusAPI.READY,
            ModelTaskStatus.RUNNING: TaskStatusAPI.RUNNING,
            ModelTaskStatus.COMPLETED: TaskStatusAPI.COMPLETED,
            ModelTaskStatus.FAILED: TaskStatusAPI.FAILED,
            ModelTaskStatus.CANCELLED: TaskStatusAPI.CANCELLED,
            ModelTaskStatus.RETRYING: TaskStatusAPI.RETRYING
        }
        
        priority_map = {
            ModelTaskPriority.LOW: TaskPriorityAPI.LOW,
            ModelTaskPriority.MEDIUM: TaskPriorityAPI.MEDIUM,
            ModelTaskPriority.HIGH: TaskPriorityAPI.HIGH,
            ModelTaskPriority.CRITICAL: TaskPriorityAPI.CRITICAL
        }
        
        return TaskSchema(
            id=task.id,
            name=task.name,
            description=task.description,
            status=status_map[task.status],
            priority=priority_map[task.priority],
            agent_id=task.agent_id,
            parent_task_id=task.parent_task_id,
            dependencies=[
                {
                    'task_id': dep.task_id,
                    'dependency_type': dep.dependency_type,
                    'required': dep.required,
                    'metadata': dep.metadata
                }
                for dep in task.dependencies
            ],
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
    
    def _convert_agent_to_schema(self, agent) -> AgentSchema:
        """Convert agent model to API schema."""
        from ..models.agent import AgentStatus as ModelAgentStatus, AgentCapability as ModelAgentCapability
        
        # Convert model enums to API enums
        status_map = {
            ModelAgentStatus.INITIALIZING: AgentStatusAPI.INITIALIZING,
            ModelAgentStatus.IDLE: AgentStatusAPI.IDLE,
            ModelAgentStatus.BUSY: AgentStatusAPI.BUSY,
            ModelAgentStatus.OVERLOADED: AgentStatusAPI.OVERLOADED,
            ModelAgentStatus.UNHEALTHY: AgentStatusAPI.UNHEALTHY,
            ModelAgentStatus.OFFLINE: AgentStatusAPI.OFFLINE,
            ModelAgentStatus.TERMINATED: AgentStatusAPI.TERMINATED
        }
        
        capability_map = {
            ModelAgentCapability.TASK_EXECUTION: AgentCapabilityAPI.TASK_EXECUTION,
            ModelAgentCapability.DATA_PROCESSING: AgentCapabilityAPI.DATA_PROCESSING,
            ModelAgentCapability.API_INTEGRATION: AgentCapabilityAPI.API_INTEGRATION,
            ModelAgentCapability.FILE_OPERATIONS: AgentCapabilityAPI.FILE_OPERATIONS,
            ModelAgentCapability.COMPUTATION: AgentCapabilityAPI.COMPUTATION,
            ModelAgentCapability.COMMUNICATION: AgentCapabilityAPI.COMMUNICATION,
            ModelAgentCapability.MONITORING: AgentCapabilityAPI.MONITORING,
            ModelAgentCapability.COORDINATION: AgentCapabilityAPI.COORDINATION
        }
        
        api_capabilities = {
            capability_map[cap] for cap in agent.capabilities
            if cap in capability_map
        }
        
        return AgentSchema(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            status=status_map[agent.status],
            capabilities=api_capabilities,
            current_task_id=agent.current_task_id,
            task_queue=agent.task_queue,
            max_concurrent_tasks=agent.max_concurrent_tasks,
            resource_limits=agent.resource_limits,
            configuration=agent.configuration,
            metadata=agent.metadata,
            created_at=agent.created_at,
            started_at=agent.started_at,
            last_seen=agent.last_seen,
            metrics=agent.metrics,
            tags=agent.tags,
            health_check_interval=agent.health_check_interval,
            heartbeat_timeout=agent.heartbeat_timeout
        )
    
    def _convert_resource_to_schema(self, resource) -> ResourceSchema:
        """Convert resource model to API schema."""
        from ..models.resource import ResourceType as ModelResourceType
        
        # Convert model resource type to API resource type
        type_map = {
            ModelResourceType.CPU: ResourceTypeAPI.CPU,
            ModelResourceType.MEMORY: ResourceTypeAPI.MEMORY,
            ModelResourceType.DISK: ResourceTypeAPI.DISK,
            ModelResourceType.NETWORK: ResourceTypeAPI.NETWORK,
            ModelResourceType.GPU: ResourceTypeAPI.GPU,
            ModelResourceType.CUSTOM: ResourceTypeAPI.CUSTOM
        }
        
        return ResourceSchema(
            id=resource.id,
            name=resource.name,
            type=type_map[resource.type],
            total_capacity=resource.total_capacity,
            available_capacity=resource.available_capacity,
            allocated_capacity=resource.allocated_capacity,
            reserved_capacity=resource.reserved_capacity,
            unit=resource.unit,
            metadata=resource.metadata,
            created_at=resource.created_at,
            updated_at=resource.updated_at,
            allocations=[
                {
                    'agent_id': alloc.agent_id,
                    'amount': alloc.amount,
                    'allocated_at': alloc.allocated_at,
                    'released_at': alloc.released_at,
                    'metadata': alloc.metadata
                }
                for alloc in resource.allocations
            ],
            tags=resource.tags,
            location=resource.location,
            health_status=resource.health_status,
            performance_metrics=resource.performance_metrics,
            cost_per_unit=resource.cost_per_unit,
            minimum_allocation=resource.minimum_allocation,
            maximum_allocation=resource.maximum_allocation
        )
    
    def _apply_task_filters(self, tasks: List, filters: TaskFilterParams) -> List:
        """Apply filters to task list."""
        filtered_tasks = tasks
        
        if filters.status:
            from ..models.task import TaskStatus as ModelTaskStatus
            status_map = {
                TaskStatusAPI.PENDING: ModelTaskStatus.PENDING,
                TaskStatusAPI.READY: ModelTaskStatus.READY,
                TaskStatusAPI.RUNNING: ModelTaskStatus.RUNNING,
                TaskStatusAPI.COMPLETED: ModelTaskStatus.COMPLETED,
                TaskStatusAPI.FAILED: ModelTaskStatus.FAILED,
                TaskStatusAPI.CANCELLED: ModelTaskStatus.CANCELLED,
                TaskStatusAPI.RETRYING: ModelTaskStatus.RETRYING
            }
            model_status = status_map.get(filters.status)
            if model_status:
                filtered_tasks = [t for t in filtered_tasks if t.status == model_status]
        
        if filters.priority:
            from ..models.task import TaskPriority as ModelTaskPriority
            priority_map = {
                TaskPriorityAPI.LOW: ModelTaskPriority.LOW,
                TaskPriorityAPI.MEDIUM: ModelTaskPriority.MEDIUM,
                TaskPriorityAPI.HIGH: ModelTaskPriority.HIGH,
                TaskPriorityAPI.CRITICAL: ModelTaskPriority.CRITICAL
            }
            model_priority = priority_map.get(filters.priority)
            if model_priority:
                filtered_tasks = [t for t in filtered_tasks if t.priority == model_priority]
        
        if filters.agent_id:
            filtered_tasks = [t for t in filtered_tasks if t.agent_id == filters.agent_id]
        
        if filters.parent_task_id:
            filtered_tasks = [t for t in filtered_tasks if t.parent_task_id == filters.parent_task_id]
        
        if filters.tags:
            filtered_tasks = [
                t for t in filtered_tasks 
                if any(tag in t.tags for tag in filters.tags)
            ]
        
        if filters.created_after:
            filtered_tasks = [t for t in filtered_tasks if t.created_at >= filters.created_after]
        
        if filters.created_before:
            filtered_tasks = [t for t in filtered_tasks if t.created_at <= filters.created_before]
        
        if filters.search:
            search_lower = filters.search.lower()
            filtered_tasks = [
                t for t in filtered_tasks
                if search_lower in t.name.lower() or search_lower in (t.description or "").lower()
            ]
        
        return filtered_tasks
    
    def _apply_agent_filters(self, agents: List, filters: AgentFilterParams) -> List:
        """Apply filters to agent list."""
        filtered_agents = agents
        
        if filters.status:
            from ..models.agent import AgentStatus as ModelAgentStatus
            status_map = {
                AgentStatusAPI.INITIALIZING: ModelAgentStatus.INITIALIZING,
                AgentStatusAPI.IDLE: ModelAgentStatus.IDLE,
                AgentStatusAPI.BUSY: ModelAgentStatus.BUSY,
                AgentStatusAPI.OVERLOADED: ModelAgentStatus.OVERLOADED,
                AgentStatusAPI.UNHEALTHY: ModelAgentStatus.UNHEALTHY,
                AgentStatusAPI.OFFLINE: ModelAgentStatus.OFFLINE,
                AgentStatusAPI.TERMINATED: ModelAgentStatus.TERMINATED
            }
            model_status = status_map.get(filters.status)
            if model_status:
                filtered_agents = [a for a in filtered_agents if a.status == model_status]
        
        if filters.agent_type:
            filtered_agents = [a for a in filtered_agents if a.type == filters.agent_type]
        
        if filters.capabilities:
            from ..models.agent import AgentCapability as ModelAgentCapability
            capability_map = {
                AgentCapabilityAPI.TASK_EXECUTION: ModelAgentCapability.TASK_EXECUTION,
                AgentCapabilityAPI.DATA_PROCESSING: ModelAgentCapability.DATA_PROCESSING,
                AgentCapabilityAPI.API_INTEGRATION: ModelAgentCapability.API_INTEGRATION,
                AgentCapabilityAPI.FILE_OPERATIONS: ModelAgentCapability.FILE_OPERATIONS,
                AgentCapabilityAPI.COMPUTATION: ModelAgentCapability.COMPUTATION,
                AgentCapabilityAPI.COMMUNICATION: ModelAgentCapability.COMMUNICATION,
                AgentCapabilityAPI.MONITORING: ModelAgentCapability.MONITORING,
                AgentCapabilityAPI.COORDINATION: ModelAgentCapability.COORDINATION
            }
            
            required_capabilities = {
                capability_map[cap] for cap in filters.capabilities 
                if cap in capability_map
            }
            
            filtered_agents = [
                a for a in filtered_agents 
                if required_capabilities.issubset(a.capabilities)
            ]
        
        if filters.tags:
            filtered_agents = [
                a for a in filtered_agents 
                if any(tag in a.tags for tag in filters.tags)
            ]
        
        if filters.search:
            search_lower = filters.search.lower()
            filtered_agents = [
                a for a in filtered_agents
                if search_lower in a.name.lower() or search_lower in a.type.lower()
            ]
        
        return filtered_agents
    
    def _apply_resource_filters(self, resources: List, filters: ResourceFilterParams) -> List:
        """Apply filters to resource list."""
        filtered_resources = resources
        
        if filters.resource_type:
            from ..models.resource import ResourceType as ModelResourceType
            type_map = {
                ResourceTypeAPI.CPU: ModelResourceType.CPU,
                ResourceTypeAPI.MEMORY: ModelResourceType.MEMORY,
                ResourceTypeAPI.DISK: ModelResourceType.DISK,
                ResourceTypeAPI.NETWORK: ModelResourceType.NETWORK,
                ResourceTypeAPI.GPU: ModelResourceType.GPU,
                ResourceTypeAPI.CUSTOM: ModelResourceType.CUSTOM
            }
            model_type = type_map.get(filters.resource_type)
            if model_type:
                filtered_resources = [r for r in filtered_resources if r.type == model_type]
        
        if filters.location:
            filtered_resources = [r for r in filtered_resources if r.location == filters.location]
        
        if filters.health_status:
            filtered_resources = [r for r in filtered_resources if r.health_status == filters.health_status]
        
        if filters.tags:
            filtered_resources = [
                r for r in filtered_resources 
                if any(tag in r.tags for tag in filters.tags)
            ]
        
        if filters.min_available_capacity is not None:
            filtered_resources = [
                r for r in filtered_resources 
                if r.available_capacity >= filters.min_available_capacity
            ]
        
        if filters.search:
            search_lower = filters.search.lower()
            filtered_resources = [
                r for r in filtered_resources
                if search_lower in r.name.lower() or search_lower in r.location.lower()
            ]
        
        return filtered_resources
    
    async def start_server(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        reload: bool = False,
        log_level: str = "info"
    ) -> None:
        """Start the REST API server."""
        self.logger.logger.info(f"Starting MAOS REST API server on {host}:{port}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()


# Factory function for easy API creation
def create_api(orchestrator: Orchestrator, **kwargs) -> MAOSRestAPI:
    """Factory function to create MAOS REST API."""
    return MAOSRestAPI(orchestrator, **kwargs)