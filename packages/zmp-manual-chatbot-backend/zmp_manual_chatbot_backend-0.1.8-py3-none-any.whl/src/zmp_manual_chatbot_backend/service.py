from .mcp_client import MCPClient
from langgraph.graph import StateGraph, END, START
from langgraph.errors import GraphRecursionError
from .schemas import PlanExecute
import aiofiles
import logging
from .utils import set_plan_execute, get_plan_execute
from .agents import (
    query_rewriter_agent,
    anonymize_query_agent,
    planner_agent,
    de_anonymize_plan_agent,
    break_down_plan_agent,
    task_handler_agent,
    retrieve_context_agent,
    search_chat_history_agent,
    answer_agent,
    replan_agent,
    get_final_answer_agent,
    log_chat_history_agent,
)

class ChatbotService:
    def __init__(self, mcp_client: MCPClient = None):
        self.mcp_client = mcp_client or MCPClient()
        self.workflow = None  # Will be set in async_init

    @classmethod
    async def async_init(cls, mcp_client: MCPClient = None):
        self = cls(mcp_client)
        self.workflow = self._build_workflow()
        # Save the query processing graph (optional)
        graph_image = self.workflow.get_graph().draw_mermaid_png()
        async with aiofiles.open("workflow_graph.png", "wb") as f:
            await f.write(graph_image)
        return self

    def _build_workflow(self):
        graph = StateGraph(PlanExecute)
        # Add nodes using modular agent functions
        graph.add_node("query_rewriter", query_rewriter_agent)
        graph.add_node("anonymize_query", anonymize_query_agent)
        graph.add_node("planner", planner_agent)
        graph.add_node("de_anonymize_plan", de_anonymize_plan_agent)
        graph.add_node("break_down_plan", break_down_plan_agent)
        graph.add_node("task_handler", task_handler_agent)
        graph.add_node("retrieve_context", retrieve_context_agent)
        graph.add_node("search_chat_history", search_chat_history_agent)
        graph.add_node("answer", answer_agent)
        graph.add_node("replan", replan_agent)
        graph.add_node("get_final_answer", get_final_answer_agent)
        graph.add_node("log_chat_history", log_chat_history_agent)
        # Set entry point
        graph.add_edge(START, "query_rewriter")
        graph.add_edge("query_rewriter", "anonymize_query")
        # Linear flow
        graph.add_edge("anonymize_query", "planner")
        graph.add_edge("planner", "de_anonymize_plan")
        graph.add_edge("de_anonymize_plan", "break_down_plan")
        graph.add_edge("break_down_plan", "search_chat_history")
        graph.add_edge("search_chat_history", "task_handler")
        # Task handler branching: Route based on chat history results and determined tool
        def task_handler_router(state):
            tool = state.get("tool", "")
            chat_history_results = state.get("chat_history_result", [])
            
            logging.info(f"[task_handler_router] Tool determined by task_handler: {tool}")
            logging.info(f"[task_handler_router] Chat history results count: {len(chat_history_results) if chat_history_results else 0}")
            
            # Priority 1: If task_handler decided to search knowledge base, do that regardless of chat history presence
            if tool == "search_knowledge":
                logging.info("[task_handler_router] Task handler determined knowledge search needed, routing to retrieve_context")
                return "retrieve_context"
            # Priority 2: If the task handler determined we should answer from context, go directly to answer
            elif tool == "answer_from_context":
                logging.info("[task_handler_router] Task handler determined answer from context, routing to answer")
                return "answer"
            # Priority 3: If chat history found relevant results and no specific tool was set
            elif chat_history_results and len(chat_history_results) > 0:
                logging.info(f"[task_handler_router] Found relevant chat history ({len(chat_history_results)} results), routing to answer")
                return "answer"
            # Fallback: No relevant data, search knowledge base
            else:
                logging.info("[task_handler_router] No relevant data found, routing to retrieve_context")
                return "retrieve_context"
        
        graph.add_conditional_edges(
            "task_handler",
            task_handler_router,
            {
                "retrieve_context": "retrieve_context", 
                "answer": "answer"
            }
        )
        
        # Other nodes go directly to replan
        graph.add_edge("retrieve_context", "replan")
        graph.add_edge("answer", "replan")
        # Replan branching
        def replan_router(state):
            if state.get("can_be_answered_already"):
                return "get_final_answer"
            else:
                return "break_down_plan"
        graph.add_conditional_edges(
            "replan",
            replan_router,
            {"get_final_answer": "get_final_answer", "break_down_plan": "break_down_plan"}
        )
        # Get final answer -> Log chat history -> END
        graph.add_edge("get_final_answer", "log_chat_history")
        graph.add_edge("log_chat_history", END)
        return graph.compile()

    async def run_workflow(self, state: dict):
        session_id = state.get("session_id")
        incoming_query = state.get("query")
        incoming_chat_history = state.get("chat_history", [])
        incoming_image_url = state.get("image_url")
        incoming_user_id = state.get("user_id")
        incoming_user_name = state.get("user_name")
        incoming_thread_id = state.get("thread_id")  # Extract client-provided thread_id
        
        # Always process queries fresh - never reuse cached workflow state
        # Only preserve session metadata if available
        if session_id:
            loaded_state = await get_plan_execute(session_id)
            if loaded_state:
                cached_query = loaded_state.get("query")
                logging.info(f"Processing fresh query in session {session_id}. Previous: '{cached_query}', Current: '{incoming_query}'")
            else:
                logging.info(f"Starting new session {session_id} with query: '{incoming_query}'")
            
            # Always reset workflow state, preserve only session info
            state.update({
                "session_id": session_id,
                "query": incoming_query,
                "chat_history": incoming_chat_history,
                "image_url": incoming_image_url,
                "user_id": incoming_user_id,
                "user_name": incoming_user_name,
                "thread_id": incoming_thread_id  # Include client-provided thread_id
            })
        
        # Ensure user_id and user_name are always set in state (for cases where session_id is None)
        if "user_id" not in state:
            state["user_id"] = incoming_user_id
        if "user_name" not in state:
            state["user_name"] = incoming_user_name
        
        # Debug logging for user_id and user_name tracking
        logging.info(f"[run_workflow] incoming_user_id: {incoming_user_id}")
        logging.info(f"[run_workflow] incoming_user_name: {incoming_user_name}")
        logging.info(f"[run_workflow] final state user_id: {state.get('user_id')}")
        logging.info(f"[run_workflow] final state user_name: {state.get('user_name')}")
        
        # Initialize required fields for PlanExecute TypedDict
        state.setdefault("past_steps", [])
        state.setdefault("current_step", "")
        state.setdefault("anonymized_query", "")
        state.setdefault("rewritten_query", None)
        state.setdefault("query_to_retrieve_or_answer", "")
        state.setdefault("plan", [])
        state.setdefault("mapping", {})
        state.setdefault("current_context", "")
        state.setdefault("aggregated_context", "")
        state.setdefault("tool", "")
        state.setdefault("retrieve_context_result", None)
        state.setdefault("chat_history_result", None)
        
        # Load session_dialogue from saved session state if not already set
        if not state.get("session_dialogue"):
            if session_id:
                loaded_state = await get_plan_execute(session_id)
                if loaded_state and loaded_state.get("session_dialogue"):
                    saved_session_dialogue = loaded_state.get("session_dialogue", [])
                    state["session_dialogue"] = saved_session_dialogue
                    print(f"[run_workflow] Loaded session_dialogue with {len(saved_session_dialogue)} messages from saved session state")
            else:
                state.setdefault("session_dialogue", [])
        
        # Thread_id priority logic:
        # 1. If client provided thread_id -> use it (update session state)  
        # 2. If no client thread_id but exists in session state -> reuse it
        # 3. If no client thread_id and not in session state -> generate new (first conversation)
        if incoming_thread_id:
            state["thread_id"] = incoming_thread_id
            print(f"[run_workflow] Using client-provided thread_id: {incoming_thread_id}")
        elif not state.get("thread_id"):
            # Check if thread_id exists in saved session state (not first conversation)
            if session_id:
                loaded_state = await get_plan_execute(session_id)
                if loaded_state and loaded_state.get("thread_id"):
                    saved_thread_id = loaded_state.get("thread_id")
                    state["thread_id"] = saved_thread_id
                    print(f"[run_workflow] Reusing thread_id from session state: {saved_thread_id}")
            # If still no thread_id, will be generated by log_chat_history_agent (first conversation)
        
        state.setdefault("answer", None)
        state.setdefault("answer_confidence", None)
        state.setdefault("sources", None)
        state.setdefault("final_answer", None)
        state.setdefault("answer_summary", None)
        state.setdefault("answer_quality_score", None)
        state.setdefault("response", "")
        state.setdefault("user_id", incoming_user_id)  # Ensure user_id is always in state
        state.setdefault("user_name", incoming_user_name)  # Ensure user_name is always in state
        # thread_id is handled explicitly above - will be client-provided or generated by planner_agent
        
        plan = state.get("plan")
        # If plan is a string (single step), convert to list
        if isinstance(plan, str):
            plan = [plan]
        state["plan"] = plan
        try:
            async for event in self.workflow.astream(state, stream_mode="values", config={"recursion_limit": 50}):
                # Use current_step for step tracking
                current_step = event.get("current_step")
                if not current_step:
                    # Fallback: try to infer from plan or previous step
                    if plan and len(plan) > 0:
                        current_step = plan[0]
                    else:
                        current_step = None
                
                # Update past_steps in the event
                if current_step:
                    event_past_steps = event.get("past_steps", [])
                    if current_step not in event_past_steps:
                        event_past_steps.append(current_step)
                    event["past_steps"] = event_past_steps
                
                # Ensure current_step is set in the event
                if current_step:
                    event["current_step"] = current_step
                
                if session_id:
                    await set_plan_execute(session_id, event)
                yield event
        except GraphRecursionError:
            # Handle recursion limit error gracefully
            error_event = {
                "current_step": "error",
                "final_answer": "I apologize, but I encountered a processing limit while trying to answer your question. This might be due to the complexity of the query or insufficient information in my knowledge base. Please try rephrasing your question or asking about a different topic.",
                "answer_summary": "Recursion limit exceeded - providing fallback response",
                "answer_quality_score": 0.0,
                "doc_urls": [],
                "citation_map": {},
                "past_steps": state.get("past_steps", [])
            }
            if session_id:
                await set_plan_execute(session_id, error_event)
            yield error_event
