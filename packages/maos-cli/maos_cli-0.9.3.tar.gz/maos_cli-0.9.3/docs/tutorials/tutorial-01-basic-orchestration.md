# Tutorial 1: Basic Task Orchestration

**Duration:** 30-45 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Basic command-line knowledge

## Overview

In this tutorial, you'll learn the fundamentals of MAOS task orchestration. You'll discover how MAOS automatically decomposes complex tasks into parallel subtasks and coordinates multiple agents to achieve faster, more efficient execution.

By the end of this tutorial, you'll be able to:
- Submit tasks to MAOS and understand different task types
- Monitor task progress in real-time
- Retrieve and interpret results
- Compare parallel vs sequential execution performance
- Use the MAOS dashboard for visual monitoring

## Learning Objectives

1. **Understand MAOS Architecture**: Learn how MAOS differs from traditional systems
2. **Master Task Submission**: Submit various types of tasks effectively
3. **Monitor Task Execution**: Track progress and agent coordination
4. **Analyze Performance**: Measure and understand performance improvements
5. **Use Visual Tools**: Navigate the MAOS dashboard

## Prerequisites Check

Before starting, ensure you have:
- MAOS installed (`maos version` should return version 2.0.0+)
- Basic understanding of command-line operations
- Text editor of your choice

If you need to install MAOS:
```bash
pip install maos
maos init
```

## Part 1: Understanding MAOS Basics

### What Makes MAOS Different?

Traditional systems process tasks sequentially or simulate multi-agent behavior. MAOS provides true parallel execution with:
- **Real concurrent processing** (not simulated)
- **Automatic task decomposition** into parallelizable components
- **Intelligent agent coordination** with shared state
- **Transparent operation** with full visibility

### Key Concepts

**Tasks**: Work requests submitted to MAOS
**Agents**: Specialized workers (researcher, coder, analyst, tester, coordinator)
**Orchestration**: Automatic planning and coordination of parallel execution
**Checkpoints**: Automatic state snapshots for fault tolerance

Let's see this in action!

## Part 2: Your First MAOS Task

### Exercise 1: Simple Task Submission

Start with a basic task to understand the core workflow:

```bash
# Submit your first task
maos task submit "What are the key benefits of renewable energy?"
```

**Expected Output:**
```
Task submitted successfully!
Task ID: task_20250811_143022_abc123
Status: QUEUED
Estimated completion: 2-3 minutes
```

### Exercise 2: Monitor Task Progress

Watch your task execute in real-time:

```bash
# Monitor task progress
maos task show task_20250811_143022_abc123

# Follow progress live
maos task progress task_20250811_143022_abc123 --follow
```

**What You'll See:**
- Task status progression (QUEUED → RUNNING → COMPLETED)
- Agent assignments and activities
- Subtask breakdowns
- Real-time updates

### Exercise 3: Retrieve Results

Once completed, examine the results:

```bash
# View results in terminal
maos task results task_20250811_143022_abc123

# Export as markdown
maos task export task_20250811_143022_abc123 --format markdown --output results.md

# Open in default text editor
cat results.md
```

**Understanding the Results:**
- **Summary**: High-level findings
- **Detailed Analysis**: Comprehensive breakdown
- **Agent Contributions**: What each agent provided
- **Sources**: References and citations
- **Performance Metrics**: Execution time and efficiency

## Part 3: Task Types and Agent Selection

### Exercise 4: Understanding Task Types

MAOS optimizes agent selection based on task type. Try different types:

**Research Task:**
```bash
maos task submit "Research the top 3 programming languages for web development in 2025" --type research
```

**Analysis Task:**
```bash
maos task submit "Analyze the pros and cons of microservices vs monolithic architecture" --type analysis
```

**Coding Task:**
```bash
maos task submit "Create a Python function to calculate Fibonacci numbers with error handling" --type coding
```

**Mixed Task (Default):**
```bash
maos task submit "Research Python web frameworks, analyze their performance, and create a comparison chart" --type mixed
```

### Exercise 5: Observing Agent Selection

Check how MAOS assigns different agents:

```bash
# List all submitted tasks
maos task list

# Examine agent assignments for each task
maos agent list --details
```

**Key Observations:**
- Research tasks → researcher agents
- Analysis tasks → analyst agents  
- Coding tasks → coder agents
- Mixed tasks → multiple specialized agents + coordinator

## Part 4: Parallel vs Sequential Comparison

### Exercise 6: Performance Comparison

Submit a task that benefits significantly from parallelization:

