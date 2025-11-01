from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph , START , END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage
from dotenv import load_dotenv
from typing import  Literal , TypedDict
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated,List

# **************************************************** Declare API-KEY **************************************************************
load_dotenv()

# **************************************************** MODEL Setup ******************************************************************

llm = ChatOpenAI()

class ChatState(TypedDict):
    messages : Annotated[List[BaseMessage] , add_messages]

def Chat_node(state : ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages' : [response]}

graph=StateGraph(ChatState)
checkpointer = MemorySaver()
graph.add_node('chat_node',Chat_node)
graph.add_edge(START , 'chat_node')
graph.add_edge('chat_node' , END)

chatbot = graph.compile(checkpointer = checkpointer)
