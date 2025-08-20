import json
from typing import Optional

from mcp.types import CallToolResult
from pydantic import BaseModel


class AgentToolResult(BaseModel):
    tool_name: str
    result: Optional[str] = None
    is_error: bool = False
    error_message: Optional[str] = None

    @classmethod
    def from_mcp_tool_result(
        cls, tool_name: str, tool_result: CallToolResult
    ) -> "AgentToolResult":
        if tool_result.isError:
            return cls(
                tool_name=tool_name,
                result=None,
                is_error=tool_result.isError,
                error_message=str(tool_result.content),
            )

        # try to use structured content if available
        if tool_result.structuredContent:
            return cls(
                tool_name=tool_name,
                result=json.dumps(tool_result.structuredContent),
                is_error=tool_result.isError,
            )
        # fallback to content if structured content is not available
        elif tool_result.content:
            # TODO try to parse the content using the output schema defined
            #   in the tool schema (if present)
            return cls(
                tool_name=tool_name,
                result=json.dumps(
                    [content.model_dump() for content in tool_result.content]
                ),
                is_error=tool_result.isError,
            )
        # if no content is available, return None
        else:
            return cls(
                tool_name=tool_name,
                result=None,
                is_error=tool_result.isError,
                error_message="No content returned from tool `{tool_name}`",
            )
