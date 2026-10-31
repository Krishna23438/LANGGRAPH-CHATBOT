
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

from langchain_groq import ChatGroq
from dotenv import load_dotenv

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

checkpointer = InMemorySaver()

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


# Compile graph

chatbot = graph.compile(
    checkpointer=checkpointer
)
