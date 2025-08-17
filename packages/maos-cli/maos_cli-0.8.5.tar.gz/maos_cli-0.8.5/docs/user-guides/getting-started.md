# MAOS Getting Started Guide

## Welcome to MAOS

The Multi-Agent Orchestration System (MAOS) enables true parallel execution of AI agents with shared state management and inter-agent communication. This guide will walk you through your first MAOS experience.

## What Makes MAOS Different

Unlike traditional "multi-agent" systems that simulate parallel processing, MAOS provides:

- **True Parallel Execution**: Multiple agents working simultaneously
- **Shared State Management**: Real-time coordination between agents
- **Automatic Checkpointing**: Never lose work due to failures
- **3-5x Performance Gains**: Measurable speedup for parallelizable tasks
- **Transparent Operation**: Clear visibility into what each agent is doing

## Your First MAOS Task

### Quick Start (5 Minutes)

1. **Start MAOS** (from [Quick Start Guide](../deployment/quick-start.md)):
   ```bash
   curl -fsSL https://get.maos.dev/quickstart | bash
   ```

2. **Submit your first task**:
   ```bash
   maos task submit "Research the top 3 programming languages in 2025 and their key advantages"
   ```

3. **Watch the magic happen**:
   ```bash
   maos monitor --follow
   ```

You'll see MAOS automatically:
- Decompose your task into subtasks
- Spawn specialized researcher agents  
- Execute research in parallel
- Coordinate results between agents
- Deliver a comprehensive final report

## Understanding MAOS Concepts

### Tasks and Orchestration

**Tasks** are the work you want MAOS to perform. When you submit a task, MAOS:

1. **Analyzes** the task complexity and requirements
2. **Decomposes** it into smaller, parallelizable subtasks
3. **Plans** the optimal execution strategy
4. **Spawns** the right agents with appropriate capabilities
5. **Coordinates** execution and combines results

### Agents and Capabilities

MAOS includes specialized **agent types**:

| Agent Type | Capabilities | Best For |
|------------|-------------|----------|
| **Researcher** | web_search, data_analysis, report_generation | Market research, competitive analysis |
| **Coder** | code_generation, testing, debugging | Software development, automation |
| **Analyst** | data_analysis, visualization, statistics | Data processing, insights generation |
| **Tester** | test_generation, test_execution, validation | Quality assurance, verification |
| **Coordinator** | task_coordination, consensus_building | Complex multi-step workflows |

### Shared State and Communication

Agents in MAOS can:
- **Share information** through a distributed memory system
- **Send messages** to coordinate work
- **Build consensus** when decisions are needed
- **Access each other's results** in real-time

## Step-by-Step Tutorial

### Tutorial 1: Simple Research Task

Let's start with a straightforward research task:

```bash
# Submit the task
maos task submit "Compare the environmental impact of solar vs wind energy"

# The command returns a task ID, for example: task_abc123
# Check the status
maos task show task_abc123

# Monitor progress in real-time
maos task progress task_abc123 --follow
```

**What you'll see:**
1. Task decomposition into research areas
2. Multiple researcher agents spawning
3. Parallel research execution
4. Results consolidation
5. Final comprehensive report

### Tutorial 2: Multi-Agent Development Task

Now let's try a more complex development task:

```bash
# Submit a coding task that benefits from parallel execution
maos task submit "Create a Python REST API for a todo application with authentication, CRUD operations, and unit tests" --type coding --max-agents 4
```

**Expected execution flow:**
1. **Planner agent**: Designs the API structure
2. **Coder agent 1**: Implements authentication
3. **Coder agent 2**: Implements CRUD operations  
4. **Tester agent**: Creates unit tests
5. **Coordinator**: Integrates all components

### Tutorial 3: Data Analysis Workflow

For data-intensive tasks:

```bash
# Submit an analysis task
maos task submit "Analyze customer satisfaction trends from the uploaded CSV data and create visualizations" --type analysis --priority HIGH
```

