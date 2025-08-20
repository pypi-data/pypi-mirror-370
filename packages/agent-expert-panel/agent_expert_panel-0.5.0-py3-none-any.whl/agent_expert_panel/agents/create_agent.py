"""
Used to create an agent from a config file.
"""

from typing import List, Callable
from agent_expert_panel.models.config import AgentConfig
from agent_expert_panel.tools import BUILTIN_TOOLS, get_tools_by_names
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from autogen_agentchat.agents import AssistantAgent


def create_agent(
    config: AgentConfig,
    additional_tools: List[Callable] = None,
    available_tools: dict = None,
) -> AssistantAgent:
    """
    Create an agent from configuration with optional tools.

    Args:
        config: Agent configuration
        additional_tools: Additional tool functions to add to the agent
        available_tools: Dictionary of available tools (defaults to BUILTIN_TOOLS)
    """
    model_client = OpenAIChatCompletionClient(
        model=config.model_name,
        base_url=config.openai_base_url,
        api_key=config.openai_api_key,
        model_info=ModelInfo(**config.model_info.model_dump()),
    )

    # Start with available tools (built-in by default)
    tools_dict = available_tools or BUILTIN_TOOLS.copy()

    # Collect tools to pass to the agent
    agent_tools = []

    # 1. Tools from config (YAML-defined)
    if config.tools:
        tool_names = []
        for tool_spec in config.tools:
            if isinstance(tool_spec, str):
                tool_names.append(tool_spec)
            elif isinstance(tool_spec, dict) and "name" in tool_spec:
                tool_names.append(tool_spec["name"])

        if tool_names:
            try:
                config_tools = get_tools_by_names(tool_names, tools_dict)
                agent_tools.extend(config_tools)
            except ValueError as e:
                print(f"Warning: {e}")

    # 2. Additional tools (programmatically provided)
    if additional_tools:
        agent_tools.extend(additional_tools)

    agent = AssistantAgent(
        name=config.name,
        model_client=model_client,
        system_message=config.system_message,
        reflect_on_tool_use=config.reflect_on_tool_use,
        tools=agent_tools if agent_tools else None,
    )

    return agent
