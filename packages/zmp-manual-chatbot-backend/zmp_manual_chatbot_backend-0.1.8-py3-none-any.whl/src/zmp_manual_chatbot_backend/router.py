import asyncio
import logging
import traceback
from fastapi import APIRouter, Request, Query, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
import json
import uuid
from typing import List, Optional
from .service import ChatbotService
from .session import SessionManager
from .schemas import Message, ChatRequest, ThreadsListResponse, ThreadConversationResponse, ThreadInfo, ChatRecord
from .config import settings
from .utils import extract_user_id_from_token, extract_user_name_from_token
# Note: Authentication is handled by zmp_authentication_provider package

router = APIRouter()

async def get_token(request: Request):
    """
    Extract and validate the token from the Authorization header.
    
    Args:
        request: FastAPI request object
        
    Returns:
        The extracted JWT token string
        
    Raises:
        HTTPException: If token is missing or invalid format
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split("Bearer ")[1]

    # Do a basic token validation to ensure it's a proper JWT
    parts = token.split(".")
    if len(parts) != 3:
        logging.error(
            f"Invalid token format: token has {len(parts)} segments, expected 3"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


async def response_generator(chat_history: List[Message], question: str, thread_id: str, session_manager: SessionManager, chatbot_service: ChatbotService, image_url: Optional[str] = None, user_id: Optional[str] = None, user_name: Optional[str] = None, client_thread_id: Optional[str] = None):
    """
    Generate streaming response with proper session management.
    """
    try:
        # Track what content has already been streamed to prevent duplicates
        streamed_content = {
            "final_answer": None,
            "plan": None,
            "metadata": None
        }
        
        # Track thread_id across all workflow events
        current_thread_id = None
        
        # Retrieve or create session resources
        session_queue, queue_lock, session_task = await session_manager.get_or_create_session(thread_id)
        
        # Add cleanup task if this is a new session (we'll use background_tasks from global state if available)
        if session_task is None:
            try:
                # Try to add cleanup task if background_tasks is available
                asyncio.create_task(cleanup_session_delayed(thread_id, session_manager))
            except Exception:
                # Ignore if background task creation fails
                pass
                
        async with queue_lock:
            logging.info(f"Acquired lock for session {thread_id}")

            if session_task is None or session_task.done():
                # Start new workflow execution
                logging.info(f"Starting new workflow for session {thread_id}")
                
                # Define and start the streaming task
                async def stream_workflow_inner():
                    try:
                        # Run the workflow with the chatbot service
                        async for event in chatbot_service.run_workflow({
                            "query": question, 
                            "session_id": thread_id,
                            "chat_history": chat_history,
                            "image_url": image_url,
                            "user_id": user_id,
                            "user_name": user_name,
                            "thread_id": client_thread_id  # Pass client_thread_id to workflow
                        }):
                            logging.debug(f"Received event: {event}")
                            await session_queue.put(event)
                        await session_queue.put(None)  # Sentinel value to signal end of stream
                    except Exception as e:
                        logging.error(f"Error in workflow streaming: {e}")
                        logging.error(traceback.format_exc())
                        await session_queue.put({"error": str(e)})
                        await session_queue.put(None)  # Ensure streaming ends

                # Create and store the streaming task
                new_task = asyncio.create_task(stream_workflow_inner())
                await session_manager.set_session_task(thread_id, new_task)

                logging.info(f"Started generation task for session {thread_id}")

            else:
                logging.info(f"Task for session {thread_id} is already running.")
                
        # Streaming loop: yield data as it becomes available
        while True:
            try:
                # Wait for the next item with a timeout to prevent hanging
                value = await asyncio.wait_for(session_queue.get(), timeout=180.0)
                logging.info(f"Received value from queue: {value}")

                if value is None:
                    logging.info(f"Received stop signal for session {thread_id}")
                    break

                # Convert dict to JSON string if it's a dictionary
                if isinstance(value, dict):
                    # Handle different streaming modes based on content
                    final_answer = value.get("final_answer")
                    plan = value.get("plan")
                    doc_urls = value.get("doc_urls")
                    citation_map = value.get("citation_map")
                    workflow_thread_id = value.get("thread_id")  # Get thread_id from workflow
                    
                    # Track thread_id from any workflow event that has it
                    if workflow_thread_id:
                        current_thread_id = workflow_thread_id
                    
                    # If we have a final_answer, stream it only if it's different from what we've already streamed
                    if final_answer and final_answer != "None" and final_answer != streamed_content["final_answer"]:
                        logging.info(f"Streaming new final_answer for session {thread_id}")
                        
                        # First, send plan if available and not already sent
                        if plan and plan != streamed_content["plan"]:
                            event_data = {"type": "plan", "data": plan}
                            yield f"data: {json.dumps(event_data, default=str, ensure_ascii=False)}\n\n"
                            streamed_content["plan"] = plan
                        
                        # Stream final_answer character by character (if enabled)
                        if settings.ENABLE_CHAR_STREAMING:
                            for i in range(0, len(final_answer), settings.STREAMING_CHUNK_SIZE):
                                chunk = final_answer[i:i + settings.STREAMING_CHUNK_SIZE]
                                char_event = {"type": "answer_chunk", "data": chunk}
                                yield f"data: {json.dumps(char_event, default=str, ensure_ascii=False)}\n\n"
                                if settings.CHAR_STREAMING_DELAY > 0:
                                    await asyncio.sleep(settings.CHAR_STREAMING_DELAY)
                        else:
                            # Send complete final_answer at once
                            answer_event = {"type": "final_answer", "data": final_answer}
                            yield f"data: {json.dumps(answer_event, default=str, ensure_ascii=False)}\n\n"
                        
                        # Mark final_answer as streamed
                        streamed_content["final_answer"] = final_answer
                        
                        # Send metadata at the end only once
                        if (doc_urls is not None or citation_map is not None or current_thread_id is not None) and streamed_content["metadata"] is None:
                            # Ensure we have thread_id - get from session state if not available
                            final_thread_id = current_thread_id
                            if not final_thread_id:
                                try:
                                    from .utils import get_plan_execute
                                    session_state = await get_plan_execute(thread_id)
                                    if session_state and session_state.get("thread_id"):
                                        final_thread_id = session_state.get("thread_id")
                                        logging.info(f"Retrieved thread_id from session state for metadata: {final_thread_id}")
                                except Exception as e:
                                    logging.error(f"Error retrieving thread_id from session state for metadata: {e}")
                            
                            metadata_event = {
                                "type": "metadata", 
                                "data": {
                                    "doc_urls": doc_urls,
                                    "citation_map": citation_map,
                                    "thread_id": final_thread_id  # Include thread_id in response for client
                                }
                            }
                            yield f"data: {json.dumps(metadata_event, default=str, ensure_ascii=False)}\n\n"
                            streamed_content["metadata"] = {"doc_urls": doc_urls, "citation_map": citation_map, "thread_id": final_thread_id}
                            logging.info(f"Sent consolidated metadata with thread_id: {final_thread_id}")
                    
                    # For intermediate updates (no final_answer yet), send as progress only if plan changed
                    elif plan and plan != streamed_content["plan"] and not final_answer:
                        event_data = {"type": "progress", "data": {"plan": plan}}
                        yield f"data: {json.dumps(event_data, default=str, ensure_ascii=False)}\n\n"
                        # Mark plan as streamed to prevent duplicates
                        streamed_content["plan"] = plan
                else:
                    # If it's already a string, yield it directly
                    yield str(value)

                # Mark the task as done
                session_queue.task_done()

            except asyncio.TimeoutError:
                logging.error(f"Timeout while waiting for queue item in session {thread_id}")
                yield "Error: Timeout while generating response.\n"
                break
            except Exception as e:
                logging.error(f"Unexpected error while retrieving from queue: {e}")
                yield "Error: Unexpected error while generating response.\n"
                break

        # Only send fallback metadata if no metadata was sent at all during the workflow
        if streamed_content["metadata"] is None:
            # If we don't have thread_id from workflow events, try to get it from session state
            if not current_thread_id:
                try:
                    from .utils import get_plan_execute
                    session_state = await get_plan_execute(thread_id)
                    if session_state and session_state.get("thread_id"):
                        current_thread_id = session_state.get("thread_id")
                        logging.info(f"Retrieved thread_id from session state for fallback: {current_thread_id}")
                except Exception as e:
                    logging.error(f"Error retrieving thread_id from session state for fallback: {e}")
            
            if current_thread_id:
                metadata_event = {
                    "type": "metadata", 
                    "data": {
                        "doc_urls": None,
                        "citation_map": None,
                        "thread_id": current_thread_id
                    }
                }
                yield f"data: {json.dumps(metadata_event, default=str, ensure_ascii=False)}\n\n"
                logging.info(f"Sent fallback thread_id metadata (no metadata was sent during workflow): {current_thread_id}")
            else:
                logging.warning(f"No thread_id available for fallback metadata in session {thread_id}")

        logging.info(f"Final result for session {thread_id}")        
    except Exception as e:
        logging.error(f"An unexpected error occurred for session {thread_id}: {e}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        logging.info(f"Releasing lock for session {thread_id}")

async def cleanup_session(thread_id: str, session_manager: SessionManager):
    """
    Background task to cleanup session after timeout.
    """
    await asyncio.sleep(3600)  # Wait for 1 hour
    await session_manager.delete_session(thread_id)
    logging.info(f"Cleaned up session queue for thread_id: {thread_id}")

async def cleanup_session_delayed(thread_id: str, session_manager: SessionManager):
    """
    Delayed cleanup task for sessions without background task support.
    """
    await asyncio.sleep(3600)  # Wait for 1 hour
    await session_manager.delete_session(thread_id)
    logging.info(f"Cleaned up session queue for thread_id: {thread_id}")

@router.post("/chat/query")
async def chat_query(
    chat_request: ChatRequest, 
    request: Request, 
    background_tasks: BackgroundTasks = None
):
    """
    Chat query endpoint with intelligent session management.
    
    **AUTHENTICATION**: This endpoint requires OAuth2 authentication.
    
    **SESSION MANAGEMENT**:
    - For new conversations: Server automatically generates UUID-based session ID
    - For follow-up questions: Send existing session ID in 'X-Session-ID' request header
    - Server will reuse existing session file or create new one as needed
    
    Note: Authentication is implemented using zmp_authentication_provider package.
    Token validation is performed manually via get_token() helper function.
    
    Args:
        chat_request: Chat request data (question, chat_history, image_url)
        request: FastAPI request object (may contain X-Session-ID header)
        background_tasks: FastAPI background tasks
        
    Returns:
        Streaming response with chat results and session_id in response headers
        
    Raises:
        HTTPException: If authentication fails or other errors occur
    """
    try:
        # Simple token validation
        token = await get_token(request)
        logging.info(f"Authenticated request with token (last 10 chars): ...{token[-10:] if len(token) > 10 else token}")
        
        # Extract user ID from JWT token
        try:
            user_id = extract_user_id_from_token(token)
            logging.info(f"Extracted user_id from JWT token: {user_id}")
            if user_id is None:
                logging.warning("extract_user_id_from_token returned None - check token structure")
        except Exception as e:
            logging.error(f"Error extracting user_id from token: {e}")
            user_id = None
            
        # Extract user name from JWT token
        try:
            user_name = extract_user_name_from_token(token)
            logging.info(f"Extracted user_name from JWT token: {user_name}")
            if user_name is None:
                logging.warning("extract_user_name_from_token returned None - check token structure")
        except Exception as e:
            logging.error(f"Error extracting user_name from token: {e}")
            user_name = None
        
        # Get session manager from app state
        session_manager: SessionManager = request.app.state.session_manager
        chatbot_service: ChatbotService = request.app.state.chatbot_service
        
        # Check for existing session ID in request headers, or generate new UUID
        existing_session_id = request.headers.get("X-Session-ID")
        if existing_session_id and existing_session_id.startswith("session_"):
            session_id = existing_session_id
            logging.info(f"Using existing session ID from request header: {session_id}")
        else:
            session_id = f"session_{str(uuid.uuid4())}"
            logging.info(f"Generated new session ID for authenticated request: {session_id}")
        
        # Session management is handled in response_generator

        question = chat_request.question
        chat_history = chat_request.chat_history
        image_url = chat_request.image_url
        client_thread_id = chat_request.thread_id  # Extract thread_id from client request
        
        # Log query details
        logging.info(f"Authenticated user query: {question}")
        logging.info(f"Chat History: {chat_history}")
        logging.info(f"Image URL: {image_url}")
        logging.info(f"Client thread_id: {client_thread_id}")

        # Start the response generation process
        return StreamingResponse(
            response_generator(chat_history, question, session_id, session_manager, chatbot_service, image_url, user_id, user_name, client_thread_id),
            media_type='text/event-stream',
            headers={'X-Session-ID': session_id}
        )

    except Exception as e:
        # Log the error and return an HTTP error response
        logging.exception("Error processing chat interaction:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    
    Returns:
        JSON response indicating the service health status
    """
    return {
        "status": "healthy",
        "service": "zmp-manual-chatbot-backend",
        "version": "0.1.4"
    }

