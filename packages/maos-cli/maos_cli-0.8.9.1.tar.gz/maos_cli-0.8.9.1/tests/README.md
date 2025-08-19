# MAOS Testing Suite

Comprehensive test suite for the Multi-Agent Orchestration System (MAOS) achieving >95% test coverage with performance benchmarks, chaos engineering, and automated regression detection.

## 🎯 Testing Strategy

### Test Pyramid Structure
```
         /\
        /E2E\      <- End-to-End (Integration)
       /------\
      /Integr. \   <- Integration Tests  
     /----------\
    /   Unit     \ <- Unit Tests (Base)
   /--------------\
```

## 📁 Test Structure

```
tests/
├── unit/                    # Unit tests (>80% of tests)
│   ├── core/               # Core component tests
│   ├── models/             # Data model tests
│   ├── communication/      # Message bus tests
│   └── services/           # Service layer tests
├── integration/            # Integration tests
│   ├── workflows/          # Multi-agent workflows
│   ├── api/                # API endpoint tests
│   └── storage/            # Database integration
├── performance/            # Performance benchmarks
│   ├── load/               # Load testing
│   ├── throughput/         # Message throughput
│   └── latency/            # Latency measurements
├── chaos/                  # Chaos engineering
│   ├── failures/           # Agent failure scenarios
│   ├── partitions/         # Network partitions
│   └── stress/             # Stress testing
├── benchmarks/             # Reference benchmarks
├── fixtures/               # Test fixtures & utilities
└── utils/                  # Testing utilities
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis (for message bus tests)
- PostgreSQL (optional, for storage tests)
- Docker (for integration tests)

### Installation
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Install MAOS in development mode
pip install -e .
```

### Running Tests

#### All Tests
```bash
# Run complete test suite
pytest

# Run with coverage
pytest --cov=src/maos --cov-report=html
```

#### Test Categories
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Performance tests
pytest tests/performance -m performance

# Chaos tests
pytest tests/chaos -m chaos

# Benchmark tests
pytest tests/benchmarks -m benchmark
```

#### Filtered Testing
```bash
# Fast tests only (skip slow tests)
pytest -m "not slow"

# Redis-dependent tests
pytest -m redis_required

# Specific components
pytest tests/unit/core/test_orchestrator.py -v
```

## 📊 Performance Benchmarks

### Target Metrics
- **20 Concurrent Agents**: Baseline performance target
- **1000 Messages/Second**: Message throughput target
- **<100ms p99**: State operation latency target
- **<5 seconds**: Checkpoint save time target
- **<60 seconds**: Recovery time target
- **2-3x Speedup**: Multi-agent vs single-agent performance

### Running Benchmarks
```bash
# Reference benchmarks (single vs multi-agent)
pytest tests/benchmarks/test_reference_benchmarks.py -v

# Performance load tests
pytest tests/performance/load/ -v

# Throughput benchmarks
pytest tests/performance/throughput/ -v
```

### Benchmark Results
Benchmarks automatically generate performance reports and detect regressions:

```bash
# Generate performance trend report
python tests/utils/performance_reporter.py trend test_20_concurrent_agents_baseline

# Check for regressions
python tests/utils/performance_reporter.py regression --threshold 10.0

# Export results
python tests/utils/performance_reporter.py export results.json
```

## 🔥 Chaos Engineering

### Failure Scenarios Tested
- **Random Agent Crashes**: 30% agent failure rate
- **Cascading Failures**: Initial failure triggering additional failures
- **Memory Exhaustion**: Resource pressure scenarios  
- **Network Partitions**: Split-brain scenarios
- **Byzantine Behavior**: Malicious agent behavior
- **Resource Starvation**: CPU/Memory/Disk constraints

### Running Chaos Tests
```bash
# All chaos tests
pytest tests/chaos/ -v

# Specific failure scenarios
pytest tests/chaos/failures/test_agent_failures.py::TestAgentFailures::test_random_agent_crashes -v

