"""
Search Chat History Agent for the multi-agent workflow system.

This agent is responsible for searching chat history using MCP
and filtering the results for relevance.
"""

from ..schemas import PlanExecute
from typing import Optional
from ..mcp_client import MCPClient
from ..utils import extract_mcp_results
from .base import update_step_tracking, keep_only_relevant_content


async def search_chat_history_agent(state: PlanExecute, mcp_client: Optional[MCPClient] = None) -> PlanExecute:
    """
    Agent: Search chat history using MCP and return 'chat_history_result' as a unique key.
    Uses MCPClient as an async context manager for robust resource management.
    """
    # Use rewritten query for better semantic search performance (English works better than original language)
    rewritten_query = state.get("rewritten_query") or state.get("query", "")
    print(f"[search_chat_history_agent] Searching chat history with rewritten query: {rewritten_query}")
    payload = {
        "query": rewritten_query, 
        "n_results": 5,
        "user_id": state.get("user_id") or "anonymous"  # Provide string fallback for None
    }
    # Try MCP connection with graceful fallback
    try:
        if mcp_client:
            mcp_result = await mcp_client.call_tool("search_chat_history", payload)
        else:
            async with MCPClient() as client:
                mcp_result = await client.call_tool("search_chat_history", payload)
        results = extract_mcp_results(mcp_result)
        if isinstance(mcp_result, dict) and not mcp_result.get("success", True):
            print(f"[search_chat_history_agent] MCP error: {mcp_result.get('error')}")
            results = []
    except Exception as e:
        print(f"[search_chat_history_agent] MCP connection failed: {str(e)}")
        print("[search_chat_history_agent] Falling back to no chat history context")
        results = []
    
    # Use LLM-based content filtering for relevance (same as retrieve_context_agent)
    filtered_results = []
    
    # Combine all retrieved content for LLM-based filtering
    all_content = []
    all_results = []
    
    for result in results:
        if isinstance(result, dict):
            payload = result.get("payload", {})
            content = payload.get("response", "") or payload.get("content", "")
            
            if content:
                all_content.append(f"Chat History: {content}")
                all_results.append(result)
    
    if all_content:
        # Use LLM-based filtering to determine relevance
        combined_content = "\n\n".join(all_content)
        
        try:
            # Use the LLM-based content filtering
            filter_state = {
                "question": rewritten_query,
                "context": combined_content
            }
            
            filtered_output = keep_only_relevant_content(filter_state)
            relevant_content = filtered_output["relevant_context"]
            
            # Check if the LLM found any relevant content
            if (relevant_content.strip() and 
                relevant_content != "No relevant content found." and
                relevant_content != "NO_RELEVANT_CONTENT_FOUND" and
                "not explicitly mentioned" not in relevant_content.lower()):
                # If LLM found relevant content, include the results
                filtered_results = all_results
                print(f"[search_chat_history_agent] LLM filtering found relevant content for query: {rewritten_query}")
            else:
                print(f"[search_chat_history_agent] LLM filtering found no relevant content for query: {rewritten_query}")
                print(f"[search_chat_history_agent] Relevant content was: {relevant_content}")
                # Don't include any results if no relevant content found
                filtered_results = []
                
        except Exception as e:
            print(f"[search_chat_history_agent] Error in LLM-based filtering: {e}")
            # Fallback to simple filtering if LLM filtering fails
            for result in all_results:
                payload = result.get("payload", {})
                content = payload.get("response", "") or payload.get("content", "")
                
                # Simple relevance check as fallback
                if any(term.lower() in content.lower() for term in rewritten_query.lower().split() if len(term) > 2):
                    filtered_results.append(result)
                    print(f"[search_chat_history_agent] Simple filtering included result for query: {rewritten_query}")
                else:
                    print(f"[search_chat_history_agent] Simple filtering excluded result for query: {rewritten_query}")
    else:
        print(f"[search_chat_history_agent] No chat history content found for query: {rewritten_query}")
    
    # Update state with results and step tracking
    state["chat_history_result"] = filtered_results

    # Populate aggregated_context with RELEVANT chat history for downstream agents
    if filtered_results:
        # Only add responses that are relevant to the current query
        rewritten_query = state.get("query", "")
        relevant_responses = []
        
        for result in filtered_results:
            if isinstance(result, dict) and "payload" in result:
                payload = result["payload"]
                response = payload.get("response", "")
                if response:
                    relevant_responses.append(response)
        
        if relevant_responses:
            # Use LLM to filter only relevant content
            chat_context = "\n\n".join([f"Previous Response: {resp}" for resp in relevant_responses])
            try:
                filter_state = {"question": rewritten_query, "context": chat_context}
                filtered_output = keep_only_relevant_content(filter_state)
                relevant_content = filtered_output["relevant_context"]
                
                if (relevant_content != "NO_RELEVANT_CONTENT_FOUND" and 
                    "not explicitly mentioned" not in relevant_content.lower()):
                    state["aggregated_context"] = relevant_content
                    print("[search_chat_history_agent] Set aggregated_context with relevant chat history")
                else:
                    print("[search_chat_history_agent] No relevant chat history content for query")
            except Exception as e:
                print(f"[search_chat_history_agent] Error filtering relevant content: {e}")

    update_step_tracking(state, "search_chat_history")
    
    return state
