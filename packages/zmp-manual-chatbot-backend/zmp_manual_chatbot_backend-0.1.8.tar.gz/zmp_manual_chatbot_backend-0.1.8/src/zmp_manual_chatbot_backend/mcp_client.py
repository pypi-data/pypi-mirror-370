# NOTE: You must add 'fastmcp' to your pyproject.toml dependencies for this client to work.
from typing import Any, Dict, List, Optional
from .config import settings
import asyncio
import logging

try:
    from fastmcp import Client as FastMCPClient
except ImportError:
    FastMCPClient = None  # Placeholder for type checking

class MCPClient:
    """
    Official MCP client using FastMCP (https://gofastmcp.com/clients/client).
    Usage:
        async with MCPClient() as client:
            result = await client.call_tool("search_knowledge", {"query": query, ...})
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.MCP_SERVER_URL
        self._client: Optional[FastMCPClient] = None
        
    def _log_connection_attempt(self):
        """Log connection attempt details for debugging."""
        logging.info(f"[MCP_CLIENT] Attempting to connect to: {self.base_url}")
        logging.info("[MCP_CLIENT] Cross-cluster connection: sre → ags cluster")
        logging.info("[MCP_CLIENT] Using FastMCP client for MCP protocol handshake")

    async def __aenter__(self):
        if FastMCPClient is None:
            raise ImportError("fastmcp is not installed. Please add it to your dependencies.")
        
        self._log_connection_attempt()
        
        try:
            logging.info(f"[MCP_CLIENT] Creating FastMCP client (version: fastmcp>=2.10.5)")
            self._client = FastMCPClient(self.base_url)
            logging.info("[MCP_CLIENT] FastMCP client created, initiating connection...")
            await self._client.__aenter__()
            logging.info("[MCP_CLIENT] Successfully connected to MCP server")
            
            # Test basic connectivity with a ping
            try:
                await self.health_check()
                logging.info("[MCP_CLIENT] MCP server health check passed")
            except Exception as health_e:
                logging.warning(f"[MCP_CLIENT] Health check failed but connection succeeded: {health_e}")
            
            return self
        except Exception as e:
            logging.error(f"[MCP_CLIENT] Connection failed: {str(e)}")
            logging.error(f"[MCP_CLIENT] Error type: {type(e).__name__}")
            logging.error(f"[MCP_CLIENT] FastMCP client version: 2.10.5")
            
            # Enhanced debugging for session termination
            if "Session terminated" in str(e):
                logging.error("[MCP_CLIENT] === MCP PROTOCOL HANDSHAKE FAILURE ===")
                logging.error("[MCP_CLIENT] The MCP server terminated the session during initialization")
                logging.error("[MCP_CLIENT] Possible causes:")
                logging.error("[MCP_CLIENT]   1. MCP server FastMCP version mismatch (client: 2.10.5)")
                logging.error("[MCP_CLIENT]   2. MCP server not properly implementing protocol handshake")
                logging.error("[MCP_CLIENT]   3. Server-side initialization errors or crashes")
                logging.error("[MCP_CLIENT]   4. Protocol version incompatibility")
                logging.error("[MCP_CLIENT] Check MCP server startup logs for initialization errors")
                logging.error(f"[MCP_CLIENT] Server URL: {self.base_url}")
            elif "Connection" in str(e) or "timeout" in str(e).lower():
                logging.error("[MCP_CLIENT] Network connectivity issue between sre and ags clusters")
                logging.error("[MCP_CLIENT] Check ingress, service, and DNS resolution")
            else:
                logging.error("[MCP_CLIENT] Unknown error - check MCP server implementation")
                
            # Don't raise exception yet - let the agent handle this gracefully
            raise RuntimeError(f"Cross-cluster MCP connection failed: {str(e)}") from e

    async def __aexit__(self, exc_type, exc, tb):
        if self._client:
            await self._client.__aexit__(exc_type, exc, tb)
            self._client = None

    async def call_tool(self, tool_name: str, payload: Dict[str, Any], retry: int = 3, delay: float = 1.0) -> Any:
        """
        Call an MCP tool endpoint using FastMCP's call_tool method.
        Retries on failure.
        Returns the raw result (see FastMCP docs for details).
        """
        for attempt in range(retry):
            try:
                if not self._client:
                    raise RuntimeError("MCPClient must be used as an async context manager.")
                result = await self._client.call_tool(tool_name, payload)
                return result
            except Exception as e:
                if attempt < retry - 1:
                    await asyncio.sleep(delay)
                else:
                    raise e
        return None

    @staticmethod
    def extract_structured_content(result: Any) -> Any:
        """
        Helper to extract 'structured_content' from a FastMCP CallToolResult, if present.
        """
        if hasattr(result, 'structured_content'):
            return result.structured_content
        return result

    async def health_check(self) -> Dict[str, Any]:
        """
        Ping the MCP server to check connectivity.
        """
        if not self._client:
            raise RuntimeError("MCPClient must be used as an async context manager.")
        try:
            await self._client.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def list_threads(self, user_id: str) -> Dict[str, Any]:
        """
        List all threads for a specific user using the list_threads MCP tool.
        
        Args:
            user_id: User ID to list threads for
            
        Returns:
            Dictionary containing user_id and threads list with thread_id and thread_title
        """
        payload = {"user_id": user_id}
        return await self.call_tool("list_threads", payload)

    async def get_thread(self, user_id: str, thread_id: str) -> Dict[str, Any]:
        """
        Get conversation history for a specific thread using the get_thread MCP tool.
        
        Args:
            user_id: User ID that owns the thread
            thread_id: Thread ID to retrieve conversation for
            
        Returns:
            Dictionary containing user_id, thread_id, and records array (newest first)
        """
        payload = {"user_id": user_id, "thread_id": thread_id}
        return await self.call_tool("get_thread", payload)