```bash
# Submit parallelizable task
TASK_ID=$(maos task submit "Research AWS, Azure, and Google Cloud pricing models, compare their features for startups, and analyze cost-effectiveness for different usage scenarios" --type research --format json | jq -r '.task_id')

echo "Submitted task: $TASK_ID"

# Monitor performance metrics
maos task show $TASK_ID --metrics
```

### Exercise 7: Understanding Parallel Execution

Watch the parallel decomposition:

```bash
# Monitor with detailed agent view
maos monitor --task $TASK_ID --show-agents

# See task breakdown
maos task show $TASK_ID --subtasks
```

**What You'll Observe:**
- **Task Decomposition**: Single task broken into 3+ parallel research streams
- **Concurrent Execution**: Multiple agents working simultaneously
- **Real-time Coordination**: Agents sharing findings and coordinating
- **Result Synthesis**: Coordinator agent combining results

### Exercise 8: Performance Analysis

Once the task completes, analyze the performance:

```bash
# Get detailed performance metrics
maos task analyze $TASK_ID --performance

# Compare with estimated sequential time
maos task compare $TASK_ID --baseline sequential
```

**Expected Results:**
- **Speedup**: 2.5-4x faster than sequential execution
- **Efficiency**: High parallel efficiency (>0.8)
- **Agent Utilization**: Multiple agents actively contributing

## Part 5: MAOS Dashboard

### Exercise 9: Visual Monitoring

Access the MAOS dashboard for visual monitoring:

```bash
# Start the dashboard (if not already running)
maos dashboard --port 3001

# Open in browser
echo "Dashboard available at: http://localhost:3001"
```

**Dashboard Features to Explore:**

1. **System Overview**
   - Active agents and their status
   - Task queue and completion rates
   - System resource utilization

2. **Task Management**
   - Real-time task progress
   - Agent assignments and coordination
   - Performance metrics and trends

3. **Agent Pool**
   - Agent types and capabilities
   - Utilization and performance
   - Health and status monitoring

### Exercise 10: Dashboard Navigation

Practice using the dashboard:

1. **Submit a new task through the UI**
2. **Monitor its progress visually**
3. **Examine agent coordination**
4. **View results and performance metrics**

## Part 6: Advanced Task Management

### Exercise 11: Task Parameters

Experiment with task parameters:

```bash
# Task with specific agent limit
maos task submit "Compare the environmental impact of solar vs wind energy" --max-agents 2

# High priority task
maos task submit "Urgent: Analyze security vulnerabilities in our authentication system" --priority HIGH

# Task with timeout
maos task submit "Comprehensive market research on AI tools for developers" --timeout 3600

# Task with specific requirements
maos task submit "Research and code a REST API for user management" --type mixed --max-agents 4 --priority NORMAL
```

### Exercise 12: Task Dependencies

Create a workflow with dependencies:

```bash
# Submit parent task
RESEARCH_TASK=$(maos task submit "Research current trends in cloud computing" --format json | jq -r '.task_id')

# Submit dependent task
ANALYSIS_TASK=$(maos task submit "Analyze the research findings and create recommendations" --depends-on $RESEARCH_TASK --format json | jq -r '.task_id')

# Monitor the workflow
maos task show $RESEARCH_TASK
maos task show $ANALYSIS_TASK
```

### Exercise 13: Batch Processing

Submit multiple related tasks efficiently:

```bash
# Create a batch
maos batch create --name "web-frameworks-analysis"

# Add tasks to the batch
maos batch add-task "web-frameworks-analysis" "Research React.js current features and ecosystem"
maos batch add-task "web-frameworks-analysis" "Research Vue.js current features and ecosystem"  
maos batch add-task "web-frameworks-analysis" "Research Angular current features and ecosystem"

# Submit all tasks
maos batch submit "web-frameworks-analysis"

# Monitor batch progress
maos batch status "web-frameworks-analysis" --follow
```

## Part 7: Troubleshooting and Best Practices

### Exercise 14: Handling Issues

Practice troubleshooting common issues:

**Check system health:**
```bash
maos health --all-components
```

**Monitor system resources:**
```bash
maos status --resources
```

**View system logs:**
```bash
maos logs --tail 50 --level WARNING
```

**Check specific task issues:**
```bash
# If a task fails
maos task show $TASK_ID --error-details
```

### Exercise 15: Best Practices

Apply best practices for task submission:

**✅ Good Task Descriptions:**
```bash
# Specific and clear
maos task submit "Research the top 5 JavaScript testing frameworks, compare their features, performance, and learning curves, then provide recommendations for a React project"

# Appropriate task type
maos task submit "Analyze customer churn data from Q4 2024, identify patterns, and create visualizations showing key insights" --type analysis
```

**❌ Suboptimal Examples:**
```bash
# Too vague
maos task submit "Help me with my project"

# Wrong task type
maos task submit "Write code to sort an array" --type research  # Should be --type coding
```

### Exercise 16: Performance Optimization

Optimize your tasks for best performance:

```bash
# Right-sized agent allocation
maos task submit "Research 3 cloud providers and compare pricing" --max-agents 3  # One per provider

# Appropriate priority
maos task submit "Generate monthly report" --priority LOW  # Not urgent

# Reasonable timeouts
maos task submit "Deep analysis of market trends" --timeout 7200  # 2 hours for complex analysis
```

## Part 8: Results and Evaluation

### Exercise 17: Result Analysis

Practice interpreting MAOS results:

1. **Pick your best-performing task from the tutorial**
2. **Export results in multiple formats:**
   ```bash
   maos task export $TASK_ID --format markdown --output task_results.md
   maos task export $TASK_ID --format json --output task_data.json
   maos task export $TASK_ID --format pdf --output final_report.pdf
   ```

3. **Analyze the performance:**
   ```bash
   maos task analyze $TASK_ID --detailed
   ```

### Exercise 18: Create Your Performance Report

Generate a comprehensive report of your tutorial experience:

```bash
# Get system metrics for the tutorial session
maos metrics --timeframe 2h --export json --output tutorial_metrics.json

# List all tasks from this session
maos task list --created-since "2h ago" --detailed > my_tasks.txt
```

## Tutorial Summary

### What You've Learned

✅ **MAOS Fundamentals**: Understanding true parallel execution  
✅ **Task Submission**: Different types and parameters  
✅ **Monitoring**: Real-time progress tracking  
✅ **Performance Analysis**: Measuring speedup and efficiency  
✅ **Dashboard Usage**: Visual monitoring and management  
✅ **Best Practices**: Optimal task design and troubleshooting  

### Key Takeaways

1. **MAOS provides real parallel execution**, not simulation
2. **Task type selection matters** for agent optimization
3. **Clear, specific descriptions** lead to better results
4. **Parallel decomposition** can achieve 2-5x speedup
5. **The dashboard provides intuitive visual management**

### Performance Summary

Based on typical tutorial results:
- **Average Speedup**: 2.8x faster than sequential execution
- **Task Success Rate**: >95% completion rate
- **Agent Efficiency**: 80-90% parallel efficiency
- **Time Savings**: 60-70% reduction in execution time

## Next Steps

### Immediate Actions

1. **Experiment** with your own tasks and use cases
2. **Explore** different task types and parameters
3. **Practice** using the dashboard for daily workflows
4. **Document** your performance improvements

### Continue Learning

- **Tutorial 2**: [Multi-Agent Workflows](tutorial-02-multi-agent-workflows.md) - Learn advanced coordination
- **Tutorial 4**: [Custom Agent Development](tutorial-04-custom-agents.md) - Create specialized agents
- **Best Practices Guide**: Read the [complete guide](../user-guides/best-practices.md)

### Community Engagement

- **Share your results** on the MAOS community forum
- **Ask questions** on Discord or GitHub Discussions  
- **Contribute** your tutorial improvements or variations

## Troubleshooting

### Common Issues

**Task not starting:**
```bash
# Check agent availability
maos agent list --status IDLE

# Check system resources
maos status --resources
```

**Slow performance:**
```bash
# Monitor resource usage
maos monitor --metric cpu,memory

# Check for bottlenecks
maos diagnostics --performance
```

**Dashboard not accessible:**
```bash
# Restart dashboard
maos dashboard restart --port 3001
```

### Getting Help

- **Built-in help**: `maos help <command>`
- **Community support**: https://community.maos.dev
- **Documentation**: https://docs.maos.dev

## Tutorial Feedback

Help us improve this tutorial:
- **Feedback form**: https://feedback.maos.dev/tutorial-1
- **GitHub issues**: Report bugs or suggest improvements
- **Community discussions**: Share your experience

---

🎉 **Congratulations!** You've completed Tutorial 1 and learned the fundamentals of MAOS task orchestration. You're now ready to tackle more complex workflows in Tutorial 2!

**Total Tutorial Time**: ~45 minutes  
**Tasks Completed**: 18 exercises  
**Skills Acquired**: MAOS basics, task management, performance analysis