@router.get("/threads", response_model=ThreadsListResponse)
async def list_user_threads(request: Request):
    """
    List all conversation threads for the authenticated user.
    
    **AUTHENTICATION**: This endpoint requires OAuth2 authentication.
    
    Returns:
        ThreadsListResponse with user_id and list of threads with thread_id and thread_title
        
    Raises:
        HTTPException: If authentication fails or MCP server errors occur
    """
    try:
        # Simple token validation
        token = await get_token(request)
        logging.info(f"Authenticated threads list request with token (last 10 chars): ...{token[-10:] if len(token) > 10 else token}")
        
        # Extract user ID from JWT token
        user_id = extract_user_id_from_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unable to extract user_id from token")
        
        # Get chatbot service from app state
        chatbot_service: ChatbotService = request.app.state.chatbot_service
        
        # Call MCP server to list threads
        async with chatbot_service.mcp_client as mcp_client:
            mcp_result = await mcp_client.list_threads(user_id)
            
        # Extract structured content from MCP result
        # For list_threads, we need to extract data differently than search results
        if hasattr(mcp_result, 'structured_content') and mcp_result.structured_content:
            mcp_data = mcp_result.structured_content
        elif hasattr(mcp_result, 'content') and mcp_result.content:
            # Handle CallToolResult with content list containing TextContent
            content_list = mcp_result.content
            if isinstance(content_list, list) and content_list:
                text_content = content_list[0]
                if hasattr(text_content, "text"):
                    try:
                        mcp_data = json.loads(text_content.text)
                    except Exception as e:
                        logging.error(f"Error parsing MCP result text: {e}")
                        mcp_data = {}
                else:
                    mcp_data = {}
            else:
                mcp_data = {}
        else:
            mcp_data = {}
        
        # Handle both direct dict and nested dict formats
        if isinstance(mcp_data, dict):
            # Direct format from MCP
            threads_data = mcp_data.get("threads", [])
            result_user_id = mcp_data.get("user_id", user_id)
        elif isinstance(mcp_data, list) and mcp_data:
            # Nested format - get first item
            first_item = mcp_data[0]
            threads_data = first_item.get("threads", [])
            result_user_id = first_item.get("user_id", user_id)
        else:
            # Empty or unknown format
            threads_data = []
            result_user_id = user_id
        
        # Convert to response format
        threads = [
            ThreadInfo(thread_id=thread["thread_id"], thread_title=thread["thread_title"])
            for thread in threads_data
        ]
        
        return ThreadsListResponse(user_id=result_user_id, threads=threads)
        
    except Exception as e:
        logging.exception("Error listing user threads:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threads/{thread_id}", response_model=ThreadConversationResponse)
