# Tutorial 2: Multi-Agent Workflows

**Duration:** 45-60 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Completion of Tutorial 1

## Overview

In this tutorial, you'll master the art of designing and managing complex multi-agent workflows in MAOS. You'll learn how agents communicate, share state, and coordinate to solve complex problems that would be impossible for single agents.

By the end of this tutorial, you'll be able to:
- Design workflows that leverage multiple agent types effectively
- Understand and utilize shared state for agent coordination
- Implement complex task dependencies and conditional workflows
- Optimize workflows for maximum parallel efficiency
- Debug and monitor multi-agent coordination

## Learning Objectives

1. **Agent Coordination**: Understand how agents communicate and share information
2. **Workflow Design**: Create complex multi-step workflows with dependencies
3. **State Management**: Use shared state for agent coordination
4. **Performance Optimization**: Design workflows for maximum efficiency
5. **Advanced Monitoring**: Track complex multi-agent interactions

## Part 1: Understanding Agent Types and Capabilities

### Agent Capabilities Matrix

Each agent type has specific strengths. Let's understand them:

```bash
# Examine available agent types and their capabilities
maos agent types --detailed
```

| Agent Type | Primary Capabilities | Best For | Coordination Role |
|------------|---------------------|----------|-------------------|
| **researcher** | web_search, data_analysis, synthesis | Market research, competitive analysis | Information gathering |
| **coder** | programming, testing, debugging | Software development, automation | Implementation |
| **analyst** | data_analysis, visualization, statistics | Data processing, insights | Analysis and reporting |
| **tester** | test_generation, validation, qa | Quality assurance, verification | Validation |
| **coordinator** | orchestration, consensus, planning | Complex workflows, decision-making | Leadership and synthesis |

### Exercise 1: Single vs Multi-Agent Task Analysis

Let's compare how the same task is handled differently:

**Single Agent Approach:**
```bash
# Submit task to single agent
SINGLE_TASK=$(maos task submit "Create a comprehensive business plan for a SaaS startup" --max-agents 1 --format json | jq -r '.task_id')

echo "Single agent task: $SINGLE_TASK"
```

**Multi-Agent Approach:**
```bash
# Submit same task for multi-agent handling
MULTI_TASK=$(maos task submit "Create a comprehensive business plan for a SaaS startup" --max-agents 6 --format json | jq -r '.task_id')

echo "Multi-agent task: $MULTI_TASK"
```

**Observe the Difference:**
```bash
# Monitor both approaches
maos task show $SINGLE_TASK --subtasks &
maos task show $MULTI_TASK --subtasks &

# Compare agent assignments
maos agent list --task $SINGLE_TASK
maos agent list --task $MULTI_TASK
```

**Expected Differences:**
- Single agent: Linear execution, longer duration
- Multi-agent: Parallel execution (market research, financial modeling, competitive analysis, etc.)

## Part 2: Shared State and Agent Communication

### Understanding Shared State

MAOS agents coordinate through shared state - a distributed memory system that enables real-time information sharing.

### Exercise 2: Exploring Shared State

Create a workflow that requires heavy coordination:

```bash
# Submit a coordination-heavy task
COORDINATION_TASK=$(maos task submit "Research top 5 AI companies, analyze their business models, compare their strengths/weaknesses, and predict future market positions" --type research --max-agents 4 --format json | jq -r '.task_id')

# Monitor shared state during execution
maos state monitor --task $COORDINATION_TASK --follow
```

**What You'll See:**
- Agents sharing research findings in real-time
- Coordination messages between agents
- Consensus building for conclusions
- Dynamic work allocation based on discoveries

### Exercise 3: Custom Workflow with Explicit Dependencies

Design a complex workflow with multiple stages:

