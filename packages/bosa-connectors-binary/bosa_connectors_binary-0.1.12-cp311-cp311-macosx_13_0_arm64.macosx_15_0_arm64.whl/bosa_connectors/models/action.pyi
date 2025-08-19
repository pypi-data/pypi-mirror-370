from bosa_connectors.models.file import ConnectorFile as ConnectorFile
from pydantic import BaseModel
from typing import Any

class ActionResponseData(BaseModel):
    """Response data model with data and meta information."""
    data: list[Any] | dict[str, Any] | ConnectorFile
    meta: dict[str, Any] | None

class InitialExecutorRequest(BaseModel):
    """Initial executor request model."""
    params: dict[str, Any]
    headers: dict[str, str] | None
    max_attempts: int | None
    token: str | None
    account: str | None
    timeout: int | None
