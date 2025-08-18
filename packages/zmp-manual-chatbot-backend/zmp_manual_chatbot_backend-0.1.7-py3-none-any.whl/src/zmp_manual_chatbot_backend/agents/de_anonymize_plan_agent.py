"""
De-Anonymize Plan Agent for the multi-agent workflow system.

This agent is responsible for de-anonymizing plans by replacing variables
with their original mapped words.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
from ..utils import get_llm
from .base import update_step_tracking


class DeAnonymizePlan(BaseModel):
    plan: List[str] = Field(description="Plan to follow in future. with all the variables replaced with the mapped words.")


de_anonymize_plan_prompt = PromptTemplate(
    template="""
You receive a list of tasks: {plan}, where some of the words are replaced with mapped variables. 
You also receive the mapping for those variables to words {mapping}. 
Replace all the variables in the list of tasks with the mapped words. 
If no variables are present, return the original list of tasks. 
In any case, just output the updated list of tasks in a JSON format as described here, 
without any additional text apart from the JSON.
""",
    input_variables=["plan", "mapping"],
)

de_anonymize_plan_llm = get_llm()
de_anonymize_plan_chain = (
    de_anonymize_plan_prompt
    | de_anonymize_plan_llm.with_structured_output(DeAnonymizePlan)
)


async def de_anonymize_plan_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: De-anonymize the plan by replacing variables with their original mapped words.
    
    This agent takes the anonymized plan and replaces all variables with their
    original names using the mapping created during the anonymization process.
    """
    result = await de_anonymize_plan_chain.ainvoke({
        "plan": state["plan"],
        "mapping": state["mapping"],
    })
    state["plan"] = result.plan
    update_step_tracking(state, "de_anonymize_plan")
    return state
