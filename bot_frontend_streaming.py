import streamlit as st
from langchain_core.messages import HumanMessage
from bot_backend import chatbot
import time,random
import uuid
# *****************************************************************************************************************
# ******************************* Utilities ***********************************************************************
# *****************************************************************************************************************
def generate_thread_id():
    thread_id=uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':thread_id}}).values['messages']

# **************************************************************************************************************************************************
# ****************************** Session Setup *****************************************************************************************************
# **************************************************************************************************************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


# *************************************************************************************************************************************************************
# **************************************************** Main UI ************************************************************************************************
# *************************************************************************************************************************************************************

st.sidebar.title("🤖 LangGraph Chatbot")
if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.header('My Conversation History')
for threads in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(threads)):
        msg=load_conversation(threads)
        temp_messages=[]
        for message in msg:
            if(isinstance(message , HumanMessage)):
                role='user'
            else:
                role = 'assistant'
            temp_messages.append({'role':role,'content':message.content})
        st.session_state['message_history']=temp_messages


# ************************************************************************************************************************************************************
# ****************************************** Display previous messages ***************************************************************************************
# ************************************************************************************************************************************************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])


user_input = st.chat_input("Type here")
if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.write(user_input)
   

    
    with st.chat_message('assistant'):
        def slow_stream():
            for message_chunk,metadata in chatbot.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            ):
                yield message_chunk.content
                time.sleep(random.uniform(0.02,0.07))
        ai_message = st.write_stream(slow_stream())
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})