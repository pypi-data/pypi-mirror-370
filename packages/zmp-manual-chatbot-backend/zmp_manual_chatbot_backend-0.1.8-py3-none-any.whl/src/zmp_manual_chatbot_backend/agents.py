"""
Multi-agent workflow implementation for the ZMP Manual Chatbot Backend.

This module imports all agents from the modular agents package for backward compatibility.
The agents have been refactored into separate files for better maintainability.

Each agent is implemented as an async function that takes a PlanExecute state
and returns an updated state, following the AsyncAgentProtocol interface.
"""

# Import all agents from the modular agents package
from .agents import (
    # Utility functions
    update_step_tracking,
    should_log_chat_history,
    keep_only_relevant_content,
    
    # Query processing agents
    query_rewriter_agent,
    anonymize_query_agent,
    de_anonymize_plan_agent,
    
    # Planning agents
    planner_agent,
    break_down_plan_agent,
    replan_agent,
    task_handler_agent,
    
    # Retrieval agents
    retrieve_context_agent,
    search_chat_history_agent,
    
    # Response agents
    answer_agent,
    get_final_answer_agent,
    
    # Task handling agents
    log_chat_history_agent
)

# Re-export everything for backward compatibility
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
