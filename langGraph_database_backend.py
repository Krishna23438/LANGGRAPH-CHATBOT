
import sqlite3

from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv


# ----------------- Load Environment -----------------

load_dotenv()


# ----------------- Initialize LLM -----------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7
)


# ----------------- Define State -----------------

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ----------------- Define Chat Node -----------------

def chat_node(state: ChatState):

    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


# ----------------- SQLite Database -----------------

connection = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)


# ----------------- Checkpointer -----------------

checkpointer = SqliteSaver(conn=connection)

# Create LangGraph checkpoint tables
checkpointer.setup()


# ----------------- Conversation Titles Table -----------------

connection.execute("""
    CREATE TABLE IF NOT EXISTS chat_titles (
        thread_id TEXT PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

connection.commit()


# ----------------- Build LangGraph -----------------

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


# ----------------- Compile Graph -----------------

chatbot = graph.compile(
    checkpointer=checkpointer
)


# ----------------- Save Conversation Title -----------------

def save_chat_title(thread_id: str, title: str):

    connection.execute(
        """
        INSERT OR REPLACE INTO chat_titles (thread_id, title)
        VALUES (?, ?)
        """,
        (thread_id, title)
    )

    connection.commit()


# ----------------- Retrieve All Conversation Titles -----------------

def retrieve_chat_titles():

    cursor = connection.execute(
        "SELECT thread_id, title FROM chat_titles"
    )

    return dict(cursor.fetchall())


# ----------------- Retrieve All Thread IDs -----------------

def retrieve_all_threads():

    all_threads = set()

    for checkpoint in checkpointer.list(None):

        thread_id = checkpoint.config["configurable"]["thread_id"]

        all_threads.add(thread_id)

    return list(all_threads)
