# backend.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv
import os 
import sqlite3
import requests

load_dotenv()

# ==================================
# 1. LLM
# ==================================
llm = ChatOpenAI()

# ==================================
# 2. Tools
# ==================================
# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage.
    """
    # Load the key from environment variables
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        return {"error": "ALPHAVANTAGE_API_KEY not set in environment."}

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    return r.json()


tools = [search_tool, get_stock_price, calculator]
llm_with_tools = llm.bind_tools(tools)

# ==================================
# 3. State
# ==================================
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ==================================
# 4. Nodes
# ==================================
'''def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}'''

# Make sure this import is at the top of backend.py
from langchain_core.runnables import RunnableConfig

# ... (rest of your backend code) ...

# ===================================
# 4. Nodes
# ===================================

def chat_node(state: ChatState, config: RunnableConfig): # <--- CHANGE 1
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    
    # Get thread_id from config, not state
    thread_id = config.get("configurable", {}).get("thread_id") # <--- CHANGE 2
    
    # Now, generate the response *after* getting the thread_id
    response = llm_with_tools.invoke(messages)
    
    # If this is the first user message for this thread → generate title
    if thread_id:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS thread_titles (thread_id TEXT PRIMARY KEY, title TEXT)"
        )
        cur.execute("SELECT title FROM thread_titles WHERE thread_id=?", (str(thread_id),)) # Good idea to cast to str
        row = cur.fetchone()

        if not row:  # title not yet created for this thread
            # Pass the full context (user message + AI response) for a better title
            title = generate_chat_title(messages + [response]) 
            save_thread_title(str(thread_id), title) # Good idea to cast to str

    return {"messages": [response]}



tool_node = ToolNode(tools)

# ===================================
# 5. Checkpointer
# ===================================
conn = sqlite3.connect(database="chatbotdemo.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# ===================================
# 6. Graph
# ===================================
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# ===========================
# 7. Helper
# ===========================
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)

# ============================================================
# 8. Title Generation for Threads
# ============================================================

def generate_chat_title(messages):
    """Generate a short, descriptive title for the chat."""
    # Combine only the first user message for context
    user_msg = next((m.content for m in messages if isinstance(m, HumanMessage)), "")
    if not user_msg.strip():
        return "New Conversation"
    
    prompt = f"Generate a short, capitalized title (max 6 words) that summarizes this message:\n\n{user_msg}\n\nTitle:"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        title = response.content.strip().replace('"', "")
        # Ensure fallback in case model responds weirdly
        return title if title else "New Conversation"
    except Exception as e:
        print("Title generation failed:", e)
        return "New Conversation"



def save_thread_title(thread_id: str, title: str):
    """Save title in SQLite metadata table (persisted)."""
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS thread_titles (thread_id TEXT PRIMARY KEY, title TEXT)"
        )
        conn.execute(
            "INSERT OR REPLACE INTO thread_titles (thread_id, title) VALUES (?, ?)",
            (str(thread_id), title),
        )
        conn.commit()
    except Exception as e:
        print("Failed to save title:", e)


def get_thread_title(thread_id: str) -> str:
    """Retrieve stored title (or fallback)."""
    try:
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS thread_titles (thread_id TEXT PRIMARY KEY, title TEXT)"
        )
        cur.execute("SELECT title FROM thread_titles WHERE thread_id=?", (str(thread_id),))
        row = cur.fetchone()
        if row:
            return row[0]
        return str(thread_id)
    except Exception:
        return str(thread_id)
