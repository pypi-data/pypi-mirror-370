# MAOS API Documentation

## Overview

The MAOS API provides comprehensive endpoints for task orchestration, agent management, and system monitoring. All APIs follow RESTful principles and return JSON responses.

**Base URL**: `https://api.maos.dev/v1`
**Authentication**: Bearer Token (JWT)
**Content-Type**: `application/json`

## OpenAPI Specification

```yaml
openapi: 3.0.3
info:
  title: MAOS API
  description: Multi-Agent Orchestration System REST API
  version: 1.0.0
  contact:
    name: MAOS Support
    email: support@maos.dev
    url: https://docs.maos.dev
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html

servers:
  - url: https://api.maos.dev/v1
    description: Production server
  - url: https://staging-api.maos.dev/v1
    description: Staging server
  - url: http://localhost:8000/v1
    description: Local development server

security:
  - BearerAuth: []

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Task:
      type: object
      required:
        - description
        - type
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
          example: "550e8400-e29b-41d4-a716-446655440000"
        description:
          type: string
          maxLength: 2000
          example: "Analyze customer sentiment from support tickets"
        type:
          type: string
          enum: [research, analysis, coding, testing, documentation]
          example: "analysis"
        priority:
          type: string
          enum: [LOW, MEDIUM, HIGH, CRITICAL]
          default: MEDIUM
          example: "HIGH"
        status:
          type: string
          enum: [QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED]
          readOnly: true
          example: "RUNNING"
        constraints:
          type: object
          properties:
            max_agents:
              type: integer
              minimum: 1
              maximum: 20
              default: 5
              example: 3
            timeout_seconds:
              type: integer
              minimum: 60
              maximum: 7200
              default: 1800
              example: 3600
            require_consensus:
              type: boolean
              default: false
              example: true
        metadata:
          type: object
          additionalProperties: true
          example:
            source: "api"
            user_id: "user123"
        created_at:
          type: string
          format: date-time
          readOnly: true
          example: "2025-08-11T10:30:00Z"
        started_at:
          type: string
          format: date-time
          readOnly: true
          example: "2025-08-11T10:30:05Z"
        completed_at:
          type: string
          format: date-time
          readOnly: true
          example: "2025-08-11T10:45:00Z"
        result:
          type: object
          readOnly: true
          properties:
            output:
              type: string
            artifacts:
              type: array
              items:
                type: string
            metrics:
              type: object

    Agent:
      type: object
      properties:
        id:
          type: string
          readOnly: true
          example: "agent_researcher_001"
        type:
          type: string
          enum: [researcher, coder, analyst, tester, coordinator]
          example: "researcher"
        status:
          type: string
          enum: [IDLE, BUSY, FAILED, TERMINATED]
          readOnly: true
          example: "BUSY"
        capabilities:
          type: array
          items:
            type: string
          example: ["web_search", "data_analysis", "report_generation"]
        current_task:
          type: string
          format: uuid
          nullable: true
          readOnly: true
          example: "550e8400-e29b-41d4-a716-446655440000"
        performance_metrics:
          type: object
          readOnly: true
          properties:
            tasks_completed:
              type: integer
              example: 42
            average_completion_time:
              type: number
              format: float
              example: 180.5
            success_rate:
              type: number
              format: float
              example: 0.95
        created_at:
          type: string
          format: date-time
          readOnly: true
          example: "2025-08-11T10:00:00Z"
        last_heartbeat:
          type: string
          format: date-time
          readOnly: true
          example: "2025-08-11T10:29:00Z"

    SystemStatus:
      type: object
      readOnly: true
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
          example: "healthy"
        version:
          type: string
          example: "1.0.0"
        uptime_seconds:
          type: integer
          example: 86400
        active_agents:
          type: integer
          example: 15
        queued_tasks:
          type: integer
          example: 3
        running_tasks:
          type: integer
          example: 8
        completed_tasks_today:
          type: integer
          example: 127
        system_resources:
          type: object
          properties:
            cpu_usage_percent:
              type: number
              format: float
              example: 45.2
            memory_usage_mb:
              type: integer
              example: 2048
            disk_usage_percent:
              type: number
              format: float
              example: 23.1

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: "TASK_NOT_FOUND"
            message:
              type: string
              example: "The requested task could not be found"
            details:
              type: object
              additionalProperties: true
            timestamp:
              type: string
              format: date-time
              example: "2025-08-11T10:30:00Z"

paths:
  /health:
    get:
      summary: System health check
      description: Returns the current health status of the MAOS system
      tags: [System]
      security: []
      responses:
        '200':
          description: System is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SystemStatus'

  /tasks:
    get:
      summary: List tasks
      description: Retrieve a paginated list of tasks with optional filtering
      tags: [Tasks]
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED]
          description: Filter by task status
        - name: type
          in: query
          schema:
            type: string
            enum: [research, analysis, coding, testing, documentation]
          description: Filter by task type
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
          description: Number of tasks to return
        - name: offset
          in: query
          schema:
            type: integer
            minimum: 0
            default: 0
          description: Number of tasks to skip
      responses:
        '200':
          description: List of tasks
          content:
            application/json:
              schema:
                type: object
                properties:
                  tasks:
                    type: array
                    items:
                      $ref: '#/components/schemas/Task'
                  total:
                    type: integer
                    example: 150
                  limit:
                    type: integer
                    example: 20
                  offset:
                    type: integer
                    example: 0
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    post:
      summary: Create a new task
      description: Submit a new task for execution by the agent orchestrator
      tags: [Tasks]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - description
                - type
              properties:
                description:
                  type: string
                  maxLength: 2000
                  example: "Research the latest trends in AI agent architectures"
                type:
                  type: string
                  enum: [research, analysis, coding, testing, documentation]
                  example: "research"
                priority:
                  type: string
                  enum: [LOW, MEDIUM, HIGH, CRITICAL]
                  default: MEDIUM
                  example: "HIGH"
                constraints:
                  type: object
                  properties:
                    max_agents:
                      type: integer
                      minimum: 1
                      maximum: 20
                      default: 5
                      example: 3
                    timeout_seconds:
                      type: integer
                      minimum: 60
                      maximum: 7200
                      default: 1800
                      example: 3600
                    require_consensus:
                      type: boolean
                      default: false
                      example: true
                metadata:
                  type: object
                  additionalProperties: true
                  example:
                    source: "web_ui"
                    department: "research"
      responses:
        '201':
          description: Task created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /tasks/{task_id}:
    get:
      summary: Get task details
      description: Retrieve detailed information about a specific task
      tags: [Tasks]
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
          description: Task ID
      responses:
        '200':
          description: Task details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '404':
          description: Task not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    put:
      summary: Update task
      description: Update task properties (limited fields while running)
      tags: [Tasks]
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                priority:
                  type: string
                  enum: [LOW, MEDIUM, HIGH, CRITICAL]
                  example: "HIGH"
                constraints:
                  type: object
                  properties:
                    timeout_seconds:
                      type: integer
                      minimum: 60
                      maximum: 7200
                      example: 3600
      responses:
        '200':
          description: Task updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: Task not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    delete:
      summary: Cancel task
      description: Cancel a queued or running task
      tags: [Tasks]
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Task cancelled successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '400':
          description: Task cannot be cancelled
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '404':
          description: Task not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /tasks/{task_id}/progress:
    get:
      summary: Get task progress
      description: Get real-time progress updates for a running task
      tags: [Tasks]
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Task progress information
          content:
            application/json:
              schema:
                type: object
                properties:
                  task_id:
                    type: string
                    format: uuid
                    example: "550e8400-e29b-41d4-a716-446655440000"
                  status:
                    type: string
                    enum: [QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED]
                    example: "RUNNING"
                  progress_percent:
                    type: number
                    format: float
                    minimum: 0
                    maximum: 100
                    example: 65.5
                  current_step:
                    type: string
                    example: "Data analysis phase"
                  estimated_completion:
                    type: string
                    format: date-time
                    example: "2025-08-11T11:15:00Z"
                  assigned_agents:
                    type: array
                    items:
                      type: string
                    example: ["agent_researcher_001", "agent_analyst_002"]
                  subtasks:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          example: "subtask_001"
                        description:
                          type: string
                          example: "Collect data sources"
                        status:
                          type: string
                          enum: [PENDING, RUNNING, COMPLETED, FAILED]
                          example: "COMPLETED"
                        assigned_agent:
                          type: string
                          example: "agent_researcher_001"

  /agents:
    get:
      summary: List agents
      description: Retrieve a list of all agents in the system
      tags: [Agents]
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [IDLE, BUSY, FAILED, TERMINATED]
          description: Filter by agent status
        - name: type
          in: query
          schema:
            type: string
            enum: [researcher, coder, analyst, tester, coordinator]
          description: Filter by agent type
      responses:
        '200':
          description: List of agents
          content:
            application/json:
              schema:
                type: object
                properties:
                  agents:
                    type: array
                    items:
                      $ref: '#/components/schemas/Agent'
                  summary:
                    type: object
                    properties:
                      total:
                        type: integer
                        example: 15
                      by_status:
                        type: object
                        properties:
                          IDLE:
                            type: integer
                            example: 7
                          BUSY:
                            type: integer
                            example: 8
                          FAILED:
                            type: integer
                            example: 0
                          TERMINATED:
                            type: integer
                            example: 0

    post:
      summary: Spawn new agent
      description: Create a new agent with specified capabilities
      tags: [Agents]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - type
              properties:
                type:
                  type: string
                  enum: [researcher, coder, analyst, tester, coordinator]
                  example: "researcher"
                capabilities:
                  type: array
                  items:
                    type: string
                  example: ["web_search", "data_analysis"]
                metadata:
                  type: object
                  additionalProperties: true
                  example:
                    priority: "high"
      responses:
        '201':
          description: Agent created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Agent'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /agents/{agent_id}:
    get:
      summary: Get agent details
      description: Retrieve detailed information about a specific agent
      tags: [Agents]
      parameters:
        - name: agent_id
          in: path
          required: true
          schema:
            type: string
          description: Agent ID
      responses:
        '200':
          description: Agent details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Agent'
        '404':
          description: Agent not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    delete:
      summary: Terminate agent
      description: Gracefully terminate an agent
      tags: [Agents]
      parameters:
        - name: agent_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Agent terminated successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "Agent terminated successfully"
                  agent_id:
                    type: string
                    example: "agent_researcher_001"
        '400':
          description: Agent cannot be terminated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /system/metrics:
    get:
      summary: Get system metrics
      description: Retrieve comprehensive system performance metrics
      tags: [System]
      parameters:
        - name: timeframe
          in: query
          schema:
            type: string
            enum: [1h, 6h, 24h, 7d]
            default: 1h
          description: Time window for metrics
      responses:
        '200':
          description: System metrics
          content:
            application/json:
              schema:
                type: object
                properties:
                  timestamp:
                    type: string
                    format: date-time
                    example: "2025-08-11T10:30:00Z"
                  system:
                    type: object
                    properties:
                      cpu_usage_percent:
                        type: number
                        format: float
                        example: 45.2
                      memory_usage_mb:
                        type: integer
                        example: 2048
                      disk_usage_percent:
                        type: number
                        format: float
                        example: 23.1
                  agents:
                    type: object
                    properties:
                      total_count:
                        type: integer
                        example: 15
                      active_count:
                        type: integer
                        example: 8
                      average_cpu_percent:
                        type: number
                        format: float
                        example: 15.3
                  tasks:
                    type: object
                    properties:
                      completed_count:
                        type: integer
                        example: 127
                      average_completion_time_seconds:
                        type: number
                        format: float
                        example: 180.5
                      success_rate:
                        type: number
                        format: float
                        example: 0.95

tags:
  - name: Tasks
    description: Task orchestration and management
  - name: Agents
    description: Agent lifecycle and monitoring  
  - name: System
    description: System status and metrics
```

