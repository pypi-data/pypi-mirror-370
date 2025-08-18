"""
Retrieve Context Agent for the multi-agent workflow system.

This agent is responsible for retrieving context from the knowledge base
using MCP and filtering the results for relevance.
"""

from ..schemas import PlanExecute
from typing import Optional
from ..mcp_client import MCPClient
from ..utils import extract_mcp_results
from .base import update_step_tracking, keep_only_relevant_content


async def retrieve_context_agent(state: PlanExecute, mcp_client: Optional[MCPClient] = None) -> PlanExecute:
    """
    Agent: Retrieve context using MCP and return 'retrieve_context_result' as a unique key.
    Uses MCPClient as an async context manager for robust resource management.
    """
    query = state.get("rewritten_query", state["query"])
    rewritten_query = state.get("query", query)
    
    if mcp_client:
        mcp_result = await mcp_client.call_tool("search_knowledge", {"query": query})
    else:
        async with MCPClient() as client:
            mcp_result = await client.call_tool("search_knowledge", {"query": query})
    
    # Use updated extract_mcp_results for new MCP server
    results = extract_mcp_results(mcp_result)
    
    # Optionally, check for errors
    if isinstance(mcp_result, dict) and not mcp_result.get("success", True):
        print(f"[retrieve_context_agent] MCP error: {mcp_result.get('error')}")
        results = []
    
    # Use LLM-based content filtering for relevance
    filtered_results = []
    doc_urls = []
    
    # Combine all retrieved content for LLM-based filtering
    all_content = []
    all_results = []
    
    for result in results:
        if isinstance(result, dict):
            payload = result.get("payload", {})
            content = payload.get("content", "")
            doc_url = payload.get("doc_url")
            
            if content and doc_url:
                all_content.append(f"Source: {doc_url}\nContent: {content}")
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
                doc_urls = [result.get("payload", {}).get("doc_url") for result in all_results if result.get("payload", {}).get("doc_url")]
                print(f"[retrieve_context_agent] LLM filtering found relevant content for query: {rewritten_query}")
            else:
                print(f"[retrieve_context_agent] LLM filtering found no relevant content for query: {rewritten_query}")
                print(f"[retrieve_context_agent] Relevant content was: {relevant_content}")
                # Don't include any results if no relevant content found
                filtered_results = []
                doc_urls = []
                
        except Exception as e:
            print(f"[retrieve_context_agent] Error in LLM-based filtering: {e}")
            # Fallback to simple filtering if LLM filtering fails
            for result in all_results:
                payload = result.get("payload", {})
                content = payload.get("content", "")
                doc_url = payload.get("doc_url")
                
                # Simple relevance check as fallback
                if any(term.lower() in content.lower() for term in rewritten_query.lower().split() if len(term) > 2):
                    filtered_results.append(result)
                    if doc_url:
                        doc_urls.append(doc_url)
    else:
        print("[retrieve_context_agent] No content found in retrieved results")
    
    # Store doc_urls in state for downstream use
    state["doc_urls"] = doc_urls
    
    # Debug logging
    print(f"[retrieve_context_agent] Original query: {rewritten_query}")
    print(f"[retrieve_context_agent] Rewritten query: {query}")
    print(f"[retrieve_context_agent] Total results: {len(results)}")
    print(f"[retrieve_context_agent] Filtered results: {len(filtered_results)}")
    print(f"[retrieve_context_agent] Doc URLs: {doc_urls}")
    
    # Update state with results and step tracking
    state["retrieve_context_result"] = filtered_results
    state["doc_urls"] = doc_urls

    # Populate aggregated_context with RELEVANT knowledge base content for downstream agents
    if filtered_results:
        rewritten_query = state.get("query", "")
        kb_content_parts = []
        
        for result in filtered_results:
            if isinstance(result, dict) and "payload" in result:
                payload = result["payload"]
                content = payload.get("content", "")
                if content:
                    kb_content_parts.append(content)
        
        if kb_content_parts:
            # Use LLM to filter only relevant content
            kb_context = "\n\n".join([f"Knowledge Base: {content}" for content in kb_content_parts])
            try:
                filter_state = {"question": rewritten_query, "context": kb_context}
                filtered_output = keep_only_relevant_content(filter_state)
                relevant_content = filtered_output["relevant_context"]
                
                if (relevant_content != "NO_RELEVANT_CONTENT_FOUND" and 
                    "not explicitly mentioned" not in relevant_content.lower()):
                    # Only replace/set aggregated_context to prevent exponential growth in loops
                    # Check if we already have the same content to avoid duplication
                    existing_context = state.get("aggregated_context", "")
                    if existing_context and relevant_content in existing_context:
                        print("[retrieve_context_agent] Relevant content already exists in aggregated_context, skipping duplication")
                    else:
                        # Replace instead of append to prevent infinite context growth in replan loops
                        state["aggregated_context"] = relevant_content
                        print("[retrieve_context_agent] Added relevant knowledge base content to aggregated_context")
                else:
                    print("[retrieve_context_agent] No relevant knowledge base content for query")
            except Exception as e:
                print(f"[retrieve_context_agent] Error filtering relevant content: {e}")

    update_step_tracking(state, "retrieve_context")
    
    return state