async def get_thread_conversation(thread_id: str, request: Request):
    """
    Get conversation history for a specific thread.
    
    **AUTHENTICATION**: This endpoint requires OAuth2 authentication.
    
    Args:
        thread_id: The thread ID to retrieve conversation for
        
    Returns:
        ThreadConversationResponse with user_id, thread_id, and records array (newest first)
        
    Raises:
        HTTPException: If authentication fails, thread not found, or MCP server errors occur
    """
    try:
        # Simple token validation
        token = await get_token(request)
        logging.info(f"Authenticated thread get request for thread {thread_id} with token (last 10 chars): ...{token[-10:] if len(token) > 10 else token}")
        
        # Extract user ID from JWT token
        user_id = extract_user_id_from_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unable to extract user_id from token")
        
        # Get chatbot service from app state
        chatbot_service: ChatbotService = request.app.state.chatbot_service
        
        # Call MCP server to get thread conversation
        async with chatbot_service.mcp_client as mcp_client:
            mcp_result = await mcp_client.get_thread(user_id, thread_id)
            
        # Extract structured content from MCP result
        # For get_thread, we need to extract data differently than search results
        if hasattr(mcp_result, 'structured_content') and mcp_result.structured_content:
            mcp_data = mcp_result.structured_content
        elif hasattr(mcp_result, 'content') and mcp_result.content:
            # Handle CallToolResult with content list containing TextContent
            content_list = mcp_result.content
            if isinstance(content_list, list) and content_list:
                text_content = content_list[0]
                if hasattr(text_content, "text"):
                    try:
                        mcp_data = json.loads(text_content.text)
                    except Exception as e:
                        logging.error(f"Error parsing MCP result text: {e}")
                        mcp_data = {}
                else:
                    mcp_data = {}
            else:
                mcp_data = {}
        else:
            mcp_data = {}
        
        # Handle both direct dict and nested dict formats
        if isinstance(mcp_data, dict):
            # Direct format from MCP
            records_data = mcp_data.get("records", [])
            result_user_id = mcp_data.get("user_id", user_id)
            result_thread_id = mcp_data.get("thread_id", thread_id)
        elif isinstance(mcp_data, list) and mcp_data:
            # Nested format - get first item
            first_item = mcp_data[0]
            records_data = first_item.get("records", [])
            result_user_id = first_item.get("user_id", user_id)
            result_thread_id = first_item.get("thread_id", thread_id)
        else:
            # Empty or unknown format
            records_data = []
            result_user_id = user_id
            result_thread_id = thread_id
        
        # Convert to response format with robust field extraction
        records = []
        for record in records_data:
            try:
                # Handle different possible record structures
                chat_record = ChatRecord(
                    user_id=record.get("user_id", user_id),  # Fallback to extracted user_id
                    thread_id=record.get("thread_id", thread_id),  # Fallback to request thread_id
                    query=record.get("query", ""),
                    response=record.get("response", ""),
                    doc_urls=record.get("doc_urls", []),
                    citation_map=record.get("citation_map", {}),
                    timestamp=record.get("timestamp", "")
                )
                records.append(chat_record)
            except Exception as e:
                logging.error(f"Error processing chat record: {record}, error: {e}")
                # Skip malformed records but continue processing others
                continue
        
        return ThreadConversationResponse(
            user_id=result_user_id,
            thread_id=result_thread_id,
            records=records
        )
        
    except Exception as e:
        logging.exception(f"Error getting thread conversation for {thread_id}:", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
