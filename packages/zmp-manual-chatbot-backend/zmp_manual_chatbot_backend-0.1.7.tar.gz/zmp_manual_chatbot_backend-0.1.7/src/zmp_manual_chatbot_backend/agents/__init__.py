"""
Multi-agent workflow implementation for the ZMP Manual Chatbot Backend.

This package implements the core agents that comprise the multi-agent workflow system:
- Query processing agents (rewriter, anonymizer)  
- Planning agents (planner, task handler)
- Information retrieval agents (context retriever, chat history search)
- Response generation agents (answer generator, final synthesis)

Each agent is implemented as an async function that takes a PlanExecute state
and returns an updated state, following the AsyncAgentProtocol interface.
"""

# Import all agents for backward compatibility
from .query_rewriter_agent import query_rewriter_agent
from .anonymize_query_agent import anonymize_query_agent
from .de_anonymize_plan_agent import de_anonymize_plan_agent
from .planner_agent import planner_agent
from .break_down_plan_agent import break_down_plan_agent
from .replan_agent import replan_agent
from .task_handler_agent import task_handler_agent
from .retrieve_context_agent import retrieve_context_agent
from .search_chat_history_agent import search_chat_history_agent
from .answer_agent import answer_agent
from .get_final_answer_agent import get_final_answer_agent
from .log_chat_history_agent import log_chat_history_agent

# Import utility functions
from .base import (
    update_step_tracking,
    should_log_chat_history,
    keep_only_relevant_content
)

__all__ = [
    # Utility functions
    "update_step_tracking",
    "should_log_chat_history",
    "keep_only_relevant_content",
    
    # Query processing agents
    "query_rewriter_agent",
    "anonymize_query_agent", 
    "de_anonymize_plan_agent",
    
    # Planning agents
    "planner_agent",
    "break_down_plan_agent",
    "replan_agent",
    "task_handler_agent",
    
    # Retrieval agents
    "retrieve_context_agent",
    "search_chat_history_agent",
    
    # Response agents
    "answer_agent",
    "get_final_answer_agent",
    
    # Task handling agents
    "log_chat_history_agent"
]
