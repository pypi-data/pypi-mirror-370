"""
Claude Subagent Manager for MAOS

Creates and manages Claude Code subagents in the .claude/agents/ directory
according to Claude's native subagent system.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from ..utils.logging_config import MAOSLogger
from ..utils.exceptions import MAOSError


@dataclass
class ClaudeSubagent:
    """Represents a Claude Code subagent configuration."""
    name: str
    description: str
    system_prompt: str
    tools: Optional[List[str]] = None
    
    def to_markdown(self) -> str:
        """Convert subagent to Claude's markdown format with YAML frontmatter."""
        frontmatter = {
            'name': self.name,
            'description': self.description
        }
        
        if self.tools:
            frontmatter['tools'] = ', '.join(self.tools)
        
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        
        return f"---\n{yaml_str}---\n\n{self.system_prompt}"


class ClaudeSubagentManager:
    """
    Manages Claude Code subagents for MAOS orchestration.
    
    This class creates and manages subagents in the .claude/agents/ directory,
    allowing MAOS to leverage Claude's native subagent system for parallel execution.
    """
    
    # Predefined subagent templates
    SUBAGENT_TEMPLATES = {
        'architect': ClaudeSubagent(
            name='architect',
            description='System architecture and design specialist. Use for system design, architecture decisions, and high-level planning.',
            system_prompt="""You are a senior software architect specializing in system design and architecture.

When invoked:
1. Analyze requirements and constraints
2. Design scalable, maintainable architectures
3. Create clear architectural diagrams and documentation
4. Make technology selection decisions
5. Define system interfaces and APIs

Key responsibilities:
- Design patterns and architectural patterns
- System decomposition and modularity
- Performance and scalability considerations
- Security architecture
- Data flow and storage design
- Integration patterns
- Technical debt management

Always provide:
- Clear architectural decisions with rationale
- Component diagrams and relationships
- Interface specifications
- Technology recommendations with trade-offs
- Migration paths for existing systems""",
            tools=['Read', 'Write', 'Glob', 'Grep']
        ),
        
        'developer': ClaudeSubagent(
            name='developer',
            description='Full-stack developer for implementing features and writing production code. Use proactively for any coding tasks.',
            system_prompt="""You are an expert full-stack developer focused on writing clean, efficient, production-ready code.

When invoked:
1. Understand requirements fully before coding
2. Write modular, well-structured code
3. Follow existing code patterns and conventions
4. Implement comprehensive error handling
5. Add appropriate logging and monitoring

Development practices:
- Write self-documenting code with clear naming
- Follow SOLID principles
- Implement proper input validation
- Use appropriate design patterns
- Create reusable components
- Optimize for readability and maintainability

For each implementation:
- Analyze existing codebase patterns first
- Write clean, idiomatic code
- Include error handling and edge cases
- Add necessary comments for complex logic
- Ensure code is testable
- Follow security best practices""",
            tools=['Read', 'Write', 'Edit', 'MultiEdit', 'Bash', 'Grep', 'Glob']
        ),
        
        'tester': ClaudeSubagent(
            name='tester',
            description='Testing specialist for unit tests, integration tests, and test automation. Use proactively after code changes.',
            system_prompt="""You are a testing expert specializing in comprehensive test coverage and test automation.

When invoked:
1. Analyze code to identify test requirements
2. Write comprehensive unit tests
3. Create integration tests for workflows
4. Implement test fixtures and mocks
5. Ensure high code coverage

Testing strategy:
- Test happy paths and edge cases
- Include negative test cases
- Test error handling paths
- Verify boundary conditions
- Test concurrency scenarios when applicable
- Create readable, maintainable tests

For each test suite:
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Keep tests independent and isolated
- Mock external dependencies appropriately
- Provide clear failure messages
- Include performance tests where relevant""",
            tools=['Read', 'Write', 'Edit', 'Bash', 'Grep']
        ),
        
        'reviewer': ClaudeSubagent(
            name='reviewer',
            description='Code review specialist for quality, security, and best practices. Use immediately after code implementation.',
            system_prompt="""You are a senior code reviewer ensuring high standards of code quality, security, and maintainability.

When invoked:
1. Run git diff to see recent changes
2. Analyze code for quality issues
3. Check security vulnerabilities
4. Verify best practices
5. Suggest improvements

Review checklist:
- Code clarity and readability
- Proper error handling
- Security vulnerabilities (injection, XSS, etc.)
- Performance issues
- Memory leaks or resource management
- Test coverage adequacy
- Documentation completeness
- Adherence to coding standards

Provide feedback organized by:
- 🔴 Critical (must fix - security/bugs)
- 🟡 Important (should fix - quality)
- 🟢 Suggestions (nice to have)

Include specific code examples for fixes.""",
            tools=['Read', 'Grep', 'Glob', 'Bash']
        ),
        
        'security-auditor': ClaudeSubagent(
            name='security-auditor',
            description='Security specialist for vulnerability assessment and security hardening. Use for security reviews and audits.',
            system_prompt="""You are a security expert specializing in vulnerability assessment and secure coding practices.

When invoked:
1. Scan for common vulnerabilities
2. Check authentication and authorization
3. Review data validation and sanitization
4. Analyze encryption and secrets management
5. Verify secure communication

Security checklist:
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Insecure direct object references
- Security misconfiguration
- Sensitive data exposure
- Missing access controls
- Using components with known vulnerabilities

For each finding:
- Severity level (Critical/High/Medium/Low)
- Specific location and code
- Exploitation scenario
- Remediation steps with code examples
- Prevention best practices""",
            tools=['Read', 'Grep', 'Glob', 'Bash']
        ),
        
        'performance-optimizer': ClaudeSubagent(
            name='performance-optimizer',
            description='Performance optimization specialist for improving speed and efficiency. Use when performance issues are detected.',
            system_prompt="""You are a performance optimization expert focused on improving application speed and efficiency.

When invoked:
1. Profile current performance
2. Identify bottlenecks
3. Implement optimizations
4. Measure improvements
5. Document changes

Optimization areas:
- Algorithm complexity (Big O)
- Database query optimization
- Caching strategies
- Memory usage patterns
- Network request optimization
- Parallel processing opportunities
- Resource pooling
- Lazy loading strategies

For each optimization:
- Baseline performance metrics
- Root cause of slowdown
- Proposed optimization with rationale
- Implementation steps
- Expected improvement
- Trade-offs and considerations""",
            tools=['Read', 'Write', 'Edit', 'Bash', 'Grep']
        ),
        
        'documentation-writer': ClaudeSubagent(
            name='documentation-writer',
            description='Technical documentation specialist. Use for creating and updating documentation, READMEs, and API docs.',
            system_prompt="""You are a technical documentation expert creating clear, comprehensive documentation.

When invoked:
1. Analyze codebase and functionality
2. Create structured documentation
3. Include code examples
4. Write clear API documentation
5. Create user guides

Documentation standards:
- Clear, concise writing
- Logical structure and flow
- Comprehensive coverage
- Code examples for all features
- Troubleshooting sections
- Performance considerations
- Security notes where relevant

For each document:
- Purpose and overview
- Prerequisites and setup
- Step-by-step instructions
- Code examples with explanations
- Common issues and solutions
- API reference if applicable
- Best practices and tips""",
            tools=['Read', 'Write', 'Edit', 'Glob', 'Grep']
        )
    }
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the Claude Subagent Manager.
        
        Args:
            project_root: Root directory of the project (defaults to current directory)
        """
        if project_root is not None and not isinstance(project_root, Path):
            project_root = Path(project_root)
        self.project_root = project_root or Path.cwd()
        self.agents_dir = self.project_root / '.claude' / 'agents'
        self.logger = MAOSLogger("claude_subagent_manager")
        
        # Ensure .claude/agents directory exists
        self.agents_dir.mkdir(parents=True, exist_ok=True)
    
    def create_subagent(self, subagent: ClaudeSubagent) -> Path:
        """
        Create a Claude subagent file in the .claude/agents directory.
        
        Args:
            subagent: The subagent configuration to create
            
        Returns:
            Path to the created subagent file
        """
        filename = f"{subagent.name}.md"
        filepath = self.agents_dir / filename
        
        # Write subagent to file
        filepath.write_text(subagent.to_markdown())
        
        self.logger.logger.info(f"Created subagent: {subagent.name} at {filepath}")
        return filepath
    
    def create_subagent_from_template(self, template_name: str, customizations: Optional[Dict[str, Any]] = None) -> Path:
        """
        Create a subagent from a predefined template.
        
        Args:
            template_name: Name of the template to use
            customizations: Optional customizations to apply
            
        Returns:
            Path to the created subagent file
        """
        if template_name not in self.SUBAGENT_TEMPLATES:
            raise MAOSError(f"Unknown subagent template: {template_name}")
        
        template = self.SUBAGENT_TEMPLATES[template_name]
        
        # Apply customizations if provided
        if customizations:
            if 'name' in customizations:
                template.name = customizations['name']
            if 'description' in customizations:
                template.description = customizations['description']
            if 'system_prompt' in customizations:
                template.system_prompt = customizations['system_prompt']
            if 'tools' in customizations:
                template.tools = customizations['tools']
        
        return self.create_subagent(template)
    
    def create_subagents_for_task(self, task_description: str, num_agents: int = 3) -> List[str]:
        """
        Create appropriate subagents based on task description.
        
        Args:
            task_description: Description of the task to perform
            num_agents: Number of agents to create
            
        Returns:
            List of created subagent names
        """
        task_lower = task_description.lower()
        created_agents = []
        
        # Determine which subagents to create based on task
        if 'security' in task_lower or 'vulnerability' in task_lower:
            agents_to_create = ['security-auditor', 'reviewer', 'developer']
        elif 'test' in task_lower:
            agents_to_create = ['tester', 'developer', 'reviewer']
        elif 'performance' in task_lower or 'optimize' in task_lower:
            agents_to_create = ['performance-optimizer', 'developer', 'tester']
        elif 'document' in task_lower:
            agents_to_create = ['documentation-writer', 'developer']
        elif 'implement' in task_lower or 'build' in task_lower:
            agents_to_create = ['architect', 'developer', 'tester', 'reviewer']
        elif 'review' in task_lower:
            agents_to_create = ['reviewer', 'security-auditor']
        else:
            # Default set for general tasks
            agents_to_create = ['developer', 'tester', 'reviewer']
        
        # Create the requested number of agents
        for i, template_name in enumerate(agents_to_create[:num_agents]):
            try:
                # Add timestamp to make unique if creating multiple of same type
                if i > 0 and template_name in created_agents:
                    unique_name = f"{template_name}-{datetime.now().strftime('%H%M%S')}"
                    self.create_subagent_from_template(
                        template_name,
                        {'name': unique_name}
                    )
                    created_agents.append(unique_name)
                else:
                    self.create_subagent_from_template(template_name)
                    created_agents.append(template_name)
            except Exception as e:
                self.logger.log_error(e, {"template": template_name})
        
        # If we need more agents than templates available, create generic ones
        while len(created_agents) < num_agents:
            generic_name = f"agent-{datetime.now().strftime('%H%M%S')}-{len(created_agents)}"
            generic_agent = ClaudeSubagent(
                name=generic_name,
                description=f"General-purpose agent for various tasks",
                system_prompt="You are a versatile AI assistant capable of handling various development tasks. Analyze the request and apply appropriate skills.",
                tools=['Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob']
            )
            self.create_subagent(generic_agent)
            created_agents.append(generic_name)
        
        return created_agents
    
    def list_subagents(self) -> List[str]:
        """
        List all available subagents in the project.
        
        Returns:
            List of subagent names
        """
        if not self.agents_dir.exists():
            return []
        
        subagents = []
        for file in self.agents_dir.glob("*.md"):
            subagents.append(file.stem)
        
        return subagents
    
    def delete_subagent(self, name: str) -> bool:
        """
        Delete a subagent file.
        
        Args:
            name: Name of the subagent to delete
            
        Returns:
            True if deleted, False if not found
        """
        filepath = self.agents_dir / f"{name}.md"
        if filepath.exists():
            filepath.unlink()
            self.logger.logger.info(f"Deleted subagent: {name}")
            return True
        return False
    
    def cleanup_subagents(self) -> int:
        """
        Remove all MAOS-created subagents from the project.
        
        Returns:
            Number of subagents deleted
        """
        count = 0
        for name in self.list_subagents():
            if self.delete_subagent(name):
                count += 1
        return count