"""GitHub activity summarizer using AI agents."""

from typing import TYPE_CHECKING

from any_agent import AgentConfig, AgentFramework, AnyAgent
from any_agent.config import MCPStreamableHttp, Tool
from any_agent.evaluation.agent_judge import AgentJudge

if TYPE_CHECKING:
    from any_agent.tracing.agent_trace import AgentTrace

from .config import Config


class GitHubSummarizer:
    """Summarizes GitHub activity using AI agents."""

    def __init__(self, config: Config) -> None:
        """Initialize the GitHub summarizer with configuration."""
        self.config = config
        self.agent: AnyAgent | None = None

    async def create_agent(self) -> AnyAgent:
        """Create and configure the AI agent with GitHub tools."""
        github_tools = [
            "get_me",
            "list_pull_requests",
            "get_pull_request",
            "list_commits",
            "get_commit",
            "list_branches",
            "list_issues",
            "get_issue",
            "search_repositories",
            "search_issues",
            "search_pull_requests",
            "list_notifications",
            "get_notification_details",
        ]

        tools: list[Tool] = [
            MCPStreamableHttp(
                url="https://api.githubcopilot.com/mcp/",
                headers={"Authorization": f"Bearer {self.config.github_token}"},
                client_session_timeout_seconds=30,
                tools=github_tools,
            ),
        ]

        agent_config = AgentConfig(
            model_id=self.config.model_id,
            tools=tools,
        )

        self.agent = await AnyAgent.create_async("tinyagent", agent_config=agent_config)
        return self.agent

    def _build_prompt(self) -> str:
        """Build the prompt for the AI agent."""
        company_context = f" at {self.config.company}" if self.config.company else ""

        example_status = """
Yesterday:
- Address any-llm bug with our callable -> json schema conversion logic that was found by an external contributor
- Support for Llamafile Provider
Today:
- Advanced integration testing for tool usage
- Add Llama.cpp provider support"""

        return f"""
I'm a software engineer{company_context}, and I do most all of my work on GitHub.
I've been asked to provide a daily update about what I did yesterday, as well as what I plan to do today.
Please help me compile this info, and output it in the following format:

```
Yesterday:
- (List of PRs opened/closed/reviewed)
Today:
- (List of things it looks like I'll be working on)
```

Here's an example of what I'm looking for:

```
{example_status}
```
"""

    async def generate_summary(self) -> str:
        """Generate a daily work summary from GitHub activity."""
        if not self.agent:
            await self.create_agent()

        prompt = self._build_prompt()
        if self.agent is None:
            msg = "Agent not initialized"
            raise RuntimeError(msg)

        result = await self.agent.run_async(prompt)
        return str(result.final_output)

    async def evaluate_summary(self, summary_result: "AgentTrace") -> str:
        """Evaluate the quality of the generated summary."""
        judge = AgentJudge(
            model_id=self.config.model_id,
            framework=AgentFramework.TINYAGENT,
        )

        evaluation = await judge.run_async(
            summary_result,
            question="Did any of the tool calls fail?",
        )

        return str(evaluation.final_output)

    async def cleanup(self) -> None:
        """Clean up MCP connections."""
        if self.agent and hasattr(self.agent, "_mcp_clients"):
            for connection in self.agent._mcp_clients:
                await connection.disconnect()