## Authentication

### JWT Token Authentication

MAOS uses JSON Web Tokens (JWT) for API authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Obtaining a Token

```bash
curl -X POST https://api.maos.dev/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Rate Limiting

API requests are rate-limited based on your subscription tier:

| Tier | Requests/Minute | Concurrent Tasks |
|------|-----------------|------------------|
| Free | 60 | 1 |
| Pro | 600 | 5 |
| Enterprise | 6000 | 20 |

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 599
X-RateLimit-Reset: 1628097600
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "The requested task could not be found",
    "details": {
      "task_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "timestamp": "2025-08-11T10:30:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `TASK_NOT_FOUND` | 404 | Task does not exist |
| `AGENT_NOT_FOUND` | 404 | Agent does not exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | System temporarily unavailable |

## WebSocket API

For real-time updates, MAOS provides WebSocket endpoints:

### Task Progress Updates

```javascript
const ws = new WebSocket('wss://api.maos.dev/v1/ws/tasks/550e8400-e29b-41d4-a716-446655440000/progress');

ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Progress:', update.progress_percent + '%');
    console.log('Step:', update.current_step);
};
```

### System Events

```javascript
const ws = new WebSocket('wss://api.maos.dev/v1/ws/system/events');

ws.onmessage = function(event) {
    const event = JSON.parse(event.data);
    console.log('Event:', event.type);
    console.log('Data:', event.data);
};
```

## SDK Examples

### Python SDK

```python
from maos_client import MAOSClient

