# DailySum

[![Lint](https://github.com/njbrake/dailysum/actions/workflows/lint.yaml/badge.svg)](https://github.com/njbrake/dailysum/actions/workflows/lint.yaml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/dailysum)](https://pypi.org/project/dailysum/)
[![codecov](https://codecov.io/gh/njbrake/dailysum/branch/main/graph/badge.svg)](https://codecov.io/gh/njbrake/dailysum)

A CLI tool that uses AI agents to generate daily work summaries from your GitHub activity.

## What It Does

Analyzes your GitHub activity and generates daily summaries like this:

```
Yesterday:
- Merged PR #142: Fix authentication bug in user login flow
- Reviewed PR #138: Add support for OAuth2 integration
- Opened issue #145: Memory leak in background task processor

Today:
- Continue work on OAuth2 integration testing
- Address memory leak issue in background processor
- Review pending PRs from team members
```

## How It Works

This tool uses two Mozilla AI projects:

### [any-llm](https://github.com/njbrakeany-llm)
Provides a unified interface to different LLM providers. Switch between OpenAI, Anthropic, Mistral, and other models with a string change.

### [any-agent](https://github.com/njbrakeany-agent)
Provides a unified interface for AI agent frameworks. Handles tool orchestration, model interactions, and GitHub API access via Model Context Protocol (MCP).

Together, these handle the complexity of GitHub API interactions and LLM provider differences.

## Installation

### Requirements

- Python 3.11 or newer
- A GitHub Personal Access Token
- API key for your chosen LLM provider (OpenAI, Anthropic, etc.)

### Install from PyPI

```bash
pip install dailysum
```

### Install from Source

```bash
git clone https://github.com/njbrake/dailysum.git
cd dailysum
pip install -e .
```

## Configuration

### Option 1: Interactive Setup (Recommended)

Run the initialization command and follow the prompts:

```bash
dailysum init
```

This will:
- Prompt for your GitHub token
- Let you choose your preferred LLM model
- Optionally set your company name
- Save configuration to `~/.config/dailysum/config.toml`

### Option 2: Environment Variables

Set these environment variables:

```bash
export GITHUB_TOKEN="ghp_your_github_token_here"
export MODEL_ID="openai/gpt-4o-mini"  # Optional, defaults to gpt-4o-mini
export COMPANY="Your Company Name"     # Optional
```

Then run with the `--use-env` flag:

```bash
dailysum generate --use-env
```

### Getting a GitHub Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:user`, `read:org`, `notifications`
4. Copy the generated token

### Supported LLM Providers

- **OpenAI**: `openai/gpt-4o`, `openai/gpt-4o-mini`, `openai/gpt-3.5-turbo`
- **Anthropic**: `anthropic/claude-3-5-sonnet-20241022`, `anthropic/claude-3-haiku-20240307`
- **Mistral**: `mistral/mistral-large-latest`, `mistral/mistral-small-latest`
- **Google**: `google/gemini-1.5-pro`, `google/gemini-1.5-flash`

See [any-llm providers](https://mozilla-ai.github.io/any-llm/providers/) for the complete list.

## Usage

### Generate Your Daily Summary

```bash
dailysum generate
```

### Generate with Quality Evaluation

```bash
dailysum generate --evaluate
```

### View Current Configuration

```bash
dailysum config
```

### Use Environment Variables Instead of Config File

```bash
dailysum generate --use-env
```

## Advanced Usage

### Custom Configuration File Location

```bash
# Initialize with custom location
dailysum init --config-path /path/to/my/config.toml

# Generate using custom location
dailysum generate --config-path /path/to/my/config.toml
```

### Different Models for Different Purposes

You can easily switch between models by updating your config:

```bash
# Use a faster, cheaper model
dailysum init --model-id "openai/gpt-4o-mini"

# Use a more powerful model for complex summaries
dailysum init --model-id "anthropic/claude-3-5-sonnet-20241022"
```

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/njbrake/dailysum.git
cd dailysum

# Install with development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format and lint
ruff format .
ruff check . --fix

# Type checking
mypy src/
```

## Contributing

Contributions are welcome. Areas of interest:

- New LLM provider support
- Summary templates and prompts
- Additional GitHub data sources
- CLI improvements
- Tests and documentation

See [Contributing Guide](CONTRIBUTING.md) for details.

## Example Output

```
📋 Your Daily Summary
┌─────────────────────────────────────────────────────────────┐
│ Yesterday:                                                  │
│ - Merged PR #234: Implement user authentication system     │
│ - Reviewed PR #231: Add Docker configuration               │
│ - Fixed critical bug in payment processing (Issue #189)    │
│ - Updated documentation for API endpoints                  │
│                                                             │
│ Today:                                                      │
│ - Complete integration tests for authentication system     │
│ - Review pending PRs from team members                     │
│ - Start work on user dashboard redesign                    │
│ - Investigate performance issues in search functionality   │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### "Configuration error: GitHub token not found"

Make sure you've either:
- Run `dailysum init` to set up a config file, or
- Set the `GITHUB_TOKEN` environment variable

### "Unable to import 'any_agent'"

Install the required dependencies:
```bash
pip install any-agent any-llm-sdk
```

### Rate Limiting Issues

If you hit GitHub API rate limits:
- Use a GitHub token (provides 5000 requests/hour vs 60 for unauthenticated)
- Consider running the tool less frequently
- The tool automatically respects rate limits and will wait if needed

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [any-llm](https://github.com/njbrakeany-llm) - Unified LLM provider interface
- [any-agent](https://github.com/njbrakeany-agent) - Unified AI agent framework
- [GitHub Copilot MCP](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-your-ide) - GitHub API access via Model Context Protocol
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Click](https://click.palletsprojects.com/) - Command-line interface framework

---

Built by Mozilla AI
