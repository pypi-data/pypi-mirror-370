"""DailySum - A CLI tool for generating daily work summaries from GitHub activity."""

from .cli import main
from .config import Config
from .github_summarizer import GitHubSummarizer

__all__ = ["Config", "GitHubSummarizer", "main"]
