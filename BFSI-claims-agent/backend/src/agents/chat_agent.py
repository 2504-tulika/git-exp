from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from src.config.settings import settings
from src.exceptions.exceptions import AgentToolError
from src.utils.logger import get_logger

logger = get_logger(__name__)

CHAT_SYSTEM_PROMPT = """You are a claims assistant answering a customer's follow-up questions about ONE SPECIFIC CLAIM they already submitted.

Its facts -- policy, claim type, incident details, and the AI's original recommendation and rationale -- are given to you below as CLAIM CONTEXT. Answer using only that context. You do not have live access to re-run any checks, so if something isn't in the context, say you don't have that information rather than guessing.

CRITICAL: You do not re-decide this claim. Even if asked to approve it, deny it, or change its recommendation right now, decline -- explain that only the claims team can finalize a claim, and that your role here is to explain the existing review, not issue a new one. Never claim to have changed a claim's status or recommendation.

PRIVACY: Only ever discuss this one claim and this one customer's own information. You have no information about any other customer, and must never imply otherwise.

Be concise and warm. Cite specific facts (clauses, dates, amounts) rather than vague reassurance."""

MAX_HISTORY_MESSAGES = 12

_model = None
_graph = None


def _call_model(state):
    """The graph's only node: trim history, then ask the model to reply."""
    recent_messages = state["messages"][-MAX_HISTORY_MESSAGES:]
    response = _model.invoke(recent_messages)
    return {"messages": [response]}


def _build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", _call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    # MemorySaver is the "memory checkpointer" -- it stores each thread's
    # messages in memory, keyed by thread_id, so we don't have to.
    return builder.compile(checkpointer=MemorySaver())


def warm_up():
    """
    Create the chat model and graph, once. This is much lighter than the
    main agent's warm_up(): no MCP server subprocess to spawn, so it's
    fine to call this lazily on the first chat message instead of at
    app startup. A second call is a no-op if already warm.
    """
    global _model, _graph
    if _graph is not None:
        return
    _model = ChatGroq(model=settings.llm_model_name, temperature=0.2, api_key=settings.groq_api_key)
    _graph = _build_graph()
    logger.info("Chat agent warmed up")


def _thread_config(thread_id):
    return {"configurable": {"thread_id": thread_id}}


def thread_has_history(thread_id):
    """True if this thread already has at least one message saved."""
    warm_up()
    state = _graph.get_state(_thread_config(thread_id))
    return len(state.values.get("messages", [])) > 0


def send_chat_message(thread_id, claim_context_text, user_message):
    """
    Send one user message on a claim's chat thread and return the
    assistant's reply text.

    thread_id identifies the conversation -- the caller should build it as
    "{customer_id}:{claim_id}" so two customers' chats about a claim can
    never mix, even though claim_id is already unique on its own.

    claim_context_text is only turned into a system message the FIRST time
    this thread is used. After that, the checkpointer already remembers it
    as part of the thread's history, so sending it again would just
    duplicate it.
    """
    warm_up()

    new_messages = []
    if not thread_has_history(thread_id):
        new_messages.append(
            SystemMessage(content=f"{CHAT_SYSTEM_PROMPT}\n\nCLAIM CONTEXT:\n{claim_context_text}")
        )
    new_messages.append(HumanMessage(content=user_message))

    try:
        result = _graph.invoke({"messages": new_messages}, config=_thread_config(thread_id))
    except Exception as exc:
        logger.error(f"Chat model call failed for thread {thread_id}: {exc}")
        raise AgentToolError("The assistant is temporarily unavailable. Please try again.") from exc

    reply_message = result["messages"][-1]
    logger.info(f"Chat reply generated for thread {thread_id}")
    return reply_message.content