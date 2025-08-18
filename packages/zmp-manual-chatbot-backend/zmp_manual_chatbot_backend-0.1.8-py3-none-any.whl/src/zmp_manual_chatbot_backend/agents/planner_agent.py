"""
Planner Agent for the multi-agent workflow system.

This agent is responsible for creating step-by-step plans to answer user queries
and generating thread IDs for conversation continuity.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from ..utils import get_llm
from .base import update_step_tracking


class Plan(BaseModel):
    steps: List[str] = Field(description="different steps to follow, should be in sorted order")


class ThreadIdGeneration(BaseModel):
    main_topic: str = Field(description="Main topic/product being discussed (e.g., 'APIM', 'ZCP', 'Kubernetes')")
    subtopic: str = Field(description="Specific aspect or feature (e.g., 'features', 'installation', 'troubleshooting')")
    keywords: list[str] = Field(description="2-3 key terms that best describe the query")


planner_prompt = PromptTemplate(
    template="""
You are a planning agent that creates a step-by-step plan to answer the user's query.

Original User Query: {rewritten_query}
Rewritten Query (for understanding intent): {rewritten_query}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the original user query
- Analyze the original user query language and respond in that same language
- Use the rewritten query to understand the intent and create relevant steps
- Do NOT translate or change the language from the original query
- Do NOT respond in any other language
- This is a strict requirement - you must follow the original query's language exactly

Instructions:
1. Create a clear, concise plan in the SAME LANGUAGE as the original user query.
2. Use the rewritten query to understand the intent and make the plan relevant.
3. Each step should be actionable and relevant to answering the user's question.
4. All reasoning and output must be in the original user's language.
5. Do NOT use any other language in your response.

Generate your plan in the original user's language only.
""",
    input_variables=["rewritten_query"],
)


thread_id_prompt = PromptTemplate(
    template="""
You are a topic analyzer for technical documentation queries. Analyze the user's query and extract:

1. Main topic/product: The primary subject (e.g., APIM, ZCP, Kubernetes, etc.)
2. Subtopic: The specific aspect being discussed (e.g., features, setup, troubleshooting)
3. Keywords: 2-3 most important terms that capture the essence of the query

Guidelines:
- Keep topics concise and technical
- Use English terms even if query is in other languages
- Focus on product names and technical concepts
- Avoid generic words like "what", "how", "tell me"
- For follow-up questions, try to maintain consistency with the main topic

Query: {query}

Extract the topic information:
""",
    input_variables=["query"]
)

planner_llm = get_llm()
planner_chain = planner_prompt | planner_llm.with_structured_output(Plan)

thread_id_llm = get_llm()
thread_id_chain = thread_id_prompt | thread_id_llm.with_structured_output(ThreadIdGeneration)


async def planner_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Create a step-by-step plan to answer the user's query and generate thread ID.
    
    This agent generates both a plan for answering the query and creates a thread ID
    for conversation continuity. The thread ID is generated early in the workflow
    to ensure it's available for metadata responses.
    """
    # Use both original and rewritten queries for planning
    rewritten_query = state.get("query", "")
    rewritten_query = state.get("rewritten_query", rewritten_query)
    print(f"[planner_agent] Original query: {rewritten_query}")
    print(f"[planner_agent] Rewritten query: {rewritten_query}")
    
    # ===== GENERATE THREAD_ID EARLY IN WORKFLOW =====
    # Generate or reuse thread_id BEFORE planning so it's available for metadata
    try:
        # Check if we already have a thread_id from persistent state (follow-up questions)
        existing_thread_id = state.get("thread_id")
        if existing_thread_id and existing_thread_id.startswith("thread_"):
            print(f"[planner_agent] Reusing persistent thread_id from session: {existing_thread_id}")
        else:
            # Generate new thread_id using LLM topic analysis (first question in session)
            query = state.get("query", "")
            
            try:
                # Use the thread_id generation chain from log_chat_history_agent
                result = await thread_id_chain.ainvoke({"query": query})
                
                # Generate thread_id from topic analysis
                main_topic = result.main_topic.replace(" ", "_").lower()
                subtopic = result.subtopic.replace(" ", "_").lower()
                keywords_str = "_".join(result.keywords).lower()
                keywords_hash = abs(hash(keywords_str)) % 10000  # 4-digit hash
                
                thread_id = f"thread_{main_topic}_{subtopic}_{keywords_hash:04d}"
                
                # Clean up the thread_id (remove any special characters, limit length)
                thread_id = "".join(c for c in thread_id if c.isalnum() or c == "_")
                thread_id = thread_id[:50]  # Limit length
                
                # Store in state for persistence across session
                state["thread_id"] = thread_id
                
                print(f"[planner_agent] Generated new thread_id for session: {thread_id}")
                print(f"[planner_agent] Topic analysis: main={result.main_topic}, sub={result.subtopic}, keywords={result.keywords}")
                
            except Exception as e:
                # Fallback: generate a simple hash-based thread_id
                print(f"[planner_agent] Error generating LLM-based thread_id: {e}")
                query_hash = abs(hash(query.lower().strip())) % 100000
                fallback_thread_id = f"thread_general_{query_hash:05d}"
                state["thread_id"] = fallback_thread_id
                print(f"[planner_agent] Using fallback thread_id: {fallback_thread_id}")
    
    except Exception as e:
        print(f"[planner_agent] Error in thread_id generation: {e}")
        # Set a default thread_id
        state["thread_id"] = f"thread_error_{abs(hash(str(e))) % 10000:04d}"
    
    # Plan using both queries - original for language, rewritten for intent
    result = await planner_chain.ainvoke({
        "rewritten_query": rewritten_query
    })
    state["plan"] = result.steps
    update_step_tracking(state, "planner")
    return state
