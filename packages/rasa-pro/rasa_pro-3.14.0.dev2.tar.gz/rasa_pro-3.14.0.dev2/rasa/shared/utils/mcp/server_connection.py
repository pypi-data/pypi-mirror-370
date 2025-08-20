"""MCP server connection utilities."""

import asyncio
from contextlib import AsyncExitStack
from typing import Any, Dict, Optional

import structlog
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

structlogger = structlog.get_logger()


class MCPServerConnection:
    """
    Manages connection to an MCP server.

    This class handles the lifecycle of connections to MCP servers,
    including connection establishment, session management, and cleanup.
    """

    def __init__(self, server_name: str, server_url: str, server_type: str):
        """
        Initialize the MCP server connection.

        Args:
            server_name: Server name to identify the server
            server_url: Server URL
            server_type: Server type (currently only 'http' is supported)
        """
        self.server_name = server_name
        self.server_url = server_url
        self.server_type = server_type
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None

    @classmethod
    def from_config(cls, server_config: Dict[str, Any]) -> "MCPServerConnection":
        """Initialize the MCP server connection from a configuration dictionary."""
        return cls(
            server_config["name"],
            server_config["url"],
            server_config.get("type", "http"),
        )

    async def connect(self) -> None:
        """Establish connection to the MCP server.

        Raises:
            ValueError: If the server type is not supported.
            ConnectionError: If connection fails.
        """
        if self.server_type != "http":
            raise ValueError(f"Unsupported server type: {self.server_type}")

        # Create a new exit stack for this connection to avoid task boundary issues
        self.exit_stack = AsyncExitStack()

        try:
            read_stream, write_stream, _ = await self.exit_stack.enter_async_context(
                streamablehttp_client(self.server_url)
            )
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await self.session.initialize()
        except asyncio.CancelledError as e:
            event_info = f"Connection to MCP server {self.server_name} was cancelled."
            structlogger.error(
                "mcp_server_connection.connect.connection_cancelled",
                event_info=event_info,
                server_name=self.server_name,
                server_url=self.server_url,
            )
            # Clean up on cancellation
            await self._cleanup()
            raise ConnectionError(e)

        except Exception as e:
            event_info = f"Failed to connect to MCP server {self.server_name}: {e}"
            structlogger.error(
                "mcp_server_connection.connect.connection_failed",
                event_info=event_info,
                server_name=self.server_name,
                server_url=self.server_url,
            )
            # Clean up on error
            await self._cleanup()
            raise ConnectionError(e)

    async def ensure_active_session(self) -> ClientSession:
        """
        Ensure an active session is available.

        If no session exists or the current session is inactive,
        a new connection will be established.

        Returns:
            Active ClientSession instance.
        """
        if self.session is None:
            await self.connect()
            structlogger.info(
                "mcp_server_connection.ensure_active_session.no_session",
                server_name=self.server_name,
                server_url=self.server_url,
                event_info=(
                    "No session found, connecting to the server "
                    f"`{self.server_name}` @ `{self.server_url}`"
                ),
            )
        if self.session:
            try:
                await self.session.send_ping()
            except Exception as e:
                structlogger.error(
                    "mcp_server_connection.ensure_active_session.ping_failed",
                    error=str(e),
                    server_name=self.server_name,
                    server_url=self.server_url,
                    event_info=(
                        "Ping failed, trying to reconnect to the server "
                        f"`{self.server_name}` @ `{self.server_url}`"
                    ),
                )
                await self.connect()
                structlogger.info(
                    "mcp_server_connection.ensure_active_session.reconnected",
                    server_name=self.server_name,
                    server_url=self.server_url,
                    event_info=(
                        "Reconnected to the server "
                        f"`{self.server_name}` @ `{self.server_url}`"
                    ),
                )
        assert self.session is not None  # Ensures type for mypy
        return self.session

    async def close(self) -> None:
        """Close the connection and clean up resources."""
        await self._cleanup()

    async def _cleanup(self) -> None:
        """Internal cleanup method to safely close resources."""
        if self.exit_stack:
            try:
                await self.exit_stack.aclose()
            except Exception as e:
                # Log cleanup errors but don't raise them
                structlogger.warning(
                    "mcp_server_connection.cleanup.failed",
                    server_name=self.server_name,
                    error=str(e),
                )
            finally:
                self.exit_stack = None
                self.session = None
