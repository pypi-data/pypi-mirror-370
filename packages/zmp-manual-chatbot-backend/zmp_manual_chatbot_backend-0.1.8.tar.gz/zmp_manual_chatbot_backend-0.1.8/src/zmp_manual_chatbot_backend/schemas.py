from pydantic import BaseModel
from typing import Any, Dict, List, Optional, TypedDict, Protocol
from langchain_core.messages import AnyMessage



class Message(BaseModel):
    """
    Represents a message in the chat history.
    """
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """
    Represents a chat request with session management.
    
    Note: session_id is passed as a query parameter, not in the request body.
    """
    question: str
    chat_history: List[Message] = []
    image_url: Optional[str] = None
    thread_id: Optional[str] = None  # Optional thread_id from client for conversation continuity



class ContextChunk(BaseModel):
    id: str
    content: str
    doc_url: str | None = None
    score: float | None = None
    # Add more fields as needed


class ChatResponse(BaseModel):
    answer: str
    context: List[ContextChunk]
    query: str
    thread_id: str  # Mandatory thread_id for client to use in following requests


class ThreadInfo(BaseModel):
    """
    Represents a thread with its ID and title.
    """
    thread_id: str
    thread_title: str


class ThreadsListResponse(BaseModel):
    """
    Response for listing user threads.
    """
    user_id: str
    threads: List[ThreadInfo]


class ChatRecord(BaseModel):
    """
    Represents a single chat record in a thread conversation.
    """
    user_id: str
    thread_id: str
    query: str
    response: str
    doc_urls: List[str]
    citation_map: Dict[str, Any]
    timestamp: str


class ThreadConversationResponse(BaseModel):
    """
    Response for getting thread conversation history.
    """
    user_id: str
    thread_id: str
    records: List[ChatRecord]


class PlanExecute(TypedDict, total=False):
    """
    Represents the state at each step of the plan execution pipeline.

    Attributes:
        current_step (str): The current state or status of the execution.
        query (str): The original user query.
        anonymized_query (str): The anonymized version of the query (entities replaced with variables).
        rewritten_query (Optional[str]): The rewritten version of the query for retrieval (if available).
        query_to_retrieve_or_answer (str): The query to be used for retrieval or answering.
        plan (List[str]): The current plan as a list of steps to execute.
        past_steps (List[str]): List of steps that have already been executed.
        mapping (dict): Mapping of anonymized variables to original named entities.
        current_context (str): The current context used for answering or retrieval.
        aggregated_context (str): The accumulated context from previous steps.
        tool (str): The tool or method used for the current step (e.g., retrieval, answer).
        retrieve_context_result (Optional[Any]): Results from knowledge base search.
        chat_history_result (Optional[Any]): Results from chat history search.
        session_dialogue (Optional[list[AnyMessage]]): Session-specific dialogue history for follow-up questions.
        answer (Optional[str]): The generated answer from the answer agent.
        answer_confidence (Optional[float]): Confidence score for the generated answer.
        sources (Optional[List[str]]): List of sources used for answer generation.
        final_answer (Optional[str]): The comprehensive final answer synthesized from all information.
        answer_summary (Optional[str]): Summary of the answer generation process.
        answer_quality_score (Optional[float]): Overall quality score for the final answer.
        response (str): The response or output generated at this step.
        language (Optional[str]): The language of the query (optional, now handled by LLM)
        doc_urls (Optional[List[str]]): List of document URLs used as references for the answer.
        citation_map (Optional[Dict[str, Any]]): Mapping from citation number to citation metadata (solution, doc_url, page_no, page_image_url, etc.).
        thread_id (Optional[str]): Persistent thread identifier for conversation continuity across sessions.
        user_id (Optional[str]): Authenticated user identifier extracted from JWT token.
        user_name (Optional[str]): User name extracted from JWT token.
    """
    current_step: str
    query: str
    anonymized_query: str
    rewritten_query: Optional[str]
    query_to_retrieve_or_answer: str
    plan: List[str]
    past_steps: List[str]
    mapping: Dict[str, str]
    current_context: str
    aggregated_context: str
    tool: str
    retrieve_context_result: Optional[Any]
    chat_history_result: Optional[Any]
    session_dialogue: Optional[list[AnyMessage]]
    answer: Optional[str]
    answer_confidence: Optional[float]
    sources: Optional[List[str]]
    final_answer: Optional[str]
    answer_summary: Optional[str]
    answer_quality_score: Optional[float]
    response: str
    language: Optional[str]  # The language of the query (optional, now handled by LLM)
    doc_urls: Optional[List[str]]
    citation_map: Optional[Dict[str, Any]]
    thread_id: Optional[str]  # Persistent thread identifier for conversation continuity
    user_id: Optional[str]  # Authenticated user identifier extracted from JWT token
    user_name: Optional[str]  # User name extracted from JWT token


class AsyncAgentProtocol(Protocol):
    async def __call__(self, state: PlanExecute) -> PlanExecute:
        ...
