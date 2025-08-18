"""
Get Final Answer Agent for the multi-agent workflow system.

This agent is responsible for synthesizing comprehensive final answers from all available information.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional
from ..mcp_client import MCPClient
from ..utils import get_llm, extract_citations_from_results
from .base import update_step_tracking


class FinalAnswerSynthesis(BaseModel):
    final_answer: str = Field(description="The comprehensive final answer synthesized from all available information.")
    summary: str = Field(description="A brief summary of the answer generation process.")
    quality_score: float = Field(description="Overall quality score for the final answer (0.0 to 1.0).")


final_answer_prompt = PromptTemplate(
    template="""
You are an expert assistant that provides comprehensive answers based on available information.

Original User Query: {original_query}
Rewritten Query (for understanding intent): {rewritten_query}
Has Relevant Data: {has_relevant_data}

Chat History:
{chat_history_context}

Retrieved Context:
{context}

Previous Generated Answer: {answer}
Answer Confidence: {confidence}
Sources Used: {sources}
Past Steps: {past_steps}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the original user query
- Analyze the original user query language and respond in that same language
- Use the rewritten query to understand the intent and provide relevant information
- Do NOT translate or change the language from the original query
- Do NOT respond in any other language
- This is a strict requirement - you must follow the original query's language exactly

CHAT HISTORY CONTEXT:
- Use the chat history to understand the conversation context and resolve references like "this", "that", "it"
- If the current query refers to something from previous conversation, use that context to provide accurate answers
- Pay attention to entity references and topic continuity from the chat history
- If the chat history contains relevant information that helps answer the current query, incorporate it appropriately

SCENARIO-BASED INSTRUCTIONS:

**SCENARIO 1: No Relevant Data Available**
If has_relevant_data is "false" or context is "No relevant context found." or similar:
- Provide a polite response indicating no information is available about the topic
- Suggest trying a different topic or rephrasing the question
- Keep the response concise but informative
- Example: "I don't have any information about this topic in my knowledge base. Please try asking about a different topic or rephrase your question."
- Set quality_score to 0.0
- Provide a brief summary indicating no relevant data was found

**SCENARIO 2: Relevant Data Available with Citations**
If has_relevant_data is "true" and context contains relevant information:
- Provide a comprehensive answer using the provided sources
- Use inline citations with numbers in square brackets [1], [2], etc. to reference specific sources
- Only cite sources that you actually use in your answer
- If multiple sources support the same point, cite all relevant sources together like [1], [3]
- Place citations immediately after the relevant information
- There must be a source citation at the end of every paragraph
- Do not add any paragraph without at least one source at the end
- Do NOT list sources at the end of your answer
- Set quality_score based on how comprehensive and accurate the answer is (0.5 to 1.0)
- Provide a brief summary of what information was found and used

**SCENARIO 3: Context Contains Different Topic**
If the context contains information about a different topic than what was asked (e.g., ZCP content when asked about APIM):
- Respond with: "I don't have any information about this topic in my knowledge base. Please try asking about a different topic or rephrase your question."
- Set quality_score to 0.0
- Provide a brief summary indicating irrelevant data was found

