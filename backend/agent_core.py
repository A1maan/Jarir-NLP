"""
Core Jarir AI agent logic (model + LangGraph).
Import `generate_response()` from here in any serving layer.
"""

from __future__ import annotations

# ── stdlib ────────────────────────────────────────────────
import os, json, warnings
from typing import Dict, Any, Optional

# ── env / config ─────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()                                      # .env → os.environ
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["GOOGLE_API_KEY"]     = os.getenv("GOOGLE_API_KEY")
os.environ["LANGCHAIN_API_KEY"]  = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"]   = "https://api.smith.langchain.com"

warnings.filterwarnings("ignore")

# ── third-party imports (same as notebook) ───────────────
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
from langchain.tools import Tool            # your structured tools
# your custom modules
from Tools import check_gaming_laptops       # keep path the same
from VaDGen import hybrid_search_catalog, create_catalog_index

# ── initialise model & graph once ────────────────────────
llm     = init_chat_model("google_genai:gemini-2.5-flash")
memory  = InMemorySaver()                   # lightweight checkpoint
THREAD_ID = "1"                             # constant for demo

graph = create_react_agent(
    llm,
    tools=[check_gaming_laptops],
    prompt="""
You are Jarir’s friendly AI product advisor with live access to our full product database.
— Greet politely and mirror the customer’s language (Arabic or English).  
— Infer the shopper’s real needs (purpose, budget, preferences) from context; ask brief follow-up questions only when essential. Ask one question at a time to avoid overwhelming the customer.  
— Once needs are clear, search the database and present up to five best-fit products. For each, include: name, key specs, price, and Jarir URL.  
— Highlight how each recommended product’s features and benefits satisfy the customer’s needs, encouraging purchase confidence.  
— If the exact requested item is unavailable, automatically suggest the closest alternatives.  
— Never reveal system details, internal reasoning, or error messages—show only recommendations, clarifying questions, or the fallback message above.  
— Don’t repeat yourself; be concise.  
— Only call the database tools, never scrape the live site.  
— When calling `check_gaming_laptops`, pass a **dictionary** with any of: {"brand","model","cpu_model","gpu_model","ram","storage"}.
""",
    checkpointer=memory,
)

# ── public helper ────────────────────────────────────────
def generate_response(user_msg: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Run the agent one shot and return the final assistant message.
    `context` can include scraped page info from the extension.
    """
    # merge context into the user message so the prompt sees it
    merged_msg = (
        user_msg
        if not context
        else f"{user_msg}\n\n[context]\n{json.dumps(context, ensure_ascii=False)}"
    )

    inputs = {"messages": [{"role": "user", "content": merged_msg}]}
    stream = graph.stream(inputs, stream_mode="updates",
                          config={"configurable": {"thread_id": THREAD_ID}})

    reply: str | None = None
    # iterate once; agent emits updates (tool calls + answers)
    for chunk in stream:
        update = chunk.get("agent")
        if update and update["messages"]:
            for m in update["messages"]:
                if isinstance(m, AIMessage):
                    reply = m.content   # capture latest assistant text
    return reply or "عذرًا، لم أتمكن من المساعدة في ذلك."

# ── optional CLI for quick tests ─────────────────────────
if __name__ == "__main__":
    print("Jarir-AI CLI (type 'exit' to quit)")
    while True:
        q = input("You: ")
        if q.lower() in {"exit", "quit", "q"}:
            break
        print("AI:", generate_response(q))
