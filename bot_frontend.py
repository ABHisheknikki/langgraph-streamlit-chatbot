import streamlit as st
from langchain_core.messages import HumanMessage
from bot_backend import chatbot

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

st.title("🤖 AI Chatbot")

# Initialize chat history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

# Input box
user_input = st.chat_input("Type here")
if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.write(user_input)

    # Backend response
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message = response['messages'][-1].content
   

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.write(ai_message)