# Network partition tests
pytest tests/chaos/partitions/ -v
```

## 📈 Coverage Requirements

### Coverage Targets
- **Overall Coverage**: >95%
- **Line Coverage**: >95%
- **Branch Coverage**: >85%
- **Function Coverage**: >90%

### Coverage Commands
```bash
# Run coverage analysis
python tests/test_coverage_config.py run

# Generate coverage report
python tests/test_coverage_config.py report

# Create coverage badge
python tests/test_coverage_config.py badge --output coverage_badge.svg

# Compare with previous coverage
python tests/test_coverage_config.py compare previous_coverage.json
```

### Coverage Reports
- **Terminal**: Real-time coverage during test runs
- **HTML**: Detailed line-by-line coverage at `tests/coverage_html/`
- **XML**: Machine-readable format for CI/CD
- **JSON**: Historical tracking and comparison

## 🤖 CI/CD Integration

### GitHub Actions Workflow
The test suite includes comprehensive GitHub Actions configuration:

- **Lint & Format**: Black, isort, ruff, mypy
- **Unit Tests**: Python 3.11 & 3.12 matrix
- **Integration Tests**: Full system integration
- **Performance Tests**: Scheduled benchmarks
- **Chaos Tests**: Resilience validation
- **Security Scans**: Bandit, Safety, pip-audit
- **Coverage Reports**: Codecov integration

### Workflow Triggers
```yaml
# On every push/PR
on: [push, pull_request]

# Scheduled performance tests (daily)
schedule:
  - cron: '0 2 * * *'

# Manual triggers with labels
# Add [perf] to commit message for performance tests
# Add [chaos] to commit message for chaos tests
```

## 🛠 Test Configuration

### Pytest Configuration
```ini
[tool:pytest]
testpaths = tests
asyncio_mode = auto
addopts = --strict-markers --cov=src/maos --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests  
    performance: Performance tests
    chaos: Chaos engineering tests
    slow: Slow tests (may be skipped)
```

### Test Markers
- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance benchmarks
- `@pytest.mark.chaos`: Chaos engineering tests
- `@pytest.mark.slow`: Long-running tests
- `@pytest.mark.redis_required`: Requires Redis
- `@pytest.mark.postgresql_required`: Requires PostgreSQL

## 📝 Test Fixtures & Utilities

### Core Fixtures
- `orchestrator`: Full MAOS orchestrator instance
- `agent_manager`: Agent management component
- `message_bus`: Redis-backed message bus
- `state_manager`: State persistence manager
- `chaos_injection`: Chaos engineering utilities
- `performance_metrics`: Performance measurement tools

### Test Utilities
- `TestDataFactory`: Generate test data objects
- `AsyncTestRunner`: Async test execution utilities
- `StateVerifier`: State assertion utilities
- `PerformanceTimer`: Performance measurement
- `ChaosInjection`: Fault injection utilities

### Mock Utilities
- `MockManager`: Comprehensive mock management
- `NetworkChaosSimulator`: Network failure simulation
- `ResourceChaosSimulator`: Resource constraint simulation

## 📊 Test Metrics & Reporting

### Automated Reporting
- **Performance Trends**: Historical performance tracking
- **Regression Detection**: Automated performance regression alerts
- **Coverage Trends**: Coverage change tracking
- **Test Result Summaries**: Comprehensive test reporting

### Report Generation
```bash
# Performance dashboard data
python -c "from tests.utils.performance_reporter import PerformanceReporter; 
           r = PerformanceReporter(); 
           print(r.create_dashboard_data())"

# Coverage comparison
python tests/test_coverage_config.py compare baseline_coverage.json

# Generate all reports
make test-reports  # If Makefile configured
```

## 🔧 Development Workflow

### Test-Driven Development (TDD)
1. **Red**: Write failing test
2. **Green**: Implement minimal code to pass
3. **Refactor**: Improve code while keeping tests green

### Pre-commit Testing
```bash
# Quick pre-commit tests
pytest tests/unit -x --ff

# Pre-push comprehensive tests
pytest tests/unit tests/integration -x

