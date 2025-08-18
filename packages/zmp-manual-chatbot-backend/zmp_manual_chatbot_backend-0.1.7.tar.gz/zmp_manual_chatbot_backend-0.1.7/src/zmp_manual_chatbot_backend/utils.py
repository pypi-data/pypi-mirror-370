"""
Utility functions and classes for the ZMP Manual Chatbot Backend.

This module provides essential utility functions for:
- LLM provider management (Ollama, OpenAI)
- Model initialization and health checks
- MCP (Model Context Protocol) result parsing
- Session state management
- File I/O operations for session persistence

The utilities support automatic fallback between LLM providers and provide
robust error handling for external service dependencies.
"""

from src.zmp_manual_chatbot_backend.config import settings
import os
import subprocess
import requests
import time
import json
import logging
import asyncio
import base64
from typing import Optional

TMP_DIR = "./tmp"


def ensure_ollama_running() -> bool:
    """
    Ensure Ollama service is running and accessible.
    
    This function checks if the Ollama service is already running by making a
    request to its API. If the service is not running, it attempts to start it
    in the background and waits for it to become available.
    
    Returns:
        bool: True if Ollama service is running and accessible, False if it
              failed to start or become available within the timeout period.
              
    Note:
        - Has a 30-second timeout for service startup
        - Starts Ollama service with stdout/stderr redirected to avoid console output
        - Uses a polling mechanism with 1-second intervals to check availability
        
    Example:
        if ensure_ollama_running():
            print("Ollama is ready to use")
        else:
            print("Failed to start Ollama service")
    """
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("🚀 Starting Ollama service...")
    try:
        # Start Ollama in background
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama service started successfully")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        print("❌ Failed to start Ollama service")
        return False
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False


def ensure_ollama_model_pulled(model_name: str) -> bool:
    """
    Ensure the specified Ollama model is downloaded and available.
    
    This function checks if the specified model exists in the local Ollama
    installation. If the model is not found, it attempts to download it
    using the 'ollama pull' command.
    
    Args:
        model_name (str): The name and tag of the model to ensure is available
                         (e.g., 'llama3.2:3b', 'qwen2:1.5b')
    
    Returns:
        bool: True if the model is available (either already present or 
              successfully downloaded), False if download failed or timed out.
              
    Note:
        - Has a 30-minute timeout for model downloads
        - Large models (>2GB) may take significant time on first download
        - Progress is displayed to the console during download
        
    Example:
        if ensure_ollama_model_pulled('llama3.2:3b'):
            print("Model is ready to use")
        else:
            print("Failed to download model")
    """
    try:
        # Check if model exists
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            existing_models = [model["name"] for model in models]
            
            if model_name in existing_models:
                print(f"✅ Model {model_name} is already available")
                return True
        
        print(f"📥 Downloading model {model_name}...")
        print("This may take a few minutes for the first time...")
        
        # Pull the model
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Model {model_name} downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download model {model_name}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout downloading model {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading model {model_name}: {e}")
        return False


def get_llm() -> object:
    """
    Create and return the appropriate LLM client based on configuration.
    
    This factory function creates the correct LLM client instance based on the
    effective LLM provider determined by the settings. It handles provider-specific
    initialization, dependency checking, and service availability verification.
    
    Returns:
        object: An initialized LLM client instance. The specific type depends on
                the provider:
                - ChatOllama for Ollama provider
                - ChatOpenAI for OpenAI provider
    
    Raises:
        ImportError: If required provider-specific dependencies are not installed
        RuntimeError: If the selected provider service is not available
        ValueError: If required configuration (e.g., API keys) is missing
    
    Provider Priority:
        1. Ollama (if service is available)
        2. OpenAI (if API key is configured)
    
    Example:
        try:
            llm = get_llm()
            response = llm.invoke("Hello, world!")
        except RuntimeError as e:
            print(f"LLM initialization failed: {e}")
    """
    provider = settings.effective_llm_provider
    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError("langchain-ollama must be installed for Ollama support. Run: pip install langchain-ollama")
        if not ensure_ollama_running():
            raise RuntimeError("Failed to start Ollama service")
        if not ensure_ollama_model_pulled(settings.OLLAMA_MODEL):
            raise RuntimeError(f"Failed to download Ollama model: {settings.OLLAMA_MODEL}")
        return ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
            num_predict=settings.OLLAMA_NUM_PREDICT,
            top_k=settings.OLLAMA_TOP_K,
            top_p=settings.OLLAMA_TOP_P,
        )
    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai must be installed for OpenAI support. Run: pip install langchain-openai")
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set when using OpenAI provider")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0,
            max_tokens=2000,
        )
    else:
        raise RuntimeError(
            f"No valid LLM provider available. Set LLM_PROVIDER to 'ollama' or 'openai'. Current: {settings.LLM_PROVIDER}, effective: {provider}"
        )


