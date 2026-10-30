import streamlit as st

message_history = []
{'role':'user','content':'Hi'}
{'role':'assistant','content':'Hi'}

user_input = st.chat_input('Type here')

if user_input:

  # first add the message to message_history
  message_history.append({'role':'user','content':user_input})
  with st.chat_message('user'):
    st.text(user_input)

  # first add the message tot message_history
  message_history.append({'role':'assistant','content':user_input})
  with st.chat_message('assistant'):
    st.text(user_input)
