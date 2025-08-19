from _typeshed import Incomplete
from gllm_agents.agent import LangGraphReactAgent as LangGraphReactAgent
from gllm_agents.examples.tools.image_artifact_tool import ImageArtifactTool as ImageArtifactTool
from gllm_agents.examples.tools.langchain_currency_exchange_tool import CurrencyExchangeTool as CurrencyExchangeTool
from gllm_agents.examples.tools.langchain_graph_artifact_tool import GraphArtifactCommandTool as GraphArtifactCommandTool
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager

logger: Incomplete
SERVER_AGENT_NAME: str

def main(host: str, port: int):
    """Runs the Currency Exchange A2A server with metadata support."""
