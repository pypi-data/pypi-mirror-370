from gllm_agents.utils.artifact_helpers import create_artifact_command as create_artifact_command
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langchain_core.tools import BaseTool
from langgraph.types import Command as Command
from pydantic import BaseModel
from typing import Any, ClassVar

class CurrencyExchangeInput(BaseModel):
    """Input schema for currency exchange tool."""
    from_currency: str
    to_currency: str
    amount: float

class CurrencyExchangeTool(BaseTool):
    """Currency exchange tool with tenant-based pricing and authentication.

    This tool demonstrates how to use A2A metadata for:
    1. Tenant-based authentication
    2. Different exchange rates per tenant
    3. Different service levels based on tenant tier
    """
    name: str
    description: str
    args_schema: type[BaseModel]
    TENANT_CONFIG: ClassVar[dict[str, Any]]
