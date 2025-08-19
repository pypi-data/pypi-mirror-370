from _typeshed import Incomplete
from gllm_agents.agent.base_langgraph_agent import BaseLangGraphAgent as BaseLangGraphAgent
from gllm_agents.utils import add_references_chunks as add_references_chunks
from gllm_agents.utils.langgraph import convert_langchain_messages_to_multimodal_prompt as convert_langchain_messages_to_multimodal_prompt, convert_lm_output_to_langchain_message as convert_lm_output_to_langchain_message
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema import Chunk
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage as BaseMessage
from langchain_core.tools import BaseTool as BaseTool
from langgraph.graph import StateGraph as StateGraph
from langgraph.graph.message import add_messages as add_messages
from langgraph.graph.state import CompiledStateGraph as CompiledStateGraph
from langgraph.managed import IsLastStep as IsLastStep, RemainingSteps as RemainingSteps
from typing import Any, Sequence
from typing_extensions import Annotated, TypedDict

logger: Incomplete
DEFAULT_INSTRUCTION: str
SAVE_OUTPUT_HISTORY: str
FORMAT_AGENT_REFERENCE: str

class ReactAgentState(TypedDict):
    """State schema for the ReAct agent.

    Includes messages, step tracking, optional event emission support, artifacts, references, and metadata.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
    event_emitter: EventEmitter | None
    artifacts: list[dict[str, Any]] | None
    references: Annotated[list[Chunk], add_references_chunks]
    metadata: dict[str, Any] | None

class LangGraphReactAgent(BaseLangGraphAgent):
    """A ReAct agent template built on LangGraph.

    This agent can use either:
    - An LMInvoker (if self.lm_invoker is set by BaseAgent)
    - A LangChain BaseChatModel (if self.model is set by BaseAgent)

    The graph structure follows the standard ReAct pattern:
    agent -> tools -> agent (loop) -> END
    """
    def __init__(self, name: str, instruction: str = ..., model: BaseChatModel | str | Any | None = None, tools: Sequence[BaseTool] | None = None, agents: Sequence[Any] | None = None, description: str | None = None, thread_id_key: str = 'thread_id', event_emitter: EventEmitter | None = None, **kwargs: Any) -> None:
        """Initialize the LangGraph ReAct Agent.

        Args:
            name: The name of the agent.
            instruction: The system instruction for the agent.
            model: The model to use (lm_invoker, LangChain model, string, etc.).
            tools: Sequence of LangChain tools available to the agent.
            agents: Optional sequence of sub-agents for delegation (coordinator mode).
            description: Human-readable description of the agent.
            thread_id_key: Key for thread ID in configuration.
            event_emitter: Optional event emitter for streaming updates.
            **kwargs: Additional keyword arguments passed to BaseLangGraphAgent.
        """
    def define_graph(self, graph_builder: StateGraph) -> CompiledStateGraph:
        """Define the ReAct agent graph structure.

        Args:
            graph_builder: The StateGraph builder to define the graph structure.

        Returns:
            Compiled LangGraph ready for execution.
        """

class LangGraphAgent(LangGraphReactAgent):
    """Alias for LangGraphReactAgent."""
class LangChainAgent(LangGraphReactAgent):
    """Alias for LangGraphReactAgent."""
