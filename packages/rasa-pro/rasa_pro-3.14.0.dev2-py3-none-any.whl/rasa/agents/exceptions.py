from rasa.exceptions import RasaException


class AgentNotFoundException(RasaException):
    """Raised when an agent is not found."""

    def __init__(self, agent_name: str):
        super().__init__(f"The agent {agent_name} is not defined.")
