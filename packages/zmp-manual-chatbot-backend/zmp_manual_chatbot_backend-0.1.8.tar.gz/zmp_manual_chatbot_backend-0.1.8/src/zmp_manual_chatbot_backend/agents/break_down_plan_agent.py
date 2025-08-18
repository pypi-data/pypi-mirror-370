"""
Break Down Plan Agent for the multi-agent workflow system.

This agent is responsible for refining a plan into more detailed steps.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from ..utils import get_llm
from .base import update_step_tracking


class Plan(BaseModel):
    steps: List[str] = Field(description="different steps to follow, should be in sorted order")


break_down_plan_prompt = PromptTemplate(
    template="""
You are a plan breakdown agent that refines a plan into more detailed steps.

Original User Query: {rewritten_query}
Rewritten Query (for understanding intent): {rewritten_query}
Original Plan: {plan}

CRITICAL LANGUAGE REQUIREMENTS:
- You MUST respond in the EXACT SAME LANGUAGE as the original user query
- Analyze the original user query language and respond in that same language
- Use the rewritten query to understand the intent and refine the plan appropriately
- Do NOT translate or change the language from the original query
- Do NOT respond in any other language
- This is a strict requirement - you must follow the original query's language exactly

Instructions:
1. Break down the plan into more detailed, actionable steps in the SAME LANGUAGE as the original user query.
2. Use the rewritten query to understand the intent and make the plan more relevant.
3. All reasoning and output must be in the original user's language.
4. Do NOT use any other language in your response.

Generate your detailed plan in the original user's language only.
""",
    input_variables=["rewritten_query", "plan"],
)

break_down_plan_llm = get_llm()
break_down_plan_chain = break_down_plan_prompt | break_down_plan_llm.with_structured_output(Plan)


async def break_down_plan_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Break down the plan into more detailed, actionable steps.
    
    This agent takes the initial plan and refines it into more specific and
    actionable steps while maintaining the original language of the user query.
    """
    # Use both original and rewritten queries for plan breakdown
    rewritten_query = state.get("query", "")
    rewritten_query = state.get("rewritten_query", rewritten_query)
    plan = state.get("plan", [])
    print(f"[break_down_plan_agent] Processing original query: {rewritten_query}")
    print(f"[break_down_plan_agent] Processing rewritten query: {rewritten_query}")
    
    result = await break_down_plan_chain.ainvoke({
        "rewritten_query": rewritten_query,
        "plan": plan
    })
    state["plan"] = result.steps
    update_step_tracking(state, "break_down_plan")
    return state
