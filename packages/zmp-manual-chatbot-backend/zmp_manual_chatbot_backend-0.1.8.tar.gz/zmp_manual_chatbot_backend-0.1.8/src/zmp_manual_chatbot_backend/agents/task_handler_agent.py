"""
Task Handler Agent for the multi-agent workflow system.

This agent is responsible for handling task execution logic.
"""

from ..schemas import PlanExecute
from pydantic import BaseModel
from .base import update_step_tracking


class TaskHandlerOutput(BaseModel):
    plan: list = []
    instruction: str = ""


async def task_handler_agent(state: PlanExecute) -> PlanExecute:
    """
    Agent: Handle task execution logic.
    
    This agent manages the task execution flow and updates the workflow state
    for the next steps in the pipeline.
    """
    # Set the plan to empty to indicate task handling is complete
    state["plan"] = []
    update_step_tracking(state, "task_handler")
    return state