IMPORTANT: Base your answer primarily on the retrieved context, not on the previous generated answer.
Respond in the user's language only.
""",
    input_variables=["original_query", "rewritten_query", "answer", "confidence", "sources", "context", "past_steps", "has_relevant_data", "chat_history_context"],
)

final_answer_llm = get_llm()
final_answer_chain = final_answer_prompt | final_answer_llm.with_structured_output(FinalAnswerSynthesis)


async def get_final_answer_agent(state: PlanExecute, mcp_client: Optional[MCPClient] = None) -> PlanExecute:
    """
    Enhanced Agent: Synthesize comprehensive final answer from all available information.
    Args:
        state: The shared workflow state containing all generated information.
        mcp_client: Optional MCP client for logging.
    Returns:
        Updated PlanExecute with comprehensive final answer and metadata.
    """
    # Use original query for language detection in final answer
    original_query = state.get("query", "")
    rewritten_query = state.get("rewritten_query", original_query)
    print(f"[get_final_answer_agent] Original query: {original_query}")
    print(f"[get_final_answer_agent] Rewritten query: {rewritten_query}")
    answer = state.get("answer", "No answer generated.")
    confidence = state.get("answer_confidence", 0.0)
    sources = state.get("sources", [])
    past_steps = state.get("past_steps", [])
    
    # --- Begin citation-style context formatting ---
    # Gather unique (doc_url, page_no) and build citation_map
    doc_page_to_citation = {}
    citation_map = {}
    source_chunks = []
    idx = 1
    
    # Add current context from task handler (highest priority, no citations)
    current_context = state.get("current_context", "")
    if current_context and current_context.strip():
        source_chunks.append(f"Available Context: {current_context}")
        print(f"[get_final_answer_agent] Using current_context: {current_context[:100]}...")
    
    # Extract citations from retrieve_context_result (fresh knowledge base searches)
    if state.get("retrieve_context_result"):
        idx = extract_citations_from_results(
            state["retrieve_context_result"], 
            "retrieve_context_result", 
            citation_map, 
            doc_page_to_citation, 
            source_chunks, 
            idx
        )
    
    # Extract citations from chat_history_result (follow-up questions)
    if state.get("chat_history_result"):
        idx = extract_citations_from_results(
            state["chat_history_result"], 
            "chat_history_result", 
            citation_map, 
            doc_page_to_citation, 
            source_chunks, 
            idx
        )
    formatted_context = "\n".join(source_chunks) if source_chunks else "No relevant context found."
    # Note: citation_map and doc_urls will be set after final answer generation with proper filtering
    # --- End citation-style context formatting ---

    # Determine if we have relevant data (include current_context)
    has_relevant_data = "true" if (formatted_context != "No relevant context found." or 
                                  (current_context and current_context.strip())) else "false"
    
    # Format chat history from search results for LLM context
    chat_history_result = state.get("chat_history_result", [])
    if chat_history_result:
        chat_history_lines = []
        for result in chat_history_result:
            if isinstance(result, dict) and "payload" in result:
                payload = result["payload"]
                query = payload.get("query", "")
                response = payload.get("response", "")
                if query and response:
                    chat_history_lines.append(f"User: {query}")
                    chat_history_lines.append(f"Assistant: {response}")
        chat_history_context = "\n".join(chat_history_lines)
        print(f"[get_final_answer_agent] Formatted chat history context from search results with {len(chat_history_lines)} messages")
    else:
        chat_history_context = "No previous conversation history."
    
    # Use the final_answer_chain to generate the answer
    try:
        print(f"[get_final_answer_agent] Has relevant data: {has_relevant_data}")
        print(f"[get_final_answer_agent] Context: {formatted_context[:100]}...")
        print(f"[get_final_answer_agent] Chat history results: {len(chat_history_result)} items")
        
        response = await final_answer_chain.ainvoke({
            "original_query": original_query,
            "rewritten_query": rewritten_query,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
            "context": formatted_context,
            "past_steps": past_steps,
            "has_relevant_data": has_relevant_data,
            "chat_history_context": chat_history_context
        })
        
        print(f"[get_final_answer_agent] LLM response: {response}")
        
        # Handle structured response from FinalAnswerSynthesis
        state["final_answer"] = response.final_answer
        state["answer_summary"] = response.summary
        state["answer_quality_score"] = response.quality_score
        
        # If answer_confidence wasn't set by answer_agent, use quality_score as fallback
        if not state.get("answer_confidence"):
            state["answer_confidence"] = response.quality_score
        
        # Filter citation_map to only include citations actually used in the final answer
        import re
        used_citations = set(re.findall(r'\[(\d+)\]', state["final_answer"]))
        if used_citations:
            # Only include citations that are actually referenced in the answer
            filtered_citation_map = {k: v for k, v in citation_map.items() if k in used_citations}
            print(f"[get_final_answer_agent] Filtered citation_map to {len(filtered_citation_map)} used citations from {len(citation_map)} total")
            print(f"[get_final_answer_agent] Used citations: {sorted(used_citations)}")
        else:
            # If no citation markers found, preserve all citations since content was still sourced from them
            filtered_citation_map = citation_map
            print(f"[get_final_answer_agent] No citation markers found, preserving all {len(citation_map)} citations")
        
        # Set the filtered citation map and corresponding doc_urls in state
        state["citation_map"] = filtered_citation_map
        state["doc_urls"] = list({meta["doc_url"] for meta in filtered_citation_map.values()})
        
        print(f"[get_final_answer_agent] Final result: {len(state['doc_urls'])} doc_urls, {len(state['citation_map'])} citations")
        
    except Exception as e:
        print(f"[get_final_answer_agent] Error in final answer generation: {e}")
        # Set error state
        state["final_answer"] = "An error occurred while generating the answer. Please try again."
        state["answer_summary"] = "Error in answer generation"
        state["answer_quality_score"] = 0.0
        # In case of error, preserve all citations
        state["citation_map"] = citation_map
        state["doc_urls"] = list({meta["doc_url"] for meta in citation_map.values()})
    
    update_step_tracking(state, "get_final_answer")
    
    # Preserve session dialogue by appending current query-answer pair as LangGraph messages
    final_answer = state.get("final_answer", "")
    
    if final_answer and final_answer.strip():
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Manually accumulate session_dialogue (no longer using operator.add)
        existing_dialogue = state.get("session_dialogue", [])
        
        # Create structured AI response content with all metadata
        structured_ai_content = {
            "answer": final_answer,
            "summary": state.get("answer_summary", ""),
            "quality_score": state.get("answer_quality_score", 0.0),
            "doc_urls": state.get("doc_urls", []),
            "citation_map": state.get("citation_map", {})
        }
        
        # Create LangGraph messages for the current conversation pair  
        # Store structured content as list containing dictionary (LangChain format)
        new_messages = [
            HumanMessage(content=rewritten_query),
            AIMessage(content=[structured_ai_content])
        ]
        
        # Manually append to existing dialogue
        updated_session_dialogue = existing_dialogue + new_messages
        
        print(f"[get_final_answer_agent] Adding query-answer pair to session dialogue (total: {len(updated_session_dialogue)} messages)")
        
        # Return updated state with manually accumulated session_dialogue
        return {
            **state, 
            "doc_urls": state.get("doc_urls", []), 
            "citation_map": state.get("citation_map", {}),
            "session_dialogue": updated_session_dialogue
        }
    else:
        # No meaningful answer to preserve
        return {
            **state, 
            "doc_urls": state.get("doc_urls", []), 
            "citation_map": state.get("citation_map", {})
        }
