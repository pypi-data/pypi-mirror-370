"""
Answer Agent for the multi-agent workflow system.

This agent is responsible for generating comprehensive answers using retrieved context.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from ..utils import get_llm
from .base import update_step_tracking


class AnswerGeneration(BaseModel):
    answer: str = Field(description="The generated answer based on the retrieved context and user query.")
    confidence: float = Field(description="Confidence score for the generated answer (0.0 to 1.0).")
    sources: List[str] = Field(description="List of source documents used to generate the answer.")


answer_generation_prompt = PromptTemplate(
    template="""
You are an expert assistant that generates accurate and helpful answers based on retrieved context.

User Query: {query}

Retrieved Context:
{context}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

Instructions:
1. Generate a comprehensive answer based on the retrieved context
2. Use only information from the provided context - do not add external knowledge
3. Respond in the SAME LANGUAGE as the user's query
4. If the context doesn't contain enough information to answer the query, clearly state this
5. Cite specific parts of the context when relevant
6. Provide a confidence score (0.0 to 1.0) for your answer
7. List the specific sources/documents you used from the context

Generate your answer in a clear, structured format in the user's language.
""",
    input_variables=["query", "context"],
)

answer_generation_llm = get_llm()
answer_generation_chain = answer_generation_prompt | answer_generation_llm.with_structured_output(AnswerGeneration)


async def answer_agent(state: PlanExecute) -> PlanExecute:
    """
    Enhanced Agent: Generate comprehensive answer using retrieved context.
    
    Args:
        state: The shared workflow state containing retrieved context.
    
    Returns:
        Updated PlanExecute with generated answer, confidence, and sources.
    """
    query = state.get("rewritten_query", state.get("query", ""))
    
    # Extract and combine context from all available sources
    context_parts = []
    
    # Add current context from task handler (highest priority)
    current_context = state.get("current_context", "")
    if current_context and current_context.strip():
        context_parts.append(f"Available Context: {current_context}")
        print(f"[answer_agent] Using current_context: {current_context[:100]}...")
    
    # Add knowledge base results
    if state.get("retrieve_context_result"):
        for result in state["retrieve_context_result"]:
            if isinstance(result, dict):
                if "payload" in result and "content" in result["payload"]:
                    context_parts.append(f"Source: {result['payload'].get('doc_url', 'Unknown')}\nContent: {result['payload']['content']}")
                elif "content" in result:
                    context_parts.append(f"Content: {result['content']}")
    
    # Add chat history results
    if state.get("chat_history_result"):
        for result in state["chat_history_result"]:
            if isinstance(result, dict):
                if "payload" in result and "response" in result["payload"]:
                    context_parts.append(f"Previous Response: {result['payload']['response']}")
                elif "content" in result:
                    context_parts.append(f"Chat History: {result['content']}")
    
    # Combine all context
    combined_context = "\n\n".join(context_parts) if context_parts else "No relevant context found."
    
    try:
        # Generate answer using LLM
        result = await answer_generation_chain.ainvoke({
            "query": query,
            "context": combined_context
        })
        state["answer"] = result.answer
        state["answer_confidence"] = result.confidence
        # If LLM did not return sources, extract from retrieve_context_result
        sources = result.sources if result.sources else []
        if not sources and state.get("retrieve_context_result"):
            seen = set()
            for r in state["retrieve_context_result"]:
                if isinstance(r, dict):
                    payload = r.get("payload", {})
                    doc_url = payload.get("doc_url")
                    if doc_url and doc_url not in seen:
                        sources.append(doc_url)
                        seen.add(doc_url)
        state["sources"] = sources
        
    except Exception as e:
        print(f"Error in answer generation: {e}")
        # Fallback to a basic answer
        state["answer"] = f"Based on the available information: {combined_context[:200]}..."
        state["answer_confidence"] = 0.5
        state["sources"] = []
    
    update_step_tracking(state, "answer")
    # After answer generation, set doc_urls to unique doc_url values from retrieve_context_result
    doc_urls = []
    if state.get("retrieve_context_result"):
        seen = set()
        for r in state["retrieve_context_result"]:
            if isinstance(r, dict):
                payload = r.get("payload", {})
                doc_url = payload.get("doc_url")
                if doc_url and doc_url not in seen:
                    doc_urls.append(doc_url)
                    seen.add(doc_url)
    state["doc_urls"] = doc_urls
    return state
