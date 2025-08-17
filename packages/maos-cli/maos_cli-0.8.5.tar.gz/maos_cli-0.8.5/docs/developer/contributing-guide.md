# MAOS Contributing Guide

## Welcome Contributors!

Thank you for your interest in contributing to the Multi-Agent Orchestration System (MAOS). This guide will help you get started with development, understand our processes, and make meaningful contributions to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Release Process](#release-process)
10. [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Node.js 20+** for frontend development
- **Docker Desktop** for local development
- **Git** for version control
- **Make** for build automation

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/maos-team/maos.git
cd maos

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Set up the development environment
make dev-setup
```

## Development Environment Setup

### Option 1: Local Development (Recommended)

```bash
# Start development services
make dev-start

# This starts:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - MAOS API server (port 8000)
# - Web dashboard (port 3001)
# - Development proxy (port 3000)

# Run database migrations
make db-migrate

# Load test fixtures
make load-fixtures

# Verify setup
make dev-test
```

### Option 2: Docker Development

```bash
# Build development containers
make docker-dev-build

# Start development stack
make docker-dev-up

# Run tests in container
make docker-dev-test

# Access development shell
make docker-dev-shell
```

### Option 3: Codespace/GitPod

```bash
# The repository includes configurations for:
# - GitHub Codespaces (.devcontainer/)
# - GitPod (.gitpod.yml)
# - VS Code dev containers

# Simply open the repository in your preferred cloud IDE
```

### Development Tools Configuration

**VS Code Settings (`.vscode/settings.json`):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

**Git Hooks Configuration:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
        
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: pytest tests/ -v
        language: system
        pass_filenames: false
        always_run: true
```

## Project Structure

### Repository Layout

```
maos/
├── src/
│   ├── maos/                     # Main package
│   │   ├── api/                  # REST API endpoints
│   │   ├── cli/                  # Command-line interface
│   │   ├── core/                 # Core orchestration logic
│   │   ├── interfaces/           # Abstract interfaces
│   │   ├── models/               # Data models
│   │   └── utils/                # Utilities
│   ├── communication/            # Inter-agent communication
│   ├── checkpoint/               # Checkpointing system
│   ├── monitoring/               # Monitoring and metrics
│   └── storage/                  # Storage layer
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── performance/              # Performance tests
│   └── fixtures/                 # Test fixtures
├── docs/                         # Documentation
├── examples/                     # Usage examples
├── scripts/                      # Build and deployment scripts
├── config/                       # Configuration files
└── frontend/                     # Web dashboard (React)
```

### Key Components

**Core Modules:**
- `orchestrator.py`: Main orchestration engine
- `agent_manager.py`: Agent lifecycle management
- `task_planner.py`: Task decomposition and planning
- `resource_allocator.py`: Resource management
- `state_manager.py`: Shared state coordination

**Communication Layer:**
- `message_bus/`: Message routing and delivery
- `event_dispatcher/`: Event-driven communication
- `consensus/`: Consensus mechanisms
- `protocols/`: Communication protocols

**Storage Layer:**
- `redis_state/`: Redis-based state management
- `checkpoint/`: State persistence and recovery
- `persistence/`: Data persistence interfaces

## Development Workflow

### Feature Development

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/agent-load-balancing
   ```

2. **Implement Feature:**
   ```bash
   # Make your changes
   # Follow TDD principles (tests first)
   
   # Run tests frequently
   make test
   
   # Check code quality
   make lint
   make type-check
   ```

3. **Commit Changes:**
   ```bash
   # Stage changes
   git add .
   
   # Commit with conventional commit message
   git commit -m "feat(agents): implement load balancing algorithm
   
   - Add weighted round-robin load balancer
   - Implement agent performance tracking
   - Add configuration options for load balancing
   - Include comprehensive tests
   
   Closes #123"
   ```

4. **Push and Create PR:**
   ```bash
   git push origin feature/agent-load-balancing
   
   # Create pull request via GitHub CLI or web interface
   gh pr create --title "feat(agents): implement load balancing" --body "Detailed description..."
   ```

### Bug Fix Workflow

1. **Create Bug Fix Branch:**
   ```bash
   git checkout -b bugfix/task-timeout-handling
   ```

2. **Write Failing Test:**
   ```python
   # tests/unit/core/test_task_manager.py
   def test_task_timeout_handling():
       """Test that tasks are properly handled when they timeout"""
       # Write test that demonstrates the bug
       pass
   ```

3. **Fix Bug:**
   ```python
   # src/maos/core/task_manager.py
   def handle_task_timeout(self, task_id):
       # Implement fix
       pass
   ```

4. **Verify Fix:**
   ```bash
   # Ensure tests pass
   make test
   
   # Check related functionality
   make integration-test
   ```

### Hotfix Workflow

For critical production issues:

```bash
# Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Make minimal necessary changes
# Write regression tests
# Verify fix

# Fast-track review process
git push origin hotfix/critical-security-fix
gh pr create --title "hotfix: critical security vulnerability" --assignee @security-team
```

## Coding Standards

### Python Code Style

**Follow PEP 8 with these specific guidelines:**

```python
# Good: Descriptive names
class AgentLoadBalancer:
    def calculate_optimal_distribution(self, agents: List[Agent], tasks: List[Task]) -> Dict[str, List[Task]]:
        """Calculate optimal task distribution across agents."""
        pass

# Good: Type hints everywhere
async def spawn_agent(
    self, 
    agent_type: AgentType, 
    capabilities: List[str],
    resources: ResourceRequirements
) -> Agent:
    """Spawn a new agent with specified capabilities and resources."""
    pass

# Good: Comprehensive docstrings
class TaskPlanner:
    """
    Plans and decomposes tasks for optimal parallel execution.
    
    The TaskPlanner analyzes incoming tasks to identify parallelization
    opportunities, creates execution plans, and manages task dependencies.
    
    Attributes:
        decomposition_strategies: Available task decomposition strategies
        dependency_resolver: Resolves task dependencies
        performance_predictor: Predicts task execution performance
        
    Example:
        planner = TaskPlanner()
        plan = await planner.create_execution_plan(task)
    """
    
    def __init__(self, strategies: List[DecompositionStrategy]):
        """Initialize the task planner with decomposition strategies."""
        self.decomposition_strategies = strategies
```

**Error Handling:**
```python
# Good: Specific exceptions with context
class AgentSpawnError(MAOSException):
    """Raised when agent spawning fails."""
    
    def __init__(self, agent_type: str, reason: str, details: Optional[Dict] = None):
        self.agent_type = agent_type
        self.reason = reason
        self.details = details or {}
        super().__init__(f"Failed to spawn {agent_type} agent: {reason}")

# Good: Proper error handling
async def spawn_agent(self, agent_type: str) -> Agent:
    try:
        agent = await self._create_agent_instance(agent_type)
        await self._initialize_agent(agent)
        return agent
    except ResourceExhaustionError as e:
        raise AgentSpawnError(
            agent_type, 
            "Insufficient resources", 
            {"available_memory": e.available_memory}
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error spawning agent: {e}", exc_info=True)
        raise AgentSpawnError(agent_type, "Unexpected error") from e
```

**Async/Await Best Practices:**
```python
# Good: Proper async/await usage
async def process_tasks_concurrently(self, tasks: List[Task]) -> List[TaskResult]:
    """Process multiple tasks concurrently."""
    
    # Create coroutines
    task_coroutines = [self.process_single_task(task) for task in tasks]
    
    # Wait for all tasks with proper error handling
    results = []
    async with asyncio.TaskGroup() as tg:
        task_handles = [tg.create_task(coro) for coro in task_coroutines]
    
    # Collect results
    for handle in task_handles:
        try:
            results.append(await handle)
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            results.append(TaskResult.failed(str(e)))
    
    return results

# Good: Resource cleanup
async def managed_agent_session(self, agent_type: str):
    """Context manager for agent sessions."""
    agent = None
    try:
        agent = await self.spawn_agent(agent_type)
        yield agent
    finally:
        if agent:
            await self.cleanup_agent(agent)
```

### Configuration Management

```python
# Good: Centralized configuration with validation
@dataclass
class MAOSConfig:
    """Main MAOS configuration."""
    
    system: SystemConfig
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'MAOSConfig':
        """Load configuration from file with validation."""
        config_data = yaml.safe_load(config_path.read_text())
        
        # Validate required sections
        required_sections = ['system', 'database', 'redis']
        missing_sections = [s for s in required_sections if s not in config_data]
        if missing_sections:
            raise ConfigurationError(f"Missing required sections: {missing_sections}")
        
        return cls(
            system=SystemConfig(**config_data['system']),
            database=DatabaseConfig(**config_data['database']),
            redis=RedisConfig(**config_data['redis']),
            security=SecurityConfig(**config_data.get('security', {}))
        )
    
    def validate(self) -> None:
        """Validate configuration consistency."""
        if self.system.max_agents < 1:
            raise ConfigurationError("max_agents must be at least 1")
        
        if self.database.pool_size > self.system.max_agents * 2:
            warnings.warn("Database pool size may be excessive")
```

### Testing Standards

**Unit Test Example:**
```python
# tests/unit/core/test_task_planner.py
import pytest
from unittest.mock import Mock, AsyncMock
from maos.core.task_planner import TaskPlanner, Task, DecompositionStrategy

class TestTaskPlanner:
    """Test suite for TaskPlanner."""
    
    @pytest.fixture
    def mock_strategies(self):
        """Mock decomposition strategies."""
        strategy1 = Mock(spec=DecompositionStrategy)
        strategy1.can_decompose.return_value = True
        strategy1.decompose.return_value = [Mock(spec=Task), Mock(spec=Task)]
        return [strategy1]
    
    @pytest.fixture
    def task_planner(self, mock_strategies):
        """Create TaskPlanner instance."""
        return TaskPlanner(mock_strategies)
    
    async def test_create_execution_plan_success(self, task_planner):
        """Test successful execution plan creation."""
        # Arrange
        task = Task(description="Test task", type="research")
        
        # Act
        plan = await task_planner.create_execution_plan(task)
        
        # Assert
        assert plan is not None
        assert len(plan.subtasks) > 0
        assert plan.estimated_duration > 0
    
    async def test_create_execution_plan_no_strategies(self):
        """Test execution plan creation with no strategies."""
        # Arrange
        task_planner = TaskPlanner([])
        task = Task(description="Test task", type="research")
        
        # Act & Assert
        with pytest.raises(PlanningError, match="No decomposition strategies available"):
            await task_planner.create_execution_plan(task)
    
    @pytest.mark.parametrize("task_type,expected_complexity", [
        ("research", 3),
        ("coding", 5),
        ("analysis", 4),
    ])
    async def test_complexity_estimation(self, task_planner, task_type, expected_complexity):
        """Test task complexity estimation for different types."""
        # Arrange
        task = Task(description="Complex task", type=task_type)
        
        # Act
        complexity = await task_planner.estimate_complexity(task)
        
        # Assert
        assert complexity == expected_complexity
```

**Integration Test Example:**
```python
# tests/integration/test_task_workflow.py
import pytest
from maos.testing import MAOSTestClient

@pytest.mark.integration
class TestTaskWorkflow:
    """Integration tests for complete task workflows."""
    
    async def test_complete_research_workflow(self, maos_client: MAOSTestClient):
        """Test complete research task workflow."""
        # Submit task
        task_response = await maos_client.submit_task(
            description="Research AI trends in healthcare",
            task_type="research",
            max_agents=3
        )
        
        assert task_response.status_code == 201
        task_id = task_response.json()["task_id"]
        
        # Wait for completion
        result = await maos_client.wait_for_completion(task_id, timeout=300)
        
        # Verify results
        assert result.status == "COMPLETED"
        assert len(result.artifacts) > 0
        assert result.performance_metrics["agents_used"] <= 3
    
    async def test_task_failure_recovery(self, maos_client: MAOSTestClient):
        """Test task failure and recovery mechanisms."""
        # Submit task that will fail
        task_response = await maos_client.submit_task(
            description="Invalid task that should fail",
            task_type="invalid_type"
        )
        
        task_id = task_response.json()["task_id"]
        
        # Wait for failure
        result = await maos_client.wait_for_completion(task_id, timeout=60)
        assert result.status == "FAILED"
        
        # Retry task
        retry_response = await maos_client.retry_task(task_id)
        assert retry_response.status_code == 200
```

## Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Performance Tests**: Test system performance characteristics
4. **Chaos Tests**: Test system resilience under failure conditions
5. **End-to-End Tests**: Test complete user workflows

### Test Naming Convention

```python
# Pattern: test_[method_name]_[scenario]_[expected_result]
def test_spawn_agent_with_valid_type_returns_agent():
    pass

def test_spawn_agent_with_invalid_type_raises_error():
    pass

def test_spawn_agent_when_resources_exhausted_retries_then_fails():
    pass
```

### Test Data Management

```python
# tests/fixtures/agents.py
@pytest.fixture
def sample_agent():
    """Provide a sample agent for testing."""
    return Agent(
        id="test_agent_001",
        type=AgentType.RESEARCHER,
        capabilities=["web_search", "data_analysis"],
        status=AgentStatus.IDLE
    )

@pytest.fixture
def agent_pool():
    """Provide a pool of test agents."""
    return [
        Agent(id=f"agent_{i:03d}", type=AgentType.RESEARCHER)
        for i in range(10)
    ]

# Use factories for complex test data
class TaskFactory:
    @staticmethod
    def create_research_task(**kwargs):
        defaults = {
            "description": "Research task",
            "type": "research", 
            "priority": "MEDIUM",
            "max_agents": 3
        }
        defaults.update(kwargs)
        return Task(**defaults)
```

### Performance Testing

```python
# tests/performance/test_agent_scaling.py
import pytest
import asyncio
import time
from maos.testing import PerformanceTestCase

class TestAgentScaling(PerformanceTestCase):
    """Performance tests for agent scaling."""
    
    @pytest.mark.benchmark
    async def test_agent_spawn_performance(self):
        """Benchmark agent spawning performance."""
        spawn_times = []
        
        for i in range(50):
            start_time = time.perf_counter()
            agent = await self.agent_manager.spawn_agent("researcher")
            end_time = time.perf_counter()
            
            spawn_times.append(end_time - start_time)
            await self.agent_manager.terminate_agent(agent.id)
        
        # Performance assertions
        avg_spawn_time = sum(spawn_times) / len(spawn_times)
        assert avg_spawn_time < 2.0, f"Average spawn time {avg_spawn_time:.2f}s exceeds 2s threshold"
        
        p95_spawn_time = sorted(spawn_times)[int(len(spawn_times) * 0.95)]
        assert p95_spawn_time < 5.0, f"P95 spawn time {p95_spawn_time:.2f}s exceeds 5s threshold"
    
    @pytest.mark.load
    async def test_concurrent_task_processing(self):
        """Test concurrent task processing under load."""
        num_tasks = 100
        max_agents = 20
        
        # Submit tasks concurrently
        tasks = []
        start_time = time.perf_counter()
        
        for i in range(num_tasks):
            task = await self.submit_test_task(f"Load test task {i}")
            tasks.append(task)
        
        # Wait for completion
        completed_tasks = await asyncio.gather(
            *[self.wait_for_completion(task.id) for task in tasks]
        )
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        # Performance metrics
        successful_tasks = sum(1 for task in completed_tasks if task.status == "COMPLETED")
        throughput = successful_tasks / total_time
        
        assert successful_tasks >= num_tasks * 0.95, "Success rate below 95%"
        assert throughput >= 5.0, f"Throughput {throughput:.2f} tasks/s below 5 tasks/s threshold"
```

## Documentation

### Code Documentation

**Module Docstrings:**
```python
"""
MAOS Task Planning Module

This module provides task planning and decomposition capabilities for the
Multi-Agent Orchestration System. It analyzes incoming tasks to identify
parallelization opportunities and creates optimal execution plans.

Key Components:
    TaskPlanner: Main planning engine
    DecompositionStrategy: Abstract strategy for task decomposition
    ExecutionPlan: Represents a planned task execution

Example:
    >>> planner = TaskPlanner()
    >>> task = Task("Research AI trends", type="research")
    >>> plan = await planner.create_execution_plan(task)
    >>> print(f"Plan requires {len(plan.subtasks)} subtasks")
"""
```

**Function Docstrings:**
```python
async def create_execution_plan(self, task: Task) -> ExecutionPlan:
    """
    Create an optimal execution plan for the given task.
    
    This method analyzes the task requirements, applies available decomposition
    strategies, and creates a plan that maximizes parallelization while
    respecting dependencies and resource constraints.
    
    Args:
        task: The task to plan for execution
        
    Returns:
        ExecutionPlan: Optimized execution plan with subtasks and dependencies
        
    Raises:
        PlanningError: When no suitable decomposition strategy is available
        ResourceError: When insufficient resources are available
        
    Example:
        >>> task = Task("Build REST API", type="coding")
        >>> plan = await planner.create_execution_plan(task)
        >>> assert len(plan.subtasks) > 1
        >>> assert plan.estimated_duration < task.max_duration
    """
```

### Documentation Updates

When adding new features:

1. **Update API Documentation**: Add to OpenAPI spec
2. **Update User Guides**: Add usage examples
3. **Update Architecture Docs**: Document design decisions
4. **Update CLI Reference**: Document new commands
5. **Update Migration Guide**: Note breaking changes

### Documentation Review Process

```bash
# Build documentation locally
make docs-build

# Serve documentation for review
make docs-serve

# Check for broken links
make docs-check

# Generate API documentation from code
make docs-api-generate
```

## Pull Request Process

### PR Template

```markdown
## Description
Brief description of the changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated  
- [ ] Performance tests added/updated (if applicable)
- [ ] Manual testing completed

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Migration guide updated (if breaking changes)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Documentation builds successfully
- [ ] Breaking changes are documented

## Screenshots (if applicable)
Add screenshots of UI changes.

## Additional Notes
Any additional information for reviewers.
```

### Review Guidelines

**For Authors:**
1. Keep PRs focused and reasonably sized (<500 lines when possible)
2. Write clear commit messages and PR descriptions
3. Respond to feedback promptly and constructively
4. Update tests and documentation with code changes
5. Rebase and squash commits before merging

**For Reviewers:**
1. Review code for correctness, performance, and maintainability
2. Check test coverage and quality
3. Verify documentation updates
4. Test functionality locally when appropriate
5. Provide constructive, actionable feedback

### Automated Checks

All PRs must pass:
```bash
# Code quality checks
make lint
make type-check
make security-scan

# Test suite
make test
make integration-test

# Documentation
make docs-build
make docs-check

# Performance regression tests
make performance-test
```

### Merge Requirements

- ✅ All automated checks pass
- ✅ At least 2 approving reviews (1 for docs-only changes)
- ✅ Branch is up to date with main
- ✅ No merge conflicts
- ✅ Documentation is updated

## Release Process

### Versioning

MAOS follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (x.Y.0): New functionality (backward compatible)
- **PATCH** (x.y.Z): Bug fixes (backward compatible)

### Release Cycle

**Regular Releases:**
- **Patch releases**: Bi-weekly (bug fixes, small improvements)
- **Minor releases**: Monthly (new features)
- **Major releases**: Quarterly (breaking changes, major features)

**Emergency Releases:**
- **Hotfixes**: As needed for critical security/stability issues

### Release Process

1. **Version Preparation:**
   ```bash
   # Create release branch
   git checkout -b release/v1.2.0
   
   # Update version numbers
   make version-bump VERSION=1.2.0
   
   # Update CHANGELOG.md
   make changelog-generate
   
   # Update documentation
   make docs-update-version
   ```

2. **Pre-release Testing:**
   ```bash
   # Run comprehensive test suite
   make test-all
   
   # Run performance benchmarks
   make benchmark
   
   # Test deployment scenarios
   make test-deployment
   ```

3. **Release Creation:**
   ```bash
   # Tag release
   git tag -a v1.2.0 -m "Release v1.2.0"
   
   # Push to repository
   git push origin v1.2.0
   
   # GitHub Actions automatically:
   # - Builds and tests
   # - Creates GitHub release
   # - Publishes to PyPI
   # - Updates Docker images
   # - Deploys documentation
   ```

4. **Post-release:**
   ```bash
   # Merge back to main
   git checkout main
   git merge release/v1.2.0
   
   # Start next development cycle
   make version-bump-dev VERSION=1.3.0-dev
   ```

## Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/). Key principles:

- **Be Respectful**: Treat all community members with respect
- **Be Inclusive**: Welcome contributors from all backgrounds
- **Be Constructive**: Provide helpful, actionable feedback
- **Be Patient**: Remember that everyone is learning

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, technical discussions
- **GitHub Discussions**: General questions, ideas, announcements
- **Discord**: Real-time chat for contributors
- **Mailing List**: Important announcements and RFC discussions

### Recognition

Contributors are recognized through:
- **GitHub Contributors**: Automatic recognition on repository
- **CHANGELOG.md**: Major contributions acknowledged in releases
- **Hall of Fame**: Outstanding contributors featured in documentation
- **Swag**: Special contributors receive MAOS merchandise

### Getting Help

**New Contributors:**
- Check out [Good First Issues](https://github.com/maos-team/maos/labels/good%20first%20issue)
- Join our [Discord](https://discord.gg/maos) for mentorship
- Read the [Architecture Guide](../system/architecture-overview.md)

**Experienced Contributors:**
- Help with [Help Wanted](https://github.com/maos-team/maos/labels/help%20wanted) issues
- Review PRs from new contributors
- Improve documentation and examples
- Participate in RFC discussions

## Advanced Topics

### Architecture Decision Records (ADRs)

For significant architectural decisions, create an ADR:

```markdown
# ADR-001: Agent Communication Protocol

## Status
Accepted

## Context
We need to establish how agents communicate with each other for coordination.

## Decision
Use Redis Streams for agent-to-agent communication with the following characteristics:
- Asynchronous message passing
- Message persistence for reliability
- Consumer groups for load balancing

## Consequences
- Pros: Reliable, scalable, built-in persistence
- Cons: Adds Redis dependency, potential single point of failure
- Mitigation: Redis clustering for high availability

## Implementation
- Create MessageBus class wrapping Redis Streams
- Define standard message format
- Implement retry logic for failed deliveries
```

### Performance Profiling

```python
# Use cProfile for performance analysis
python -m cProfile -o profile.stats -m maos.cli task submit "Test task"

# Analyze with pstats
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
"

# Memory profiling with memory_profiler
@profile
def process_large_dataset(data):
    # Function implementation
    pass
```

### Security Considerations

**Security Review Checklist:**
- [ ] Input validation for all user inputs
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention in web interfaces
- [ ] Authentication and authorization checks
- [ ] Secure handling of secrets and credentials
- [ ] Rate limiting for APIs
- [ ] Audit logging for security events

## Conclusion

Contributing to MAOS is a collaborative effort that values quality, maintainability, and innovation. By following these guidelines, you help ensure that MAOS remains a robust, scalable, and user-friendly multi-agent orchestration system.

**Key Takeaways:**
1. **Quality First**: Write tests, follow coding standards, document changes
2. **Communication**: Engage with the community, ask questions, provide feedback
3. **Incremental Improvement**: Make small, focused changes that build up over time
4. **Learning Together**: Share knowledge, mentor others, learn from feedback

Thank you for contributing to MAOS! Your efforts help advance the state of multi-agent systems for everyone.

## Quick Links

- [Project Repository](https://github.com/maos-team/maos)
- [Issue Tracker](https://github.com/maos-team/maos/issues)
- [Documentation](https://docs.maos.dev)
- [Discord Community](https://discord.gg/maos)
- [Architecture Guide](../system/architecture-overview.md)
- [API Documentation](../system/api-documentation.md)
- [Performance Guide](../user-guides/performance-optimization.md)