def get_model_info() -> dict:
    """
    Get comprehensive information about the current LLM model configuration.
    
    This function returns detailed information about the currently configured
    LLM provider and model, including configuration parameters and availability status.
    
    Returns:
        dict: A dictionary containing model configuration information with keys:
              - provider: The LLM provider name ('ollama', 'openai', or 'unknown')
              - model: The model name/identifier
              - Additional provider-specific configuration parameters
              
    Example:
        info = get_model_info()
        print(f"Using {info['provider']} with model {info['model']}")
        
        # Output examples:
        # {'provider': 'ollama', 'model': 'llama3.2:3b', 'base_url': '...', ...}
        # {'provider': 'openai', 'model': 'gpt-3.5-turbo', 'has_api_key': True}
    """
    provider = settings.effective_llm_provider
    if provider == "ollama":
        return {
            "provider": "ollama",
            "model": settings.OLLAMA_MODEL,
            "base_url": settings.OLLAMA_BASE_URL,
            "temperature": settings.OLLAMA_TEMPERATURE
        }
    elif provider == "openai":
        return {
            "provider": "openai", 
            "model": settings.OPENAI_MODEL,
            "has_api_key": bool(settings.OPENAI_API_KEY)
        }
    else:
        return {"provider": "unknown"}


def extract_mcp_results(mcp_result) -> list:
    """
    Extract results from MCP (Model Context Protocol) server response.
    
    This helper function parses various response formats from MCP servers and
    extracts the actual results list. It handles multiple response formats for
    backward compatibility and robust parsing.
    
    Args:
        mcp_result: The response object from MCP server, which can be:
                   - CallToolResult with structured_content
                   - Dictionary with 'results' key
                   - List of result objects
    
    Returns:
        list: A list of result dictionaries extracted from the MCP response.
              Returns empty list if no results are found or parsing fails.
    
    Response Format Handling:
        1. FastMCP CallToolResult with 'structured_content' 
        2. Dictionary with 'results' key
        3. List of CallToolResult objects with content
        4. Legacy format with JSON text content
    
    Example:
        mcp_response = await mcp_client.search_knowledge_base("query")
        results = extract_mcp_results(mcp_response)
        for result in results:
            print(f"Content: {result.get('content', 'N/A')}")
    """
    # Handle CallToolResult with content list containing TextContent
    if hasattr(mcp_result, 'content') and mcp_result.content:
        content_list = mcp_result.content
        if isinstance(content_list, list) and content_list:
            text_content = content_list[0]
            if hasattr(text_content, "text"):
                try:
                    parsed = json.loads(text_content.text)
                    return parsed.get("results", [])
                except Exception as e:
                    print(f"Error parsing MCP result text: {e}")
                    return []

    # Handle FastMCP CallToolResult with 'structured_content'
    if hasattr(mcp_result, 'structured_content') and mcp_result.structured_content:
        content = mcp_result.structured_content
        if isinstance(content, dict):
            return content.get('results', [])
        elif isinstance(content, list):
            # Sometimes structured_content is a list of dicts
            return content
    
    # Fallback: handle dict with 'results'
    if isinstance(mcp_result, dict) and 'results' in mcp_result:
        return mcp_result['results']
    
    # Legacy fallback: try to parse as before
    if isinstance(mcp_result, list) and mcp_result:
        result_obj = mcp_result[0]
        if hasattr(result_obj, "content") and result_obj.content:
            text_content = result_obj.content[0]
            if hasattr(text_content, "text"):
                try:
                    parsed = json.loads(text_content.text)
                    return parsed.get("results", [])
                except Exception as e:
                    print(f"Error parsing MCP result text: {e}")
                    return []
    return []

