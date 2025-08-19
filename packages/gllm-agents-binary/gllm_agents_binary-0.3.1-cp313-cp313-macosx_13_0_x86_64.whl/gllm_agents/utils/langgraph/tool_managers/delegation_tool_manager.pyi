from _typeshed import Incomplete
from gllm_agents.agent.base_agent import BaseAgent as BaseAgent
from gllm_agents.utils.artifact_helpers import create_delegation_response_with_artifacts as create_delegation_response_with_artifacts, extract_artifacts_from_agent_response as extract_artifacts_from_agent_response
from gllm_agents.utils.langgraph.tool_managers.base_tool_manager import BaseLangGraphToolManager as BaseLangGraphToolManager
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.tools import BaseTool as BaseTool

logger: Incomplete

class DelegationToolManager(BaseLangGraphToolManager):
    """Manages internal agent delegation tools for LangGraph agents.

    This tool manager converts internal agent instances into LangChain tools
    that can be used for task delegation within a unified ToolNode. Each
    delegated agent becomes a tool that the coordinator can call.

    Simplified version following legacy BaseLangChainAgent patterns.
    """
    registered_agents: list[BaseAgent]
    def __init__(self) -> None:
        """Initialize the delegation tool manager."""
    created_tools: Incomplete
    def register_resources(self, agents: list[BaseAgent]) -> list[BaseTool]:
        """Register internal agents for delegation and convert them to tools.

        Args:
            agents: List of BaseAgent instances for internal task delegation.

        Returns:
            List of created delegation tools.
        """
    def get_resource_names(self) -> list[str]:
        """Get names of all registered delegation agents.

        Returns:
            list[str]: A list of names of all registered delegation agents.
        """
