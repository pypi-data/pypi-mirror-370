# DailySum

A CLI tool that uses AI agents to generate daily work summaries from your GitHub activity.

## Quick Start

1. Install: `pip install dailysum`
2. Configure: `dailysum init`
3. Generate: `dailysum generate`

## Features

- Uses language models to create summaries from GitHub activity
- Simple configuration with GitHub token
- Analyzes PRs, issues, commits, and reviews
- Supports multiple LLM providers (OpenAI, Anthropic, Mistral, Google, etc.)
- Powered by Mozilla AI's any-agent framework

## How It Works

Uses two Mozilla AI projects:

- **[any-llm](https://github.com/njbrakeany-llm)**: Unified interface to different LLM providers
- **[any-agent](https://github.com/njbrakeany-agent)**: Unified interface for AI agent frameworks

This handles the complexity of GitHub API interactions and LLM provider differences.
