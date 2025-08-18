"""
Base utilities and shared components for the multi-agent workflow system.

This module contains shared utilities, helper functions, and Pydantic models
that are used across multiple agents in the workflow.
"""

from ..schemas import PlanExecute
from typing import Optional, List
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import asyncio
import json
from ..mcp_client import MCPClient
from ..utils import get_llm, extract_mcp_results, extract_citations_from_results
from pprint import pprint


def update_step_tracking(state: PlanExecute, step_name: str) -> None:
    """
    Update workflow step tracking in the PlanExecute state.
    
    This helper function maintains the current step and history of completed
    steps in the workflow state. It's used by all agents to track progress
    through the multi-agent pipeline.
    
    Args:
        state (PlanExecute): The current workflow state to update
        step_name (str): Name of the current step being executed
        
    Note:
        - Updates the 'current_step' field with the new step name
        - Always appends the step to 'past_steps' list to track all executions
        - Maintains chronological order of step execution, including loops
    """
    state["current_step"] = step_name
    past_steps = state.get("past_steps", [])
    # Always append to track all step executions, including loops/repeats
    past_steps.append(step_name)
    state["past_steps"] = past_steps


def should_log_chat_history(state: PlanExecute) -> bool:
    """
    Determine if response should be logged to chat history based on quality metrics.
    
    This function implements intelligent chat history logging by evaluating multiple
    quality indicators to determine if a response contains meaningful information
    that would be valuable for future context.
    
    Args:
        state (PlanExecute): The workflow state containing the generated response
        
    Returns:
        bool: True if the response should be logged to chat history, False otherwise
        
    Quality Assessment Criteria:
        - Response has a non-empty final answer
        - LLM-generated quality score indicates valuable content (> 0.0)
        - Response is not an error message
        - Additional boost for responses with citations
        - Minimum confidence threshold for uncertain responses
        
    Example:
        if should_log_chat_history(state):
            await log_to_chat_history(state["query"], state["final_answer"])
    """
    final_answer = state.get("final_answer", "")
    quality_score = state.get("answer_quality_score", 0.0)
    answer_confidence = state.get("answer_confidence", 0.0)
    has_citations = len(state.get("citation_map", {})) > 0
    
    # Don't log if no answer
    if not final_answer or final_answer.strip() == "":
        print("[should_log_chat_history] No final answer, not logging")
        return False
    
    # Don't log error responses
    if "error occurred" in final_answer.lower():
        print("[should_log_chat_history] Detected error response, not logging")
        return False
    
    # Primary decision based on LLM quality score
    # The LLM sets quality_score to 0.0 when no relevant data is available
    if quality_score <= 0.0:
        print(f"[should_log_chat_history] LLM quality score indicates no valuable information (score: {quality_score}), not logging")
        return False
    
    # Don't log very low quality responses
    if quality_score < 0.3:
        print(f"[should_log_chat_history] Quality score too low ({quality_score}), not logging")
        return False
    
    # Log if we have citations (indicates real content was found and cited)
    if has_citations:
        print(f"[should_log_chat_history] Response has {len(state.get('citation_map', {}))} citations with quality score {quality_score}, logging")
        return True
    
    # Log if quality score indicates meaningful content (even without citations)
    if quality_score >= 0.5:
        print(f"[should_log_chat_history] High quality response (score: {quality_score}, confidence: {answer_confidence}), logging")
        return True
    
    # Log moderate quality responses if they have decent confidence
    if quality_score >= 0.3 and answer_confidence >= 0.6:
        print(f"[should_log_chat_history] Moderate quality with high confidence (score: {quality_score}, confidence: {answer_confidence}), logging")
        return True
    
    # Default: don't log low quality responses
    print(f"[should_log_chat_history] Quality score {quality_score} and confidence {answer_confidence} don't meet logging criteria, not logging")
    return False


# LLM-based Content Filtering Components
# Define a prompt template for filtering out non-relevant content from retrieved documents.
keep_only_relevant_content_prompt_template = """
You receive a query: {query} and retrieved documents: {retrieved_documents} from a vector store.

CRITICAL INSTRUCTIONS:
1. Your ONLY job is to filter out irrelevant content. Do NOT try to make connections or find broader relevance.
2. If the query asks about a specific product/technology (like APIM, ZCP, Kubernetes, Docker), ONLY keep content that EXPLICITLY mentions that specific product/technology.
3. If the retrieved documents do NOT contain the specific product/technology mentioned in the query, return "NO_RELEVANT_CONTENT_FOUND".
4. Do NOT try to connect unrelated technologies or find broader relevance.
5. Do NOT add explanations or try to be helpful - just filter the content strictly.
6. **LANGUAGE REQUIREMENT**: Always respond in the same language as the user's query. If the query is in Korean, respond in Korean. If the query is in English, respond in English. If the query is in another language, respond in that language.

Examples:
- Query: "What is APIM?" + Documents about ZCP → Return "NO_RELEVANT_CONTENT_FOUND"
- Query: "What is ZCP?" + Documents about ZCP → Return only ZCP-specific content
- Query: "How does Kubernetes work?" + Documents about Docker → Return "NO_RELEVANT_CONTENT_FOUND"

Output the filtered relevant content OR "NO_RELEVANT_CONTENT_FOUND" if no relevant content exists.
"""


# Define a Pydantic model for structured output from the LLM, specifying that the output should contain only the relevant content.
class KeepRelevantContent(BaseModel):
    relevant_content: str = Field(description="The relevant content from the retrieved documents that is relevant to the query.")


# Create a prompt template for filtering only the relevant content from retrieved documents, using the provided template string.
keep_only_relevant_content_prompt = PromptTemplate(
    template=keep_only_relevant_content_prompt_template,
    input_variables=["query", "retrieved_documents"],
)

# Create a chain that combines the prompt template, the LLM, and the structured output parser.
# The chain takes a query and retrieved documents, filters out non-relevant information,
# and returns only the relevant content as specified by the KeepRelevantContent Pydantic model.
keep_only_relevant_content_llm = get_llm()
keep_only_relevant_content_chain = (
    keep_only_relevant_content_prompt
    | keep_only_relevant_content_llm.with_structured_output(KeepRelevantContent)
)


def keep_only_relevant_content(state):
    """
    Filters and retains only the content from the retrieved documents that is relevant to the query.

    Args:
        state (dict): A dictionary containing:
            - "question": The user's query.
            - "context": The retrieved documents/content as a string.

    Returns:
        dict: A dictionary with:
            - "relevant_context": The filtered relevant content as a string.
            - "context": The original context.
            - "question": The original question.
    """
    question = state["question"]
    context = state["context"]

    # Prepare input for the LLM chain
    input_data = {
        "query": question,
        "retrieved_documents": context
    }

    print("keeping only the relevant content...")
    pprint("--------------------")

    # Invoke the LLM chain to filter out non-relevant content
    output = keep_only_relevant_content_chain.invoke(input_data)
    relevant_content = output.relevant_content

    # Ensure the result is a string (in case it's not)
    relevant_content = "".join(relevant_content)

    # Escape quotes for downstream processing
    relevant_content = relevant_content.replace('"', '\\"').replace("'", "\\'")

    return {
        "relevant_context": relevant_content,
        "context": context,
        "question": question
    }