```bash
# Stage 1: Market Research
MARKET_RESEARCH=$(maos task submit "Research the current state of the renewable energy market, including key players, market size, growth trends, and regulatory environment" --type research --format json | jq -r '.task_id')

# Stage 2: Technical Analysis (depends on market research)
TECH_ANALYSIS=$(maos task submit "Based on the market research findings, analyze the technical challenges and opportunities in renewable energy storage solutions" --type analysis --depends-on $MARKET_RESEARCH --format json | jq -r '.task_id')

# Stage 3: Business Strategy (depends on both previous stages)
BUSINESS_STRATEGY=$(maos task submit "Using insights from market research and technical analysis, develop a comprehensive business strategy for entering the renewable energy storage market" --type mixed --depends-on "$MARKET_RESEARCH,$TECH_ANALYSIS" --format json | jq -r '.task_id')

# Stage 4: Implementation Plan (depends on strategy)
IMPLEMENTATION=$(maos task submit "Create a detailed implementation plan with timeline, resources, and milestones for the renewable energy storage business strategy" --type mixed --depends-on $BUSINESS_STRATEGY --format json | jq -r '.task_id')

echo "Workflow created:"
echo "1. Market Research: $MARKET_RESEARCH"
echo "2. Technical Analysis: $TECH_ANALYSIS"
echo "3. Business Strategy: $BUSINESS_STRATEGY"
echo "4. Implementation Plan: $IMPLEMENTATION"
```

### Exercise 4: Monitor Complex Workflow

Track the complex dependency execution:

```bash
# Create a comprehensive monitoring view
maos workflow create --name "renewable-energy-analysis" \
  --tasks "$MARKET_RESEARCH,$TECH_ANALYSIS,$BUSINESS_STRATEGY,$IMPLEMENTATION"

# Monitor the entire workflow
maos workflow monitor "renewable-energy-analysis" --detailed --follow
```

**Key Observations:**
- **Sequential Dependencies**: Tasks wait for dependencies to complete
- **Parallel Execution**: Independent tasks run simultaneously
- **State Sharing**: Later tasks use results from earlier ones
- **Dynamic Adaptation**: Task plans adjust based on intermediate results

## Part 3: Advanced Agent Coordination Patterns

### Pattern 1: Parallel Research with Synthesis

### Exercise 5: Parallel Research Pattern

```bash
# Create parallel research streams that feed into synthesis
PARALLEL_WORKFLOW=$(cat << 'EOF'
{
  "workflow_name": "ai_framework_comparison",
  "tasks": [
    {
      "id": "research_tensorflow",
      "description": "Research TensorFlow: features, performance, ecosystem, pros/cons",
      "type": "research",
      "dependencies": []
    },
    {
      "id": "research_pytorch", 
      "description": "Research PyTorch: features, performance, ecosystem, pros/cons",
      "type": "research",
      "dependencies": []
    },
    {
      "id": "research_jax",
      "description": "Research JAX: features, performance, ecosystem, pros/cons", 
      "type": "research",
      "dependencies": []
    },
    {
      "id": "compare_frameworks",
      "description": "Compare all three frameworks and provide recommendations for different use cases",
      "type": "analysis",
      "dependencies": ["research_tensorflow", "research_pytorch", "research_jax"]
    },
    {
      "id": "create_guide",
      "description": "Create a comprehensive selection guide with decision tree and examples",
      "type": "mixed",
      "dependencies": ["compare_frameworks"]
    }
  ]
}
EOF
)

# Submit the workflow
echo "$PARALLEL_WORKFLOW" | maos workflow submit --format json
```

### Pattern 2: Iterative Refinement

### Exercise 6: Iterative Development Pattern

```bash
# Create iterative refinement workflow
ITERATIVE_TASK=$(maos task submit "Design and implement a Python web scraper for job postings, with error handling, rate limiting, and data validation. Include comprehensive tests and documentation." --type coding --max-agents 3 --require-consensus --format json | jq -r '.task_id')

# Monitor the iterative process
maos task monitor $ITERATIVE_TASK --show-consensus --follow
```

**What Happens:**
1. **Initial Design**: Coder agent creates initial implementation
2. **Review**: Tester agent identifies issues and improvements
3. **Refinement**: Coder agent implements improvements
4. **Validation**: All agents reach consensus on quality
5. **Finalization**: Coordinator agent ensures completeness

