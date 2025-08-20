from typing import Any, Dict, Optional

from mcp import Tool
from pydantic import BaseModel

from rasa.agents.constants import (
    TOOL_ADDITIONAL_PROPERTIES_KEY,
    TOOL_DESCRIPTION_KEY,
    TOOL_NAME_KEY,
    TOOL_PARAMETERS_KEY,
    TOOL_PROPERTIES_KEY,
    TOOL_PROPERTY_TYPE_KEY,
    TOOL_REQUIRED_KEY,
    TOOL_STRICT_KEY,
    TOOL_TYPE_FUNCTION_KEY,
    TOOL_TYPE_KEY,
)


class AgentToolSchema(BaseModel):
    name: str
    parameters: dict[str, Any]
    strict: bool
    description: Optional[str] = None
    type: str = "function"

    @classmethod
    def from_mcp_tool(cls, tool: Tool) -> "AgentToolSchema":
        """Convert MCP Tool to AgentToolSchema."""
        parameters = tool.inputSchema.copy() if tool.inputSchema else {}

        if parameters:
            cls._validate_and_fix_parameters(parameters)

        return cls(
            name=tool.name,
            description=tool.description,
            parameters=parameters,
            strict=False,
            type=TOOL_TYPE_FUNCTION_KEY,
        )

    @classmethod
    def from_openai_json_format(cls, tool: Dict[str, Any]) -> "AgentToolSchema":
        """Convert OpenAI dict format to AgentToolSchema."""
        function_data = tool[TOOL_TYPE_FUNCTION_KEY]
        parameters = function_data.get(TOOL_PARAMETERS_KEY, {})

        if parameters:
            cls._validate_and_fix_parameters(parameters)

        return cls(
            name=function_data[TOOL_NAME_KEY],
            description=function_data[TOOL_DESCRIPTION_KEY],
            parameters=parameters,
            strict=function_data.get(TOOL_STRICT_KEY, False),
            type=tool[TOOL_TYPE_KEY],
        )

    @staticmethod
    def _validate_and_fix_parameters(parameters: Dict[str, Any]) -> None:
        """Validate and fix parameters to ensure they meet OpenAI function calling
        requirements."""
        if not parameters:
            return

        # Ensure additionalProperties is set at the top level
        if TOOL_ADDITIONAL_PROPERTIES_KEY not in parameters:
            parameters[TOOL_ADDITIONAL_PROPERTIES_KEY] = False

        # Ensure required is set at the top level
        if TOOL_REQUIRED_KEY not in parameters:
            parameters[TOOL_REQUIRED_KEY] = []

        # Ensure all properties have types, required field and additionalProperties
        if TOOL_PROPERTIES_KEY in parameters:
            AgentToolSchema._ensure_property_types(parameters)

    @staticmethod
    def _ensure_property_types(parameters: Dict[str, Any]) -> None:
        """Ensure all properties in parameters have a type defined and
        additionalProperties is set."""
        properties = parameters[TOOL_PROPERTIES_KEY]

        if not properties:
            return

        for _, prop_schema in properties.items():
            if not isinstance(prop_schema, dict):
                continue

            # Ensure the property has a type
            if TOOL_PROPERTY_TYPE_KEY not in prop_schema:
                prop_schema[TOOL_PROPERTY_TYPE_KEY] = "string"

            # If it's an object type, ensure additionalProperties and required
            # fields are set
            if prop_schema[TOOL_PROPERTY_TYPE_KEY] == "object":
                if TOOL_ADDITIONAL_PROPERTIES_KEY not in prop_schema:
                    prop_schema[TOOL_ADDITIONAL_PROPERTIES_KEY] = False

                # Ensure required key exists for object properties
                if TOOL_REQUIRED_KEY not in prop_schema:
                    prop_schema[TOOL_REQUIRED_KEY] = []

    def to_openai_json_format(self) -> Dict[str, Any]:
        """Convert AgentToolSchema to OpenAI format."""
        # Ensure the schema is valid before conversion
        return {
            TOOL_TYPE_KEY: TOOL_TYPE_FUNCTION_KEY,
            TOOL_TYPE_FUNCTION_KEY: self.model_dump(exclude={TOOL_TYPE_KEY}),
        }
