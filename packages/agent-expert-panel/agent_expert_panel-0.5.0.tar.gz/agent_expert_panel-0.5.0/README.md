# Agent Expert Panel - Core Package

[![codecov](https://codecov.io/gh/zbloss/agent-expert-panel/graph/badge.svg?token=ZLecmiZ5dp)](https://codecov.io/gh/zbloss/agent-expert-panel)

## Overview

This is the core package of the Agent Expert Panel monorepo, containing the main Python library for multi-agent AI collaboration. The framework orchestrates AI experts to solve complex problems through collaborative reasoning.

## Features

- **5 Specialized AI Experts**: Advocate, Critic, Pragmatist, Research Specialist, and Innovator
- **GraphRAG-Enhanced Memory**: Persistent knowledge across sessions with intelligent indexing
- **Real-Time Web Research**: Tavily-powered search with automatic synthesis
- **Interactive CLI**: Built with Typer for modern command-line experience
- **Human Participation**: Join AI experts in discussions via UserProxyAgent
- **Flexible Discussion Patterns**: Round-robin, structured debate, and more

## Installation

From the monorepo root:

```bash
# Install core package dependencies
cd packages/core
uv sync --group dev --group test

# Or using pip
pip install -e ".[dev]"
```

## Usage

### CLI Commands

```bash
# Interactive mode
agent-panel

# Run specific discussion
agent-panel discuss "Should we adopt microservices?" --pattern round-robin --rounds 3

# Virtual expert panel with research
agent-panel virtual-solve "How to improve customer retention?" --domain business
```

### Programmatic Usage

```python
import asyncio
from agent_expert_panel.panel import ExpertPanel, DiscussionPattern

async def main():
    panel = ExpertPanel()
    result = await panel.discuss(
        topic="How can we improve team productivity?",
        pattern=DiscussionPattern.ROUND_ROBIN,
        max_rounds=3
    )
    print(f"Recommendation: {result.final_recommendation}")

asyncio.run(main())
```

## Configuration

Agents are configured via YAML files in the `configs/` directory. Each agent has customizable:
- Model parameters
- System messages
- API endpoints
- Timeout settings

## Development

```bash
# Run tests
pytest tests

# Format code
ruff format

# Lint code
ruff check --fix
```

## Architecture

The core package contains:
- `/src/agent_expert_panel/` - Main package source
- `/tests/` - Test suite with pytest
- `/examples/` - Usage examples
- `/docs/` - Documentation
- `/configs/` - Agent configuration files

For complete documentation, see the [main repository README](../../README.md).