**Multi-agent approach:**
- **Analyst 1**: Data cleaning and preprocessing
- **Analyst 2**: Statistical analysis and trend identification
- **Analyst 3**: Visualization generation
- **Coordinator**: Report compilation

## Working with the Web Dashboard

### Accessing the Dashboard

Open http://localhost:3001 in your browser to access the MAOS dashboard.

### Dashboard Overview

**Main Dashboard Components:**

1. **System Status**: Overall health and performance metrics
2. **Active Tasks**: Real-time task progress and status
3. **Agent Pool**: Current agent allocation and utilization
4. **Performance Metrics**: Throughput, response times, and success rates

### Task Management

**Creating Tasks via Dashboard:**

1. Navigate to **Tasks** → **New Task**
2. Fill in the task details:
   - **Description**: Clear, specific task description
   - **Type**: Select appropriate task type
   - **Priority**: Set task urgency
   - **Constraints**: Specify agent limits and timeouts
3. Click **Submit Task**
4. Monitor progress in the **Tasks** tab

**Task Progress Monitoring:**
- **Progress Bar**: Visual completion indicator
- **Agent Assignment**: See which agents are working
- **Subtask Breakdown**: Understand task decomposition
- **Real-time Logs**: Agent activity and communication
- **Partial Results**: View intermediate outputs

## Advanced Usage Patterns

### Batch Processing

Process multiple related tasks efficiently:

```bash
# Create a batch of related tasks
maos batch create --name "market-research-2025"

# Add tasks to the batch
maos batch add-task "market-research-2025" "Research AI market size in healthcare"
maos batch add-task "market-research-2025" "Research AI market size in finance"
maos batch add-task "market-research-2025" "Research AI market size in retail"

# Submit the entire batch
maos batch submit "market-research-2025"

# Monitor batch progress
maos batch status "market-research-2025"
```

### Workflow Templates

Create reusable workflow patterns:

```bash
# Save a successful task as a template
maos template create --name "api-development" --from-task task_abc123

# Use the template for new tasks
maos task submit-from-template "api-development" \
  --params '{"project_name": "inventory-system", "database": "postgresql"}'

# List available templates
maos template list
```

### Task Dependencies

Create complex workflows with dependencies:

```bash
# Submit parent task
RESEARCH_TASK=$(maos task submit "Research customer pain points in project management")

# Submit dependent task
maos task submit "Design solution architecture based on research findings" \
  --depends-on $RESEARCH_TASK \
  --type coding
```

## Optimization Tips

### Getting the Best Performance

1. **Clear Task Descriptions**: Be specific about what you want
   ```bash
   # Good
   maos task submit "Create a Python Flask REST API with JWT authentication, CRUD operations for tasks, and PostgreSQL database integration"
   
   # Less optimal  
   maos task submit "Make a web API"
   ```

2. **Appropriate Agent Limits**: Set reasonable agent counts
   ```bash
   # For complex tasks that benefit from parallelization
   maos task submit "..." --max-agents 8
   
   # For simple tasks
   maos task submit "..." --max-agents 2
   ```

3. **Use Task Types**: Help MAOS optimize agent selection
   ```bash
   maos task submit "..." --type research    # Uses researcher agents
   maos task submit "..." --type coding      # Uses coder agents
   maos task submit "..." --type analysis    # Uses analyst agents
   ```

### Monitoring Performance

Track your task performance:

```bash
# View performance metrics
maos metrics --timeframe 24h

# Compare parallel vs sequential execution
maos task compare task_abc123 --baseline sequential

# Get performance recommendations
maos analyze performance --task-type research
```

## Common Patterns and Examples

### Content Creation

```bash
# Blog post creation with research
maos task submit "Research and write a comprehensive blog post about sustainable software development practices, including current trends, best practices, and case studies"

# Multi-part content series
maos task submit "Create a 5-part educational series on machine learning fundamentals, with each part building on the previous one"
```

### Software Development

```bash
# Full-stack development
maos task submit "Build a complete e-commerce product catalog system with React frontend, Node.js backend, MongoDB database, and comprehensive tests"

# Code review and optimization
maos task submit "Review the uploaded codebase for performance bottlenecks, security issues, and code quality improvements"
```