### Pattern 3: Divide-and-Conquer

### Exercise 7: Large Dataset Analysis

```bash
# Create a task requiring data division
DATA_ANALYSIS_TASK=$(maos task submit "Analyze customer satisfaction survey data with 50,000 responses across 12 regions. Identify trends, patterns, regional differences, and provide actionable insights with visualizations." --type analysis --max-agents 5 --format json | jq -r '.task_id')

# Watch how MAOS divides the work
maos task show $DATA_ANALYSIS_TASK --execution-plan --detailed
```

**Divide-and-Conquer Process:**
1. **Data Segmentation**: Coordinator divides data by region
2. **Parallel Analysis**: Multiple analyst agents process segments
3. **Pattern Recognition**: Each analyst identifies regional patterns
4. **Cross-Regional Analysis**: Coordinator compares findings
5. **Synthesis**: Combined insights and visualizations

## Part 4: Advanced Workflow Patterns

### Exercise 8: Conditional Workflow

Create a workflow with conditional branching:

```bash
# Submit a task with conditional logic
CONDITIONAL_TASK=$(cat << 'EOF'
maos task submit "Analyze the given financial data and determine investment strategy. If the market shows high volatility (>20%), focus on defensive strategies. If growth indicators are strong (>15% projected), focus on growth strategies. Otherwise, recommend balanced approach." --type analysis --enable-conditions --max-agents 4 --format json
EOF
)

CONDITIONAL_ID=$(eval $CONDITIONAL_TASK | jq -r '.task_id')

# Monitor conditional execution
maos task show $CONDITIONAL_ID --conditions --follow
```

### Exercise 9: Human-in-the-Loop Workflow

Create a workflow that requires human input:

```bash
# Submit task requiring human decision
HUMAN_LOOP_TASK=$(maos task submit "Research and analyze three potential office locations for our startup. Present findings and wait for human selection before proceeding with detailed lease analysis for chosen location." --type mixed --human-input-required --max-agents 3 --format json | jq -r '.task_id')

# Monitor until human input needed
maos task monitor $HUMAN_LOOP_TASK --wait-for-input
```

**When prompted for input:**
```bash
# Provide human decision
maos task input $HUMAN_LOOP_TASK --decision "Select location 2 (downtown office)" --continue
```

### Exercise 10: Error Recovery and Retry

Test MAOS error handling with a challenging task:

```bash
# Submit a task likely to encounter issues
ERROR_HANDLING_TASK=$(maos task submit "Scrape real-time stock data from multiple sources, handle API rate limits, network timeouts, and data inconsistencies. Provide clean, validated dataset." --type coding --max-agents 2 --retry-on-failure 3 --format json | jq -r '.task_id')

# Watch error handling
maos task logs $ERROR_HANDLING_TASK --follow --include-errors
```

**Error Recovery Process:**
1. **Initial Attempt**: Coder agent tries implementation
2. **Error Detection**: System detects API failures
3. **Retry Logic**: Agent implements retry mechanisms
4. **Fallback Strategies**: Alternative data sources
5. **Success**: Robust solution with error handling

## Part 5: Workflow Optimization

### Exercise 11: Performance Analysis and Optimization

Analyze workflow performance and optimize:

```bash
# Create a complex workflow for optimization
OPTIMIZATION_TASK=$(maos task submit "Create a complete e-commerce platform: database design, REST API, user authentication, product catalog, shopping cart, payment processing, and admin dashboard" --type coding --max-agents 8 --format json | jq -r '.task_id')

# Analyze performance in real-time
maos task analyze $OPTIMIZATION_TASK --performance --live
```

**Optimization Metrics to Watch:**
- **Agent Utilization**: Are all agents contributing effectively?
- **Dependency Bottlenecks**: Are tasks waiting unnecessarily?
- **Communication Overhead**: Is coordination taking too long?
- **Parallel Efficiency**: How much speedup are we achieving?

