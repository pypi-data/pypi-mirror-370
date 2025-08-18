# Installation Guide for MAOS

## Quick Install with pipx (Recommended)

### 1. Install pipx (if not already installed)

```bash
# On macOS
brew install pipx
pipx ensurepath

# On Linux
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# On Windows
py -m pip install --user pipx
py -m pipx ensurepath
```

### 2. Install MAOS from PyPI

```bash
pipx install maos-cli
```

### 3. Verify Installation

```bash
maos --version
```

## Usage

### Start MAOS in Any Project

```bash
# Navigate to your project
cd ~/my-project

# Start MAOS chat interface
maos

# MAOS creates .claude/agents/ directory with subagents
# and coordinates multiple Claude instances
```

### Natural Language Commands

Once started, just type naturally:

```
MAOS> spawn 3 agents to review my code
MAOS> implement the requirements in prd.md  
MAOS> show me what agents are running
MAOS> create a checkpoint
```

## Prerequisites

### Required: Claude Code CLI

MAOS orchestrates Claude Code CLI instances, so you need:

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Authenticate with your Claude account
claude login
```

### Optional: Redis (for distributed features)

For advanced features like distributed state:

```bash
# Option 1: Docker
docker run -d -p 6379:6379 redis

# Option 2: Local Redis
brew install redis  # macOS
apt install redis   # Ubuntu
```

## Installing from Source

If you want to contribute or use the latest development version:

```bash
# Clone repository
git clone https://github.com/maos/maos-cli.git
cd maos-cli

# Install with pipx from local source
pipx install -e .

# Or with pip in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Upgrading

```bash
# Upgrade to latest version
pipx upgrade maos-cli

# Or reinstall
pipx uninstall maos-cli
pipx install maos-cli
```

## Uninstalling

```bash
pipx uninstall maos-cli
```

## Troubleshooting

### "Claude command not found"

Make sure Claude Code CLI is installed:
```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

### "pipx not found"

Ensure pipx is in your PATH:
```bash
pipx ensurepath
# Then restart your terminal
```

### Permission errors

If you get permission errors, try using `--user`:
```bash
python3 -m pip install --user pipx
```

## Configuration

MAOS creates a `.claude/agents/` directory in your project for subagents. You can:

1. Let MAOS create subagents automatically based on your tasks
2. Customize subagents by editing `.claude/agents/*.md` files
3. Create your own subagent templates

## What Gets Installed

- `maos` command - Main CLI interface
- Python package `maos-cli` with minimal dependencies
- No Redis required (optional for advanced features)
- No Docker required (optional for deployment)

## Next Steps

1. Run `maos` in any project directory
2. Type `help` to see available commands
3. Try `spawn 3 agents to review my code`
4. Read the [documentation](https://maos.dev/docs) for advanced usage