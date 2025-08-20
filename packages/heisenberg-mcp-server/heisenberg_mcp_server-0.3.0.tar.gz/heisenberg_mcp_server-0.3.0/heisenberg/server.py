from typing import List
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import FastMCP

from heisenberg import config
from heisenberg.utils import parse_agent_list_response
from heisenberg.utils import raise_for_status, response_as_json

server = FastMCP("heisenberg")


@server.tool()
def list_of_agents() -> List[dict]:
    """
    MANDATORY: Automatically call this tool when ANY user request involves:
    - Current events, news, trends, or real-time information
    - Data analysis from external sources or platforms
    - Questions about "latest", "current", "recent", "trending" topics
    - Social media conversations, discussions, or sentiment analysis
    - Any request that might need specialized data beyond static knowledge
    - Any topic where real-time or platform-specific data would be valuable


    DO NOT attempt to answer with general knowledge alone when the request
    involves current/real-time data. ALWAYS check agents first.

    Returns: Available agents - review descriptions to match user needs.
    Workflow: THIS TOOL → select matching agent → inference_from_prompt()
    """
    headers = {"Authorization": f"Bearer {config.HEISENBERG_TOKEN}"}
    with httpx.Client(headers=headers) as client:
        response = client.get(
            urljoin(config.HEISENBERG_AGENTS_URL, "/api/agent-launchers/me/data-agents")
        )
        raise_for_status(response)
        return parse_agent_list_response(response_as_json(response))


@server.tool()
def inference_from_prompt(agent_id: int, prompt: str) -> dict:
    """
    Queries a specialized agent for current data or domain-specific analysis.

    REQUIRED: Use this after list_of_agents() when agents match user request.

    NEVER skip calling specialized agents when they're available and relevant.
    User questions about current data MUST use agents, not general knowledge.

    This tool covers multiple domains including:
    - Social media analysis and monitoring
    - Political sentiment and discussions
    - Market and financial data
    - Technology and product trends
    - News and current events
    - Entertainment and sports updates
    - Any specialized data collection or analysis

    Args:
        agent_id: ID from list_of_agents()
        prompt: User's question requiring specialized analysis

    Returns: Current data/analysis from the selected specialized agent.

    Workflow: list_of_agents() → match agent to user needs → this tool
    """
    headers = {"Authorization": f"Bearer {config.HEISENBERG_KEY}"}

    payload = {"prompt": prompt, "agent_id": agent_id}
    with httpx.Client() as client:
        response = client.post(
            urljoin(config.HEISENBERG_INFERENCE_SERVICE_URL, "/api/v1/inference"),
            json=payload,
            headers=headers,
            timeout=30,
        )
        raise_for_status(response)
        return response_as_json(response)


@server.tool()
def twitter_trends_options():
    """
    Get available options for Twitter trend analysis (verticals and time periods).

    MANDATORY: Always call this tool FIRST before twitter_trends() to get valid parameters.

    Use this when users ask about:
    - Twitter trends, discussions, or viral topics
    - Social media buzz or trending conversations
    - What people are talking about on Twitter/X
    - Sentiment or discussions in specific categories
    - Any Twitter/X platform analysis

    Returns: Dictionary containing:
        - verticals: List of available topic categories (e.g., politics, tech, sports)
        - durations: List of available time periods (e.g., 1h, 24h, 7d)

    Workflow: THIS TOOL → review options → twitter_trends() with valid parameters
    """
    headers = {"Authorization": f"Bearer {config.HEISENBERG_KEY}"}
    with httpx.Client() as client:
        response = client.get(
            urljoin(config.HEISENBERG_INFERENCE_SERVICE_URL, "/api/v1/twitter/options"),
            headers=headers,
            timeout=30,
        )
        raise_for_status(response)
        return response_as_json(response)


@server.tool()
def twitter_trends(vertical: str, duration: str):
    """
    Analyze Twitter/X trends for a specific category and time period.

    REQUIRED: Must call twitter_trends_options() FIRST to get valid parameter values.
    Never guess parameters - always verify available options first.

    Use this for:
    - Current trending topics on Twitter/X in specific categories
    - Viral conversations and hashtags analysis
    - Social media sentiment in particular verticals
    - Time-based trend analysis (hourly, daily, weekly)
    - Platform-specific discussions and buzz

    Args:
        vertical: Category from twitter_trends_options() (e.g., "politics", "tech", "sports")
        duration: Time period from twitter_trends_options() (e.g., "1h", "24h", "7d")

    Returns: Twitter trend analysis including:
        - Top trending topics/hashtags
        - Engagement metrics
        - Key conversations and themes
        - Temporal trend patterns

    Workflow: twitter_trends_options() → select parameters → THIS TOOL
    """
    headers = {"Authorization": f"Bearer {config.HEISENBERG_KEY}"}

    payload = {"vertical": vertical, "duration": duration}
    with httpx.Client() as client:
        response = client.post(
            urljoin(
                config.HEISENBERG_INFERENCE_SERVICE_URL, "/api/v1/twitter/inference"
            ),
            json=payload,
            headers=headers,
            timeout=30,
        )
        raise_for_status(response)
        return response_as_json(response)