async def _save_plan_execute(session_id: str, state: dict) -> None:
    """
    Save PlanExecute state to persistent storage for session management.
    
    This function asynchronously saves the current state of a PlanExecute workflow
    to a JSON file in the temporary directory. The file is named with the session ID
    and a .json extension to enable state recovery and session persistence across requests.
    
    Args:
        session_id (str): Unique identifier for the session
        state (dict): The PlanExecute state dictionary to save
    
    Raises:
        Exception: If file writing fails or JSON serialization fails
        
    Note:
        - Creates the tmp directory if it doesn't exist
        - Uses UTF-8 encoding for proper character support
        - Runs file I/O in a thread to avoid blocking the event loop
        - Files are saved with .json extension for clarity
        
    Example:
        await _save_plan_execute("session_123", {
            "query": "User question",
            "plan": ["step1", "step2"],
            "current_step": "planning"
        })
    """
    os.makedirs(TMP_DIR, exist_ok=True)
    file_path = os.path.join(TMP_DIR, f"{session_id}.json")
    try:
        state_copy = state.copy()
        
        # Extract session_dialogue for later placement at bottom
        session_dialogue_data = None
        if "session_dialogue" in state_copy and state_copy["session_dialogue"]:
            serializable_dialogue = []
            for message in state_copy["session_dialogue"]:
                if hasattr(message, 'content') and hasattr(message, 'type'):
                    # Convert LangChain message to dict
                    serializable_dialogue.append({
                        "type": message.type,
                        "content": message.content
                    })
                elif isinstance(message, dict):
                    # Already serializable
                    serializable_dialogue.append(message)
                else:
                    # Fallback for other types
                    serializable_dialogue.append({"type": "unknown", "content": str(message)})
            session_dialogue_data = serializable_dialogue
            # Remove from state_copy to add at the end
            del state_copy["session_dialogue"]
        
        # Remove other non-serializable fields if needed
        # for field in ['session_queue']:
        #     state_copy.pop(field, None)
        def write_file():
            with open(file_path, "w", encoding="utf-8") as f:
                # Create ordered dict to control field order
                ordered_state = {}
                # Add all fields except session_dialogue first
                for key, value in state_copy.items():
                    ordered_state[key] = value
                # Add session_dialogue at the end if it exists
                if session_dialogue_data is not None:
                    ordered_state["session_dialogue"] = session_dialogue_data
                json.dump(ordered_state, f, ensure_ascii=False, indent=2)
        await asyncio.to_thread(write_file)
        logging.info(f"PlanExecute for session '{session_id}' saved to {file_path}")
    except Exception as e:
        logging.error(f"Failed to save PlanExecute for session '{session_id}': {e}")
        raise

