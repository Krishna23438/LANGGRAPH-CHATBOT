from langgraph.graph import StateGraph, START, END
from typing import TypedDict,Annotated
from langchain.messages import HumanMessage
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7
)

class ChatState(TypedDict):
  messages:Annotated[list[BaseMessage],add_messages]


def chat_node(state:ChatState):
  messages = state['messages']
  response = llm.invoke(messages)
  return {'messages':[response]}

# checkpointer
checkpointer = InMemorySaver()


graph = StateGraph(ChatState)

# Add node
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge("chat_node",END)

chatbot  = graph.compile(checkpointer=checkpointer)



