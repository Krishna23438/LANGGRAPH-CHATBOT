
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import sqlite3

load_dotenv()


# Initialize LLM

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7
)


# Define State

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Define chatbot node

def chat_node(state: ChatState):

    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


# Build graph

connection = sqlite3.connect(database='chatbot.db',check_same_thread=False)

# checkpinter
checkpointer = SqliteSaver(conn=connection)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


# Compile graph

chatbot = graph.compile(
    checkpointer=checkpointer
)

def retrieve_all_threads():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config["configurable"]['thread_id'])


    return list(all_thread)

# Create table for conversation titles

connection.execute("""
    CREATE TABLE IF NOT EXISTS chat_titles (
        thread_id TEXT PRIMARY KEY,
        title TEXT
    )
""")

connection.commit()

def save_chat_title(thread_id, title):

    connection.execute(
        """
        INSERT OR REPLACE INTO chat_titles (thread_id, title)
        VALUES (?, ?)
        """,
        (thread_id, title)
    )

    connection.commit()


def retrieve_chat_titles():

    cursor = connection.execute(
        "SELECT thread_id, title FROM chat_titles"
    )

    return dict(cursor.fetchall())