# Performance regression check
pytest tests/performance/load/test_concurrent_agents.py::TestConcurrentAgentLoad::test_20_concurrent_agents_baseline
```

### Test Debugging
```bash
# Run specific test with debugging
pytest tests/unit/core/test_orchestrator.py::TestOrchestrator::test_submit_task -vvv -s

# Run with pdb debugging
pytest --pdb tests/unit/core/test_orchestrator.py::TestOrchestrator::test_submit_task

# Debug failed tests only
pytest --lf --pdb
```

## 🎯 Quality Gates

### Automated Quality Checks
- **Unit Test Coverage**: Must be >95%
- **Integration Tests**: Must pass all scenarios
- **Performance Benchmarks**: Must meet SLA targets
- **Chaos Tests**: Must maintain >70% success rate under failures
- **Security Scans**: Must pass all security checks
- **Code Quality**: Must pass linting and type checking

### Manual Quality Reviews
- **Test Design Review**: Ensure comprehensive test scenarios
- **Performance Analysis**: Review benchmark results and trends
- **Chaos Engineering Review**: Validate failure scenarios and recovery
- **Coverage Analysis**: Identify and address coverage gaps

## 📚 Best Practices

### Writing Tests
- **One Assertion Per Test**: Each test should verify one behavior
- **Descriptive Names**: Test names should explain what and why
- **Arrange-Act-Assert**: Structure tests clearly
- **Independent Tests**: No interdependencies between tests
- **Fast Execution**: Unit tests should complete quickly (<100ms)

### Performance Testing
- **Realistic Workloads**: Use production-like test scenarios
- **Statistical Analysis**: Multiple runs with statistical validation
- **Resource Monitoring**: Track CPU, memory, and I/O usage
- **Baseline Comparison**: Compare against established baselines
- **Regression Detection**: Automated alerts for performance degradation

### Chaos Engineering
- **Gradual Introduction**: Start with minor failures, escalate gradually
- **Observable Recovery**: Verify system recovery after failures
- **Realistic Scenarios**: Use production-like failure patterns
- **Controlled Blast Radius**: Limit scope of chaos experiments
- **Learning from Failures**: Document and address discovered weaknesses

## 🚨 Troubleshooting

### Common Issues

#### Redis Connection Errors
```bash
# Start Redis for tests
docker run -d -p 6379:6379 redis:7-alpine

# Or use Redis in CI
export TEST_REDIS_URL=redis://localhost:6379/1
```

#### PostgreSQL Connection Errors
```bash
# Start PostgreSQL for tests
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=testpass postgres:15-alpine

# Or use in-memory SQLite
export TEST_DATABASE_URL=sqlite:///test_maos.db
```

#### Performance Test Timeouts
```bash
# Increase timeout for slow systems
pytest tests/performance/ --timeout=1800

# Run with fewer agents/tasks
pytest tests/performance/ -k "not test_20_concurrent"
```

#### Coverage Below Target
```bash
# Identify uncovered lines
python tests/test_coverage_config.py report

# Focus on specific modules
pytest tests/unit/core/ --cov=src/maos/core --cov-report=term-missing
```

### Getting Help
- **Documentation**: Check test docstrings and comments
- **Issue Tracking**: Use GitHub issues for test-related problems
- **Code Review**: Request review for complex test scenarios
- **Performance Analysis**: Use built-in reporting tools for performance issues

## 📋 Maintenance

### Regular Tasks
- **Weekly**: Review performance trends and regression reports
- **Monthly**: Update baseline performance metrics
- **Quarterly**: Review and update chaos engineering scenarios
- **Release**: Full benchmark suite execution and documentation update

### Continuous Improvement
- Monitor test execution time and optimize slow tests
- Expand chaos engineering scenarios based on production incidents
- Update performance baselines as system evolves
- Enhance test coverage for new features

---

For more information, see the individual test files and their docstrings. Each test module includes detailed documentation about test scenarios, expected outcomes, and maintenance procedures.