### Exercise 12: Workflow Templates

Create reusable workflow templates:

```bash
# Create a template from successful workflow
maos template create --name "comprehensive-analysis" --from-task $DATA_ANALYSIS_TASK

# Modify template for reuse
maos template edit "comprehensive-analysis" --add-parameter "dataset_size" --add-parameter "regions"

# Use template with new parameters
maos task submit-from-template "comprehensive-analysis" \
  --params '{"dataset_size": "100000", "regions": "global", "focus": "customer_retention"}' \
  --format json
```

### Exercise 13: Workflow Composition

Combine multiple workflows:

```bash
# Create a meta-workflow that combines previous patterns
COMPOSITE_WORKFLOW=$(cat << 'EOF'
{
  "workflow_name": "product_launch_complete",
  "description": "Complete product launch workflow combining research, development, and analysis",
  "sub_workflows": [
    {
      "name": "market_research",
      "template": "parallel-research",
      "params": {"topics": ["competitor_analysis", "market_sizing", "customer_needs"]}
    },
    {
      "name": "product_development", 
      "template": "iterative-development",
      "depends_on": ["market_research"],
      "params": {"product_type": "web_application"}
    },
    {
      "name": "launch_strategy",
      "template": "comprehensive-analysis", 
      "depends_on": ["market_research", "product_development"],
      "params": {"focus": "go_to_market"}
    }
  ]
}
EOF
)

echo "$COMPOSITE_WORKFLOW" | maos workflow compose --format json
```

## Part 6: Advanced Monitoring and Debugging

### Exercise 14: Deep Workflow Monitoring

Set up comprehensive monitoring for complex workflows:

```bash
# Start advanced monitoring
maos monitor start \
  --workflow "product_launch_complete" \
  --metrics "all" \
  --agent-communication true \
  --state-changes true \
  --export-interval 30s

# View real-time dashboard
maos dashboard --workflow-focus "product_launch_complete"
```

**Advanced Monitoring Features:**
- **Agent Communication Graph**: Visual network of agent interactions
- **State Change Timeline**: History of shared state modifications
- **Bottleneck Analysis**: Automatic identification of workflow slowdowns
- **Resource Utilization**: Real-time CPU, memory, and network usage

### Exercise 15: Debugging Workflow Issues

Practice debugging common workflow problems:

**Problem 1: Deadlock Detection**
```bash
# Create a problematic workflow with circular dependencies
DEADLOCK_TEST=$(maos task submit "Task A depends on Task B, Task B depends on Task C, Task C depends on Task A" --debug-mode --format json | jq -r '.task_id')

# Watch MAOS detect and resolve the deadlock
maos task debug $DEADLOCK_TEST --deadlock-detection
```

**Problem 2: Resource Contention**
```bash
# Create resource-intensive competing tasks
maos task submit "Process large dataset requiring 8GB RAM" --max-agents 3 &
maos task submit "Train ML model requiring 6GB RAM" --max-agents 2 &
maos task submit "Generate visualizations requiring GPU" --max-agents 1 &

# Monitor resource allocation
maos resources monitor --contention-alerts
```

**Problem 3: Communication Failures**
```bash
# Simulate network issues
maos debug simulate --network-partition --duration 60s

# Watch how agents handle communication failures
maos task submit "Collaborative document creation requiring constant agent communication" --fault-tolerance high --format json
```

### Exercise 16: Performance Tuning

Optimize workflow performance:

```bash
# Run performance analysis
maos analyze performance --workflow "all" --timeframe "1h" --detailed

# Get optimization recommendations
maos optimize suggest --based-on-history --workflow-type "research"

# Apply optimizations
maos config apply-optimizations --auto-tune --workflow-specific
```

## Part 7: Real-World Workflow Examples

### Exercise 17: Software Development Workflow

Create a complete software development workflow:

```bash
SOFTWARE_DEV_WORKFLOW=$(cat << 'EOF'
{
  "workflow_name": "complete_software_project",
  "tasks": [
    {
      "id": "requirements_analysis",
      "description": "Analyze requirements for a task management web application with user authentication, project creation, task assignment, and reporting",
      "type": "analysis",
      "max_agents": 2
    },
    {
      "id": "system_design",
      "description": "Design system architecture, database schema, and API structure based on requirements",
      "type": "mixed",
      "depends_on": ["requirements_analysis"],
      "max_agents": 2
    },
    {
      "id": "backend_development",
      "description": "Implement backend API with authentication, CRUD operations, and database integration",
      "type": "coding",
      "depends_on": ["system_design"],
      "max_agents": 2
    },
    {
      "id": "frontend_development",
      "description": "Create React frontend with responsive design and API integration",
      "type": "coding", 
      "depends_on": ["system_design"],
      "max_agents": 2
    },
    {
      "id": "testing",
      "description": "Create comprehensive test suite including unit, integration, and end-to-end tests",
      "type": "testing",
      "depends_on": ["backend_development", "frontend_development"],
      "max_agents": 2
    },
    {
      "id": "deployment",
      "description": "Set up CI/CD pipeline and deploy to production environment",
      "type": "mixed",
      "depends_on": ["testing"],
      "max_agents": 1
    },
    {
      "id": "documentation",
      "description": "Create user documentation, API docs, and deployment guide",
      "type": "mixed",
      "depends_on": ["deployment"],
      "max_agents": 1
    }
  ]
}
EOF
)

echo "$SOFTWARE_DEV_WORKFLOW" | maos workflow submit --format json
```

### Exercise 18: Research and Analysis Workflow

Create a comprehensive research workflow:

```bash
RESEARCH_WORKFLOW=$(maos task submit "Conduct comprehensive analysis of the impact of AI on employment: research historical technological disruptions, analyze current AI capabilities and limitations, survey industry predictions, examine geographic and sector variations, and provide policy recommendations" --type research --max-agents 6 --consensus-required --format json | jq -r '.task_id')

# Monitor the research coordination
maos task monitor $RESEARCH_WORKFLOW --show-collaboration --export-research-process
```

## Part 8: Best Practices and Patterns

### Workflow Design Best Practices

1. **Task Granularity**: Balance between too fine-grained (coordination overhead) and too coarse (limited parallelism)

2. **Dependency Management**: Minimize unnecessary dependencies while ensuring logical flow

3. **Agent Specialization**: Match agent types to task requirements

4. **Error Handling**: Design for graceful failure and recovery

5. **Resource Planning**: Consider memory, CPU, and I/O requirements

### Exercise 19: Apply Best Practices

Redesign a workflow using best practices:

```bash
# Original suboptimal workflow
SUBOPTIMAL=$(maos task submit "Do everything related to creating a mobile app" --max-agents 10 --format json | jq -r '.task_id')

# Improved workflow with best practices
IMPROVED_WORKFLOW=$(cat << 'EOF'
{
  "workflow_name": "mobile_app_development_optimized",
  "description": "Optimized mobile app development workflow",
  "tasks": [
    {
      "id": "market_research",
      "description": "Research mobile app market, user needs, and competitor analysis",
      "type": "research",
      "max_agents": 2,
      "priority": "HIGH"
    },
    {
      "id": "ui_ux_design", 
      "description": "Create user interface mockups and user experience flow",
      "type": "mixed",
      "depends_on": ["market_research"],
      "max_agents": 2
    },
    {
      "id": "backend_api",
      "description": "Develop REST API with authentication and core functionality",
      "type": "coding",
      "depends_on": ["market_research"],
      "max_agents": 2,
      "estimated_duration": "4h"
    },
    {
      "id": "mobile_frontend",
      "description": "Implement mobile app frontend with API integration",
      "type": "coding", 
      "depends_on": ["ui_ux_design", "backend_api"],
      "max_agents": 2,
      "estimated_duration": "6h"
    },
    {
      "id": "testing_qa",
      "description": "Comprehensive testing including unit, integration, and user acceptance tests",
      "type": "testing",
      "depends_on": ["mobile_frontend"],
      "max_agents": 2,
      "priority": "HIGH"
    }
  ],
  "error_handling": {
    "retry_failed_tasks": true,
    "max_retries": 2,
    "fallback_strategies": true
  },
  "optimization": {
    "auto_scale_agents": true,
    "dynamic_priorities": true,
    "resource_monitoring": true
  }
}
EOF
)

echo "$IMPROVED_WORKFLOW" | maos workflow submit --format json
```