### Data Analysis

```bash
# Comprehensive data analysis
maos task submit "Analyze the quarterly sales data to identify trends, seasonal patterns, top-performing products, and provide actionable business recommendations"

# Multi-dataset comparison
maos task submit "Compare customer behavior patterns across different geographical regions using the provided datasets and create regional strategy recommendations"
```

### Research and Analysis

```bash
# Market research
maos task submit "Conduct comprehensive competitive analysis of the project management software market, including feature comparison, pricing analysis, and market positioning recommendations"

# Technical research
maos task submit "Research and compare different cloud database solutions for a high-traffic e-commerce application, considering performance, cost, scalability, and ease of migration"
```

## Understanding Task Results

### Result Formats

MAOS provides results in multiple formats:

```bash
# View results in terminal
maos task results task_abc123

# Export as markdown
maos task export task_abc123 --format markdown --output report.md

# Export as JSON for programmatic use
maos task export task_abc123 --format json --output results.json

# Generate PDF report
maos task export task_abc123 --format pdf --output final_report.pdf
```

### Result Structure

Typical result structure includes:

```json
{
  "task_id": "task_abc123",
  "status": "COMPLETED",
  "summary": "High-level summary of findings",
  "detailed_results": {
    "research_findings": "...",
    "analysis": "...",
    "recommendations": "..."
  },
  "artifacts": [
    "generated_code.py",
    "data_visualization.png",
    "detailed_report.md"
  ],
  "agent_contributions": {
    "agent_researcher_001": "Market size analysis",
    "agent_researcher_002": "Competitive landscape",
    "agent_analyst_001": "Data synthesis"
  },
  "performance_metrics": {
    "completion_time": 180,
    "agents_used": 3,
    "parallel_efficiency": 2.8
  }
}
```

## Troubleshooting Common Issues

### Task Not Starting

**Symptoms**: Task stuck in QUEUED status

**Solutions**:
```bash
# Check agent availability
maos agent list --status IDLE

# Check system resources
maos status --resources

# Increase agent limit if needed
maos config set system.max_agents 10
```

### Slow Task Execution

**Symptoms**: Tasks taking longer than expected

**Solutions**:
```bash
# Increase parallelization
maos task update task_abc123 --max-agents 6

# Check for bottlenecks
maos task analyze task_abc123 --performance

# Monitor resource usage
maos monitor --metric cpu,memory
```

### Poor Quality Results

**Symptoms**: Results don't meet expectations

**Solutions**:
1. **Improve task description**: Be more specific
2. **Set appropriate context**: Provide relevant background
3. **Use consensus**: Enable consensus for critical decisions
   ```bash
   maos task submit "..." --require-consensus true
   ```

## Next Steps

### Explore Advanced Features

1. **Custom Agent Types**: Create specialized agents for your domain
2. **Workflow Automation**: Set up automated task pipelines  
3. **Integration**: Connect MAOS with your existing systems
4. **API Development**: Build applications using the MAOS API

### Learn More

- [CLI Command Reference](cli-reference.md) - Complete command documentation
- [Best Practices Guide](best-practices.md) - Optimization and usage guidelines  
- [API Documentation](../system/api-documentation.md) - REST API reference
- [Performance Guide](performance-optimization.md) - Advanced performance tuning

### Get Support

- **Documentation**: https://docs.maos.dev
- **Community Forum**: https://community.maos.dev
- **GitHub Issues**: https://github.com/maos-team/maos/issues
- **Examples**: https://github.com/maos-team/examples

## Key Takeaways

1. **MAOS provides true parallel execution** - not simulated multi-agent behavior
2. **Clear task descriptions lead to better results** - be specific about requirements
3. **Different agent types excel at different tasks** - use appropriate task types
4. **Monitoring and optimization are key** - track performance and adjust
5. **Start simple, then scale** - begin with straightforward tasks before complex workflows

Ready to harness the power of true multi-agent orchestration? Start experimenting with your own tasks and discover how MAOS can accelerate your work!