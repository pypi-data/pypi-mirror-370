from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from rasa.shared.core.events import Event


class AgentInput(BaseModel):
    """A class that represents the schema of the input to the agent."""

    id: str
    user_message: str
    slots: Dict[str, Any]
    conversation_history: str
    events: List[Event]
    metadata: Dict[str, Any]
    timestamp: Optional[str] = None

    class Config:
        """Skip validation for Event class as pydantic does not know how to
        serialize or handle instances of the class.
        """

        arbitrary_types_allowed = True