client = MAOSClient(
    api_key="your_api_key",
    base_url="https://api.maos.dev/v1"
)

# Create a task
task = client.tasks.create(
    description="Analyze customer feedback sentiment",
    type="analysis",
    priority="HIGH",
    constraints={
        "max_agents": 3,
        "timeout_seconds": 1800
    }
)

print(f"Task created: {task.id}")

# Monitor progress
for update in client.tasks.stream_progress(task.id):
    print(f"Progress: {update.progress_percent}%")
    if update.status == "COMPLETED":
        break

# Get results
result = client.tasks.get_result(task.id)
print(f"Output: {result.output}")
```

### JavaScript SDK

```javascript
import { MAOSClient } from '@maos/client';

const client = new MAOSClient({
  apiKey: 'your_api_key',
  baseURL: 'https://api.maos.dev/v1'
});

// Create and monitor a task
async function runAnalysis() {
  const task = await client.tasks.create({
    description: 'Generate market research report',
    type: 'research',
    priority: 'HIGH',
    constraints: {
      maxAgents: 5,
      timeoutSeconds: 3600
    }
  });

  console.log(`Task created: ${task.id}`);

  // Wait for completion
  const result = await client.tasks.waitForCompletion(task.id, {
    onProgress: (progress) => {
      console.log(`Progress: ${progress.progressPercent}%`);
    }
  });

  console.log('Analysis complete:', result.output);
}

