from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import sqlite3
load_dotenv()

class ChatBotState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

CONFIG={"configurable":{"thread_id":"1"}}
graph=StateGraph(ChatBotState)
model=ChatGoogleGenerativeAI(model='gemini-2.5-pro',temperature=0.2)
def chat_state(state:ChatBotState):
    result=model.invoke(state['messages'])
    return {'messages':[result]}


conn=sqlite3.connect("chatbot.db",check_same_thread=False)

checkpointer=SqliteSaver(conn=conn)
graph.add_node("chat_state",chat_state)
graph.add_edge(START,"chat_state")
graph.add_edge("chat_state",END)

workflow=graph.compile(checkpointer=checkpointer)
def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        id=checkpoint.config['configurable']['thread_id']
        all_threads.add(id)
    return list(all_threads)

