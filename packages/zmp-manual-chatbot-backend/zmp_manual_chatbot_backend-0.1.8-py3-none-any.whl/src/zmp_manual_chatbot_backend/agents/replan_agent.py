"""
Replan Agent for the multi-agent workflow system.

This agent evaluates whether enough information has been gathered to answer
the user's query and decides whether to continue searching or proceed to answer generation.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
from ..utils import get_llm
from .base import update_step_tracking, keep_only_relevant_content


class Plan(BaseModel):
    steps: List[str] = Field(description="different steps to follow, should be in sorted order")


class ActPossibleResults(BaseModel):
    plan: Plan = Field(description="Plan to follow in future.")
    explanation: str = Field(description="Explanation of the action.")
    can_be_answered_already: bool = Field(description="Whether enough information has been gathered to generate a final answer.")
    new_search_query: Optional[str] = Field(description="If more information is needed, generate a NEW, MORE SPECIFIC search query different from the original query to find missing information.", default=None)


replanner_prompt = PromptTemplate(
    template="""
You are a replanning agent that evaluates whether enough information has been gathered to answer the user's query.

User Query: {query}

ORIGINAL PLAN: {plan}
STEPS COMPLETED: {past_steps}
RETRIEVED CONTEXT: {aggregated_context}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the user's query
- Analyze the user's query language and respond in that same language
- Do NOT translate or change the language
- Do NOT respond in any other language
- This is a strict requirement - you must follow the user's language exactly

All your reasoning and output must be in the user's language.

EVALUATION CRITERIA:
1. If the retrieved context contains clear, specific information that directly answers the query, set can_be_answered_already = True
2. If the context is vague, incomplete, or doesn't address the query, set can_be_answered_already = False
3. Consider the quality and relevance of the retrieved information

DECISION RULES:
- Set can_be_answered_already = True if:
  * The context clearly defines what the query is asking about (e.g., "What is X?" and context explains what X is)
  * The context provides specific details and explanations
  * The information is relevant and comprehensive
  * You can generate a complete answer from the available context
  * The context contains concrete facts, definitions, or explanations
  * **CRITICAL**: If the context is "No relevant context found." or similar, set can_be_answered_already = True

- Set can_be_answered_already = False ONLY if:
  * The context contains some information but is completely vague or general
  * The retrieved information doesn't address the query at all
  * You need more specific or detailed information that is completely missing
  * **IMPORTANT**: Do NOT set to False if the context is "No relevant context found." - this means no data exists

IMPORTANT: If the context contains ANY specific information about the query topic, even if it's not exhaustive, set can_be_answered_already = True. Do not be overly perfectionist.

**CRITICAL FOR NO DATA SCENARIOS:**
- If the context is "No relevant context found." or similar, this means no data exists for the query topic
- In this case, set can_be_answered_already = True and plan = []
- The system will generate a "no information available" response
- Do NOT try to search for more information when no data exists

If can_be_answered_already = True:
- Set plan to an empty list []
- The workflow will proceed to answer generation

If can_be_answered_already = False:
- Provide a refined plan with specific steps to gather missing information
- Focus on what specific information is still needed
- Do not repeat steps that have already been completed
- **CRITICAL**: Generate a NEW, MORE SPECIFIC search query in the `new_search_query` field
- **IMPORTANT**: The `new_search_query` MUST ALWAYS be in ENGLISH for better search effectiveness in the knowledge base
- The new query should be different from the original query and target the specific missing information
- Examples:
  * Original: "Who developed ZCP?" → New: "ZCP development team" or "ZCP creator company" or "ZCP vendor information"
  * Original: "What is APIM?" → New: "APIM architecture components" or "APIM installation process"  
  * Original: "How to install X?" → New: "X installation requirements" or "X configuration steps"
  * Korean Original: "이 솔루션을 개발한 회사는?" → New English: "APIM solution vendor company" or "APIM development company information"

**ReAct-Style Query Generation Rules:**
- Analyze what information is missing from the current context
- Generate a search query IN ENGLISH that specifically targets that missing information
- Make the new query more focused and specific than the original
- Avoid repeating the same query that was already tried
- Think like a researcher refining their search strategy
- Always use English for new_search_query regardless of user's original language