async def _load_plan_execute(session_id: str) -> Optional[dict]:
    """
    Load PlanExecute state from persistent storage.
    
    This function asynchronously loads a previously saved PlanExecute state
    from a JSON file in the temporary directory. It enables session recovery
    and state persistence across requests.
    
    Args:
        session_id (str): Unique identifier for the session to load
    
    Returns:
        Optional[dict]: The loaded PlanExecute state dictionary, or None if:
                       - The session file doesn't exist
                       - File reading fails
                       - JSON parsing fails
                       
    Note:
        - Runs file I/O in a thread to avoid blocking the event loop
        - Uses UTF-8 encoding for proper character support
        - Handles missing files gracefully by returning None
        - Looks for files with .json extension
        
    Example:
        state = await _load_plan_execute("session_123")
        if state:
            current_step = state.get("current_step", "unknown")
            print(f"Resumed session at step: {current_step}")
        else:
            print("No saved state found, starting new session")
    """
    file_path = os.path.join(TMP_DIR, f"{session_id}.json")
    try:
        if not os.path.exists(file_path):
            return None
        def read_file():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        state = await asyncio.to_thread(read_file)
        
        # Convert serialized dialogue back to LangChain messages
        if "session_dialogue" in state and state["session_dialogue"]:
            from langchain_core.messages import HumanMessage, AIMessage
            dialogue_messages = []
            for msg_dict in state["session_dialogue"]:
                if isinstance(msg_dict, dict) and "type" in msg_dict and "content" in msg_dict:
                    if msg_dict["type"] == "human":
                        dialogue_messages.append(HumanMessage(content=msg_dict["content"]))
                    elif msg_dict["type"] == "ai":
                        dialogue_messages.append(AIMessage(content=msg_dict["content"]))
                    else:
                        # Keep as dict for unknown types
                        dialogue_messages.append(msg_dict)
                else:
                    # Keep as-is if not in expected format
                    dialogue_messages.append(msg_dict)
            state["session_dialogue"] = dialogue_messages
            
        logging.info(f"PlanExecute for session '{session_id}' loaded from {file_path}")
        return state
    except Exception as e:
        logging.error(f"Failed to load PlanExecute for session '{session_id}': {e}")
        return None

async def set_plan_execute(session_id: str, updates: dict) -> dict:
    """
    Update and persist PlanExecute state for a session.
    
    This function loads the existing PlanExecute state for a session (if any),
    applies the provided updates, and saves the updated state back to persistent
    storage. It's used to incrementally update session state during workflow execution.
    
    Args:
        session_id (str): Unique identifier for the session
        updates (dict): Dictionary of key-value pairs to update in the state.
                       Keys should match PlanExecute schema fields.
    
    Returns:
        dict: The complete updated state dictionary after applying changes
        
    Example:
        # Update query and current step
        updated_state = await set_plan_execute("session_123", {
            "current_step": "planning",
            "query": "Updated user question",
            "plan": ["analyze", "research", "respond"]
        })
        
        print(f"Session now at: {updated_state['current_step']}")
    """
    state = await _load_plan_execute(session_id) or {}
    state.update(updates)
    await _save_plan_execute(session_id, state)
    return state

async def get_plan_execute(session_id: str) -> Optional[dict]:
    """
    Retrieve the current PlanExecute state for a session.
    
    This function loads the current state of a PlanExecute workflow from
    persistent storage. It's used to access session state during workflow
    execution and for debugging purposes.
    
    Args:
        session_id (str): Unique identifier for the session to retrieve
        
    Returns:
        Optional[dict]: The current PlanExecute state dictionary, or None if:
                       - No state exists for the session
                       - Loading fails due to file errors
                       
    Example:
        state = await get_plan_execute("session_123")
        if state:
            print(f"Current step: {state.get('current_step', 'unknown')}")
            print(f"Query: {state.get('query', 'N/A')}")
            print(f"Plan: {state.get('plan', [])}")
        else:
            print("No session state found")
    """
    return await _load_plan_execute(session_id)

async def delete_session_file(session_id: str) -> bool:
    """
    Delete the session state file for a given session ID.
    
    This function removes the persistent session state file from the tmp directory
    when a session is closed or expired. It's called automatically by the 
    SessionManager during cleanup operations.
    
    Args:
        session_id (str): Unique identifier for the session to delete
        
    Returns:
        bool: True if the file was successfully deleted or didn't exist,
              False if deletion failed due to file system errors
              
    Example:
        success = await delete_session_file("session_123")
        if success:
            print("Session file cleaned up successfully")
        else:
            print("Failed to clean up session file")
    """
    file_path = os.path.join(TMP_DIR, f"{session_id}.json")
    try:
        if os.path.exists(file_path):
            def delete_file():
                os.remove(file_path)
            await asyncio.to_thread(delete_file)
            logging.info(f"Session file deleted: {file_path}")
            return True
        else:
            # File doesn't exist, consider it successfully "deleted"
            logging.debug(f"Session file not found (already deleted): {file_path}")
            return True
    except Exception as e:
        logging.error(f"Failed to delete session file {file_path}: {e}")
        return False

