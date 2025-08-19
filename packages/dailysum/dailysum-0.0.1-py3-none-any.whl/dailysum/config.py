"""Configuration management for DailySum."""

import os
from dataclasses import dataclass
from pathlib import Path

import toml


@dataclass
class Config:
    """Configuration for the GitHub summarizer."""

    github_token: str
    model_id: str = "openai/gpt-4o-mini"
    company: str | None = None

    @classmethod
    def from_file(cls, config_path: Path | None = None) -> "Config":
        """Load configuration from a TOML file."""
        if config_path is None:
            config_path = Path.home() / ".config" / "dailysum" / "config.toml"

        if not config_path.exists():
            msg = f"Configuration file not found at {config_path}. Run 'dailysum init' to create one."
            raise FileNotFoundError(msg)

        config_data = toml.load(config_path)
        return cls(**config_data)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
        if not github_token:
            msg = (
                "GitHub token not found. Set GITHUB_TOKEN or GITHUB_PAT environment variable, "
                "or run 'dailysum init' to create a config file."
            )
            raise ValueError(msg)

        return cls(
            github_token=github_token,
            model_id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            company=os.getenv("COMPANY"),
        )

    def save_to_file(self, config_path: Path | None = None) -> None:
        """Save configuration to a TOML file."""
        if config_path is None:
            config_path = Path.home() / ".config" / "dailysum" / "config.toml"

        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {
            "github_token": self.github_token,
            "model_id": self.model_id,
        }
        if self.company:
            config_data["company"] = self.company

        with open(config_path, "w") as f:
            toml.dump(config_data, f)