## Tutorial Summary

### What You've Mastered

✅ **Agent Coordination**: Understanding how agents work together  
✅ **Shared State Management**: Using distributed memory for coordination  
✅ **Complex Dependencies**: Creating sophisticated workflow dependencies  
✅ **Workflow Patterns**: Implementing parallel, iterative, and conditional patterns  
✅ **Performance Optimization**: Tuning workflows for maximum efficiency  
✅ **Advanced Monitoring**: Deep visibility into multi-agent interactions  
✅ **Error Handling**: Robust workflows with fault tolerance  
✅ **Best Practices**: Professional workflow design principles  

### Key Insights

1. **Agent Specialization**: Different agents excel at different tasks
2. **Coordination Patterns**: Standard patterns solve common problems
3. **Shared State**: Critical for complex multi-agent coordination
4. **Dependency Design**: Proper dependencies enable optimal parallelism
5. **Monitoring**: Essential for understanding and optimizing workflows

### Performance Improvements

Typical results from this tutorial:
- **Multi-Agent Speedup**: 3-6x faster than single-agent approaches
- **Workflow Efficiency**: 70-85% parallel efficiency in complex workflows
- **Error Recovery**: <2% task failure rate with proper error handling
- **Resource Utilization**: 80-95% optimal agent utilization

## Next Steps

### Immediate Applications

1. **Design workflows for your own use cases**
2. **Experiment with different agent combinations**
3. **Create reusable workflow templates**
4. **Set up monitoring for production workflows**

### Advanced Learning

- **Tutorial 3**: [Advanced Consensus Mechanisms](tutorial-03-consensus-mechanisms.md) - Learn distributed decision-making
- **Tutorial 4**: [Custom Agent Development](tutorial-04-custom-agents.md) - Create specialized agents
- **Tutorial 5**: [Production Deployment](tutorial-05-production-deployment.md) - Deploy at scale

### Community Contribution

- **Share your workflow patterns** with the MAOS community
- **Contribute to workflow templates** in the public repository
- **Help others** on the community forum with workflow design questions

## Troubleshooting

### Common Multi-Agent Issues

**Agents not coordinating effectively:**
```bash
# Check shared state connectivity
maos state health --connectivity-test

# Monitor agent communication
maos monitor --agent-communication --timeout 60s
```

**Workflow stuck at dependencies:**
```bash
# Analyze dependency graph
maos task analyze $TASK_ID --dependencies --detect-issues

# Visualize workflow execution
maos workflow visualize $TASK_ID --output workflow.png
```

**Poor parallel efficiency:**
```bash
# Get parallelization recommendations  
maos optimize analyze --workflow $TASK_ID --recommendations

# Apply suggested improvements
maos workflow optimize $TASK_ID --apply-suggestions
```

### Getting Advanced Help

- **Workflow consulting**: workflow-help@maos.dev
- **Performance optimization**: performance@maos.dev  
- **Community patterns**: https://patterns.maos.dev

---

🎉 **Excellent Work!** You've mastered multi-agent workflows and can now design sophisticated, coordinated systems that leverage the full power of MAOS orchestration.

**Tutorial Stats:**
- **Exercises Completed**: 19 advanced exercises
- **Patterns Learned**: 6 workflow patterns
- **Skills Acquired**: Multi-agent coordination, workflow optimization, advanced monitoring

Ready for even more advanced topics? Continue with [Tutorial 3: Advanced Consensus Mechanisms](tutorial-03-consensus-mechanisms.md)!