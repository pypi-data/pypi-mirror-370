#!/usr/bin/env python3
"""
Simple script to create Claude agents that actually work.
"""

import os
from pathlib import Path

def create_agent(name: str, description: str, prompt: str, tools: str = None):
    """Create a simple Claude agent file."""
    
    # Ensure .claude/agents directory exists
    agents_dir = Path(".claude/agents")
    agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the agent file
    agent_file = agents_dir / f"{name}.md"
    
    # Build the YAML frontmatter
    content = f"""---
name: {name}
description: {description}
"""
    if tools:
        content += f"tools: {tools}\n"
    
    content += f"""---

{prompt}
"""
    
    # Write the file
    agent_file.write_text(content)
    print(f"✅ Created agent: {agent_file}")
    return agent_file

# Example: Create a code reviewer agent
if __name__ == "__main__":
    create_agent(
        name="code-reviewer",
        description="Reviews code for quality and security issues",
        tools="Read, Grep, Glob",
        prompt="""You are a senior code reviewer. When invoked:
1. Review the code for issues
2. Check for security problems
3. Suggest improvements

Focus on:
- Code quality
- Security issues  
- Performance problems
- Best practices"""
    )
    
    create_agent(
        name="test-runner",
        description="Runs tests and fixes failures",
        prompt="""You are a test automation expert. Your job is to:
1. Run the appropriate tests
2. Analyze any failures
3. Fix failing tests
4. Verify the fixes work"""
    )
    
    print("\n📝 Agents created! Now you can use them with:")
    print("   claude -p 'review my code'")
    print("   claude -p 'run tests'")