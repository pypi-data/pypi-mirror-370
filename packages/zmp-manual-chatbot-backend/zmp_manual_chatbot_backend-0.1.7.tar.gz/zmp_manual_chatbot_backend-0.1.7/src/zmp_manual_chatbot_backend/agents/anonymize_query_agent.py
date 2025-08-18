"""
Anonymize Query Agent for the multi-agent workflow system.

This agent is responsible for anonymizing queries by replacing named entities,
solution names, and product names with variables while maintaining a mapping
for later de-anonymization.
"""

from ..schemas import PlanExecute
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import json
from ..utils import get_llm
from .base import update_step_tracking


class Anonymizequery(BaseModel):
    anonymized_query: str = Field(description="Anonymized query.")
    mapping: str = Field(description="Mapping of original name entities to variables as JSON string.")


anonymize_query_prompt = PromptTemplate(
    template="""
You are a query anonymizer. The input you receive is a string containing several words that
construct a query {query}. Your goal is to change all name entities, solution names, and product names in the input to variables, and remember the mapping of the original names to the variables.

IMPORTANT: You should anonymize:
1. Personal names (people, companies, organizations)
2. Solution names (like APIM, ZCP, Kubernetes, etc.)
3. Product names and specific technology names
4. Any other specific named entities

Example 1:
  if the input is "who is harry potter?" the output should be "who is X?" and the mapping should be {{"X": "harry potter"}}

Example 2:
  if the input is "how did the bad guy played with the alex and rony?"
  the output should be "how did the X played with the Y and Z?" and the mapping should be {{"X": "bad guy", "Y": "alex", "Z": "rony"}}

Example 3:
  if the input is "APIM에 대해 알려줘" the output should be "X에 대해 알려줘" and the mapping should be {{"X": "APIM"}}

Example 4:
  if the input is "Tell me about ZCP and Kubernetes" the output should be "Tell me about X and Y" and the mapping should be {{"X": "ZCP", "Y": "Kubernetes"}}

You must replace all name entities, solution names, and product names in the input with variables, and remember the mapping of the original names to the variables.
Output the anonymized query and the mapping in a JSON format.
""",
    input_variables=["query"],
)

anonymize_query_llm = get_llm()
anonymize_query_chain = anonymize_query_prompt | anonymize_query_llm.with_structured_output(Anonymizequery)


async def anonymize_query_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Anonymize the query by replacing named entities with variables.
    
    This agent takes the rewritten query (or original query if rewritten is not available)
    and anonymizes it by replacing all named entities, solution names, and product names
    with variables while maintaining a mapping for later de-anonymization.
    """
    # Use rewritten_query if available, otherwise fall back to original query
    query_to_anonymize = state.get("rewritten_query", state.get("query", ""))
    result = await anonymize_query_chain.ainvoke({"query": query_to_anonymize})
    state["anonymized_query"] = result.anonymized_query
    # Parse the mapping from JSON string to dictionary
    try:
        state["mapping"] = json.loads(result.mapping)
    except (json.JSONDecodeError, TypeError):
        state["mapping"] = {}
    update_step_tracking(state, "anonymize_query")
    return state