Remember: The goal is to efficiently determine if we have enough information to provide a comprehensive answer to the user's query. If more information is needed, generate a smart, targeted new query to find it. Be decisive and don't overthink.
""",
    input_variables=["query", "plan", "past_steps", "aggregated_context"],
)

replanner_llm = get_llm()
replanner_chain = replanner_prompt | replanner_llm.with_structured_output(ActPossibleResults)


async def replan_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Evaluate whether enough information has been gathered and decide next steps.
    
    This agent analyzes the retrieved context and determines whether the workflow
    has enough information to generate a final answer or needs to continue searching.
    """
    # Extract context from retrieved results
    context_parts = []
    
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
    
    # Check if we have any relevant results
    has_relevant_results = len(context_parts) > 0 and combined_context != "No relevant context found."
    
    # Get current query for logging and analysis
    current_query = state.get("rewritten_query", state.get("query", ""))
    
    # LLM-based semantic relevance check
    if len(combined_context) > 50:  # Only check if we have substantial context
        try:
            # Use the existing keep_only_relevant_content function for semantic relevance checking
            filter_state = {
                "question": current_query,
                "context": combined_context
            }
            
            filtered_output = keep_only_relevant_content(filter_state)
            relevant_content = filtered_output["relevant_context"]
            
            # Check if the LLM found the context irrelevant to the query
            if (relevant_content == "NO_RELEVANT_CONTENT_FOUND" or 
                "not explicitly mentioned" in relevant_content.lower() or
                "no relevant content" in relevant_content.lower()):
                print("[replan_agent] LLM-based semantic check: context is not relevant to query")
                print(f"[replan_agent] Query: {current_query}")
                print(f"[replan_agent] LLM relevance result: {relevant_content}")
                has_relevant_results = False
            else:
                print("[replan_agent] LLM-based semantic check: context is relevant to query")
        except Exception as e:
            print(f"[replan_agent] Error in LLM-based semantic relevance check: {e}")
            # Continue with existing logic if LLM check fails
    
    # If no relevant results found, set a flag for the replanner and skip LLM call
    if not has_relevant_results:
        state["no_relevant_data_found"] = True
        print(f"[replan_agent] No relevant data found for query: {current_query}")
        print(f"[replan_agent] Combined context: {combined_context[:200]}...")
        # Set plan to empty to stop the loop and proceed to final answer
        state["plan"] = []
        state["can_be_answered_already"] = True
        update_step_tracking(state, "replan")
        print("[replan_agent] Skipping LLM call - proceeding to final answer generation")
        return state
    
    # Only call LLM if we have relevant results
    query = state.get("rewritten_query", state.get("query", ""))
    plan = state.get("plan", [])
    past_steps = state.get("past_steps", [])
    
    # Safety mechanism: if we've been through multiple replan cycles, force completion
    past_steps = state.get("past_steps", [])
    replan_count = past_steps.count("replan")
    if replan_count >= 2:  # Reduced from 3 to 2 to prevent excessive looping
        print(f"[replan_agent] Safety mechanism: {replan_count} replan cycles detected, forcing completion")
        state["plan"] = []
        state["can_be_answered_already"] = True
        update_step_tracking(state, "replan")
        return state
    
    result = await replanner_chain.ainvoke({
        "query": query,
        "plan": plan,
        "past_steps": past_steps,
        "aggregated_context": combined_context
    })
    
    print(f"[replan_agent] LLM decision: can_be_answered_already = {result.can_be_answered_already}")
    print(f"[replan_agent] Query: {query}")
    print(f"[replan_agent] Context length: {len(combined_context)} chars")
    print(f"[replan_agent] Replan count: {replan_count}")
    
    # Update the query if a new search query was generated (ReAct-style)
    if result.new_search_query and result.new_search_query.strip():
        print(f"[replan_agent] New search query generated: {result.new_search_query}")
        print(f"[replan_agent] Original query: {query}")
        # Update the rewritten query to use the new, more specific query
        state["rewritten_query"] = result.new_search_query
        # Also update query_to_retrieve_or_answer for the next agent cycle
        state["query_to_retrieve_or_answer"] = result.new_search_query
    
    state["plan"] = result.plan.steps
    state["can_be_answered_already"] = result.can_be_answered_already
    update_step_tracking(state, "replan")
    # Optionally: state["replan_explanation"] = result.explanation
    return state
