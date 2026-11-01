import streamlit as st
from langGraph_backend import chatbot
from langchain.messages import HumanMessage
import uuid

# ----------------- utility function-----------

def generate_thread_id():
  thread_id = uuid.uuid4()
  return str(thread_id)

def generate_chat_title(user_input):
    """
    Generate a short title from the first user message.
    No additional LLM API call is required.
    """
    title = " ".join(user_input.strip().split())

    if len(title) > 35:
        title = title[:35].rsplit(" ", 1)[0] + "..."

    return title or "New Chat"

# this function will add all the thread-id in list chat_threads
def add_thread(thread_id):
  if thread_id not in st.session_state['chat_threads']:
    st.session_state['chat_threads'].append(thread_id)

  if thread_id not in st.session_state["chat_titles"]:
        st.session_state["chat_titles"][thread_id] = "New Chat"

def reset_chat():
  thread_id = generate_thread_id()
  st.session_state['thread_id'] = thread_id
  # add_thread(st.session_state['thread_id'])
  st.session_state['message_history'] = []
  add_thread(thread_id)



def load_conversation(thread_id):
  # return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']
  config = {
    "configurable": {
    "thread_id": thread_id
    }
   }

  state = chatbot.get_state(config)

  # Handle a thread with no saved state.
  if not state or not state.values:
    return []

  # Safely retrieve messages.
  return state.values.get("messages", [])



# -----------------Session Setup --------------

if 'message_history' not in st.session_state:
  st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
  st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
  st.session_state['chat_threads'] = []

if "chat_titles" not in st.session_state:
    st.session_state["chat_titles"] = {}

add_thread(st.session_state['thread_id'])



# ------------------Sidebar UI-----------------

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button('New Chat'):
  reset_chat()
  st.rerun()

st.sidebar.header("My conversation")

# this will show all the thread_id in sidebar
for thread_id in st.session_state['chat_threads'][::-1]:

   # Display title instead of thread ID
  title = st.session_state["chat_titles"].get(
        thread_id, "New Chat"
    )
  
  if st.sidebar.button(title,key=f"chat_{thread_id}",use_container_width=True):
    st.session_state['thread_id'] = thread_id
    messages = load_conversation(thread_id)

    temp_messages = []

    for msg in messages:
      if isinstance(msg,HumanMessage):
        role = 'user'
      else:
        role="assistant"
      temp_messages.append({'role':role,'content':msg.content})

    st.session_state['message_history'] = temp_messages
    st.rerun()
      


#st.sidebar.text(st.session_state['thread_id'])

# -------------------Main UI ------------------

# loading the conversation history
st.title("Start your conversation")

# Display existing conversation history.

for message in st.session_state['message_history']:
  with st.chat_message(message['role']):
    st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

  thread_id = st.session_state["thread_id"]

    # Generate title only for the first message
  if not st.session_state["message_history"]:

        title = generate_chat_title(user_input)

        st.session_state["chat_titles"][thread_id] = title

# Display the user's message.
  with st.chat_message('user'):
    st.text(user_input)
  # first add the message to message_history
  st.session_state['message_history'].append({'role':'user','content':user_input})



  CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}


  with st.chat_message('assistant'):
    # st.text(ai_message)
    
    ai_message = st.write_stream(
      message_chunk.content for message_chunk, metadata in chatbot.stream(
        {'messages':[HumanMessage(content=user_input)]},
        config=CONFIG,
        stream_mode='messages'
      )
    )

    st.session_state['message_history'].append({'role':'assistant','content':ai_message})

    # Refresh sidebar to display the generated title
    st.rerun()