runAnalysis().catch(console.error);
```

### cURL Examples

#### Create a Task
```bash
curl -X POST https://api.maos.dev/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Research renewable energy trends in 2025",
    "type": "research",
    "priority": "HIGH",
    "constraints": {
      "max_agents": 4,
      "timeout_seconds": 2400,
      "require_consensus": true
    },
    "metadata": {
      "project": "energy_analysis",
      "budget": 1000
    }
  }'
```

#### Get Task Status
```bash
curl -X GET https://api.maos.dev/v1/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### List Active Agents
```bash
curl -X GET "https://api.maos.dev/v1/agents?status=BUSY" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get System Metrics
```bash
curl -X GET "https://api.maos.dev/v1/system/metrics?timeframe=24h" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Pagination

List endpoints support cursor-based pagination:

```bash
curl -X GET "https://api.maos.dev/v1/tasks?limit=20&offset=40" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response includes pagination metadata:
```json
{
  "tasks": [...],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 40,
    "has_more": true,
    "next_offset": 60
  }
}
```

## Webhook Integration

Configure webhooks to receive task completion notifications:

### Webhook Configuration

```bash
curl -X POST https://api.maos.dev/v1/webhooks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/maos",
    "events": ["task.completed", "task.failed"],
    "secret": "your_webhook_secret"
  }'
```

### Webhook Payload Example

```json
{
  "event": "task.completed",
  "timestamp": "2025-08-11T10:45:00Z",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "COMPLETED",
    "result": {
      "output": "Analysis complete...",
      "artifacts": ["report.pdf", "data.csv"],
      "metrics": {
        "completion_time_seconds": 180,
        "agents_used": 3
      }
    }
  },
  "signature": "sha256=..."
}
```

## Performance Tips

1. **Batch Operations**: Use batch endpoints when creating multiple tasks
2. **Appropriate Timeouts**: Set realistic timeout values based on task complexity
3. **Agent Limits**: Use `max_agents` constraint to prevent resource contention
4. **Progress Monitoring**: Use WebSocket connections for real-time updates instead of polling
5. **Error Handling**: Implement exponential backoff for retries on 5xx errors

## Support

- **Documentation**: https://docs.maos.dev/api
- **API Status**: https://status.maos.dev
- **Support Email**: api-support@maos.dev
- **GitHub Issues**: https://github.com/maos-team/maos/issues