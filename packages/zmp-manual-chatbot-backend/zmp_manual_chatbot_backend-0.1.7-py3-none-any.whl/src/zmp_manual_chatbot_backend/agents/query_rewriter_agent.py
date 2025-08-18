"""
Query Rewriter Agent for the multi-agent workflow system.

This agent is responsible for rewriting user queries to optimize them for
vectorstore retrieval while preserving the original intent and specific terms.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from ..utils import get_llm
from .base import update_step_tracking


class Rewritequery(BaseModel):
    rewritten_query: str = Field(description="The improved query optimized for vectorstore retrieval.")


rewrite_prompt_template = """You are a query re-writer that converts an input query to a better version optimized for vectorstore retrieval.

IMPORTANT: Your goal is to improve the query for retrieval while maintaining the original intent and specific terms.

Current query: {query}

Session dialogue context: {session_context}

ALGORITHMIC INSTRUCTIONS:

1. **Language Translation**: If the query is in a non-English language, translate it to English while preserving all technical terms and product names exactly as they appear.

2. **Coreference Resolution Algorithm (Follow-up Question Detection)**:
   - ONLY apply coreference resolution when the query contains actual vague references that need context
   - Vague references include: "this", "it", "that", "the solution", "the platform", "the system", pronouns in any language
   - **CRITICAL**: If the query explicitly mentions specific product names (APIM, ZCP, Kubernetes, Docker, etc.), treat it as an INDEPENDENT query
   - Apply coreference resolution ONLY when:
     a. Vague references are found AND
     b. No specific product/solution names are explicitly mentioned
   - When coreference resolution is needed:
     a. Parse the session dialogue from most recent to oldest
     b. Find the last Assistant response (most recent topic)
     c. Extract any product names, solution names, or technical terms from that response
     d. Replace the vague reference in the query with the most specific term found
   - If no vague references OR specific products are mentioned, proceed to step 3

3. **Query Optimization**:
   - Keep all specific technical terms unchanged (APIM, ZCP, Kubernetes, Docker, etc.)
   - Improve query structure for better search without changing core meaning
   - Convert questions to keyword-focused phrases when beneficial for retrieval
   - Maintain the original intent completely

4. **Quality Check**:
   - Ensure the rewritten query is in English
   - Verify all specific terms are preserved
   - Confirm the intent matches the original query

CONTEXT RESOLUTION LOGIC:
- If session dialogue exists and query contains vague references:
  - Identify the most recent Assistant message
  - Extract the primary subject/product being discussed in that message
  - Substitute vague references with the specific subject
- If no session dialogue or no vague references:
  - Apply basic optimization while preserving all specifics

EXAMPLES:
- Independent query: "Tell me about ZCP" → "Tell me about ZCP" (no coreference resolution needed)
- Independent query: "Tell me about APIM" → "Tell me about APIM" (no coreference resolution needed, even if ZCP was discussed before)
- Follow-up query: "Which company developed this solution?" (after discussing APIM) → "Which company developed APIM?" (coreference resolution needed)
- Follow-up query: "How does it work?" (after discussing Kubernetes) → "How does Kubernetes work?" (coreference resolution needed)

Return only the improved English query that maintains original intent and applies coreference resolution only when genuinely needed."""

rewrite_prompt = PromptTemplate(
    template=rewrite_prompt_template,
    input_variables=["query", "session_context"],
)

rewrite_query_llm = get_llm()
rewrite_query_chain = rewrite_prompt | rewrite_query_llm.with_structured_output(Rewritequery)


async def query_rewriter_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Rewrite the user query for better retrieval and update 'rewritten_query'.
    Uses session dialogue context to improve follow-up questions.
    """
    # Format session dialogue for context (most recent first for better precedence)
    session_dialogue = state.get("session_dialogue", [])
    session_context = "No previous session dialogue."
    
    if session_dialogue:
        dialogue_lines = []
        # Reverse the dialogue to show most recent first, but limit to recent context
        recent_dialogue = list(reversed(session_dialogue[-10:]))  # Last 10 messages, most recent first
        
        for message in recent_dialogue:
            if hasattr(message, 'content'):
                raw_content = message.content
            elif isinstance(message, dict):
                raw_content = message.get('content', str(message))
            else:
                raw_content = str(message)
            
            # Determine role from message type
            if hasattr(message, 'type'):
                role = "User" if message.type == "human" else "Assistant"
            elif isinstance(message, dict):
                msg_type = message.get('type', '')
                role = "User" if msg_type == "human" else "Assistant"
            else:
                # Fallback to alternating pattern
                role = "User" if len(dialogue_lines) % 2 == 0 else "Assistant"
            
            # Handle structured AI content vs plain text
            if role == "Assistant":
                # Handle structured AI responses (list containing dictionary format)
                if isinstance(raw_content, list) and len(raw_content) > 0 and isinstance(raw_content[0], dict):
                    # Extract the structured content from the list
                    structured_content = raw_content[0]
                    answer = structured_content.get('answer', str(structured_content))
                    citation_map = structured_content.get('citation_map', {})
                    
                    # Include solution information from citations for better context resolution
                    solutions_mentioned = set()
                    for citation_data in citation_map.values():
                        if isinstance(citation_data, dict) and 'solution' in citation_data:
                            solutions_mentioned.add(citation_data['solution'].upper())
                    
                    if solutions_mentioned:
                        solutions_context = f" [Solutions discussed: {', '.join(solutions_mentioned)}]"
                        content = f"{answer[:400]}...{solutions_context}" if len(answer) > 400 else f"{answer}{solutions_context}"
                    else:
                        content = answer[:500] + "..." if len(answer) > 500 else answer
                elif isinstance(raw_content, dict):
                    # Handle direct dictionary format (fallback)
                    answer = raw_content.get('answer', str(raw_content))
                    citation_map = raw_content.get('citation_map', {})
                    
                    # Include solution information from citations for better context resolution
                    solutions_mentioned = set()
                    for citation_data in citation_map.values():
                        if isinstance(citation_data, dict) and 'solution' in citation_data:
                            solutions_mentioned.add(citation_data['solution'].upper())
                    
                    if solutions_mentioned:
                        solutions_context = f" [Solutions discussed: {', '.join(solutions_mentioned)}]"
                        content = f"{answer[:400]}...{solutions_context}" if len(answer) > 400 else f"{answer}{solutions_context}"
                    else:
                        content = answer[:500] + "..." if len(answer) > 500 else answer
                else:
                    # Plain text format for other content types
                    content = str(raw_content)
                    if len(content) > 500:
                        content = content[:500] + "..."
            else:
                content = str(raw_content)
                if len(content) > 500:
                    content = content[:500] + "..."
            
            dialogue_lines.append(f"{role}: {content}")
        
        session_context = "\n".join(dialogue_lines)
        print(f"[query_rewriter_agent] Using session context with {len(recent_dialogue)} messages (most recent first)")
    else:
        print("[query_rewriter_agent] No session dialogue context available")
    
    result = await rewrite_query_chain.ainvoke({
        "query": state["query"],
        "session_context": session_context
    })
    state["rewritten_query"] = result.rewritten_query
    print(f"[query_rewriter_agent] Original: '{state['query']}' → Rewritten: '{result.rewritten_query}'")
    update_step_tracking(state, "query_rewriter")
    return state