async def cleanup_expired_session_files(max_age_hours: int = 24) -> int:
    """
    Clean up expired session files based on file modification time.
    
    This function scans the tmp directory for session files that are older than
    the specified maximum age and removes them. It's used for periodic cleanup
    of abandoned session files.
    
    Args:
        max_age_hours (int): Maximum age of session files in hours before cleanup.
                            Default is 24 hours.
                            
    Returns:
        int: Number of files that were successfully deleted
        
    Example:
        deleted_count = await cleanup_expired_session_files(max_age_hours=12)
        print(f"Cleaned up {deleted_count} expired session files")
    """
    if not os.path.exists(TMP_DIR):
        return 0
        
    deleted_count = 0
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    
    try:
        def scan_and_delete():
            nonlocal deleted_count
            for filename in os.listdir(TMP_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(TMP_DIR, filename)
                    try:
                        # Check file modification time
                        file_mtime = os.path.getmtime(file_path)
                        if current_time - file_mtime > max_age_seconds:
                            os.remove(file_path)
                            deleted_count += 1
                            logging.info(f"Deleted expired session file: {filename}")
                    except Exception as e:
                        logging.error(f"Error checking/deleting file {filename}: {e}")
                        
        await asyncio.to_thread(scan_and_delete)
        
        if deleted_count > 0:
            logging.info(f"Cleanup completed: {deleted_count} expired session files deleted")
        else:
            logging.debug("No expired session files found during cleanup")
            
        return deleted_count
        
    except Exception as e:
        logging.error(f"Error during session file cleanup: {e}")
        return 0

def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token payload.
    
    Args:
        token: The JWT token string
        
    Returns:
        User ID string if found, None otherwise
    """
    try:
        # JWT tokens have 3 parts separated by dots: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            logging.warning("Invalid JWT token format for user extraction")
            return None
        
        # Decode the payload (second part)
        payload_part = parts[1]
        
        # Add padding if needed for base64 decoding
        missing_padding = len(payload_part) % 4
        if missing_padding:
            payload_part += "=" * (4 - missing_padding)
        
        # Decode base64 payload
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Extract user ID - try common JWT claims
        user_id = payload.get("sub") or payload.get("user_id") or payload.get("preferred_username")
        
        if user_id:
            logging.info(f"Extracted user_id from JWT: {user_id}")
            return str(user_id)
        else:
            logging.warning("No user_id found in JWT payload")
            return None
            
    except Exception as e:
        logging.error(f"Error extracting user_id from JWT token: {e}")
        return None


def extract_user_name_from_token(token: str) -> Optional[str]:
    """
    Extract user name from JWT token payload.
    
    Args:
        token: The JWT token string
        
    Returns:
        User name string if found, None otherwise
    """
    try:
        # JWT tokens have 3 parts separated by dots: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            logging.warning("Invalid JWT token format for user name extraction")
            return None
        
        # Decode the payload (second part)
        payload_part = parts[1]
        
        # Add padding if needed for base64 decoding
        missing_padding = len(payload_part) % 4
        if missing_padding:
            payload_part += "=" * (4 - missing_padding)
        
        # Decode base64 payload
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Extract user name - try common JWT claims for name
        user_name = (payload.get("name") or 
                    payload.get("given_name") or 
                    payload.get("preferred_username") or 
                    payload.get("username") or
                    payload.get("email"))
        
        if user_name:
            logging.info(f"Extracted user_name from JWT: {user_name}")
            return str(user_name)
        else:
            logging.warning("No user_name found in JWT payload")
            return None
            
    except Exception as e:
        logging.error(f"Error extracting user_name from JWT token: {e}")
        return None


def extract_citations_from_results(results, source_name, citation_map, doc_page_to_citation, source_chunks, idx):
    """
    Extract citations from result data (either retrieve_context_result or chat_history_result).
    
    This function processes search results and extracts citation information including
    document URLs, page numbers, and content for proper source attribution.
    
    Handles two different data structures:
    1. retrieve_context_result: Individual results with payload.doc_url, payload.content, etc.
    2. chat_history_result: Stored chat history with payload.citation_map already aggregated
    
    Args:
        results: List of result dictionaries containing payload data
        source_name: String identifying the source (e.g., "retrieve_context_result", "chat_history_result")
        citation_map: Dictionary to store citation metadata keyed by citation number
        doc_page_to_citation: Dictionary mapping (doc_url, page_no) to citation numbers
        source_chunks: List to append formatted citation content
        idx: Current citation index counter
        
    Returns:
        int: Updated citation index counter
        
    Example:
        >>> citation_map = {}
        >>> doc_page_to_citation = {}
        >>> source_chunks = []
        >>> idx = 1
        >>> results = [{"payload": {"doc_url": "...", "content": "...", ...}}]
        >>> new_idx = extract_citations_from_results(results, "test", citation_map, doc_page_to_citation, source_chunks, idx)
    """
    seen = set()
    for result in results:
        if isinstance(result, dict):
            payload = result.get("payload", {})
            
            # Handle chat_history_result structure with aggregated citation_map
            if source_name == "chat_history_result" and "citation_map" in payload:
                # Extract from stored citation_map in chat history
                stored_citation_map = payload.get("citation_map", {})
                stored_response = payload.get("response", "")
                
                logging.debug(f"Processing chat_history_result with {len(stored_citation_map)} stored citations")
                
                # Import existing citations, but renumber them to avoid conflicts
                for old_citation_num, citation_data in stored_citation_map.items():
                    doc_url = citation_data.get("doc_url")
                    page_no = citation_data.get("page_no")
                    solution = citation_data.get("solution")
                    page_image_url = citation_data.get("page_image_url")
                    
                    doc_page_key = (doc_url, page_no)
                    if doc_url and page_no and doc_page_key not in doc_page_to_citation:
                        citation_map[str(idx)] = {
                            "solution": solution,
                            "doc_url": doc_url,
                            "page_no": page_no,
                            "page_image_url": page_image_url
                        }
                        doc_page_to_citation[doc_page_key] = str(idx)
                        
                        # Extract corresponding content from the response using citation numbers
                        import re
                        # Find content that was referenced by this citation in the original response
                        pattern = f"\\[{old_citation_num}\\]"
                        if re.search(pattern, stored_response):
                            # Add a generic reference since we don't have the original content chunks
                            source_chunks.append(f"[{idx}] Referenced in previous response")
                            logging.debug(f"Added citation {idx} from {source_name}: {doc_url}")
                        
                        idx += 1
                        
            else:
                # Handle retrieve_context_result structure with individual payload entries
                doc_url = payload.get("doc_url", None)
                content = payload.get("content", "")
                solution = payload.get("solution", "")
                page_no = payload.get("page_no", None)
                
                # Only assign a new citation number for unique (doc_url, page_no)
                doc_page_key = (doc_url, page_no)
                if doc_url and page_no and doc_page_key not in doc_page_to_citation:
                    # Construct S3 image URL if possible
                    page_image_url = None
                    if doc_url and solution and page_no:
                        doc_name = doc_url.rstrip("/").split("/")[-1]
                        page_image_url = f"https://s3.console.aws.amazon.com/s3/object/zmp-ai-knowledge-store/ingested_docs.cloudzcp.net/{solution}/overview/{doc_name}/{doc_name}_page{page_no}.png"
                    
                    citation_map[str(idx)] = {
                        "solution": solution,
                        "doc_url": doc_url,
                        "page_no": page_no,
                        "page_image_url": page_image_url
                    }
                    doc_page_to_citation[doc_page_key] = str(idx)
                    idx += 1
                    
                # Use (doc_url, page_no, content) as unique key for context
                key = (doc_url, page_no, content)
                if key not in seen and doc_url and page_no:
                    seen.add(key)
                    citation_num = doc_page_to_citation[doc_page_key]
                    source_chunks.append(f"[{citation_num}] {content}")
                    logging.debug(f"Added citation {citation_num} from {source_name}: {doc_url}")
                
    return idx
