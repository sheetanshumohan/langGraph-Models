import streamlit as st
from langchain_core.messages import HumanMessage
from backend import workflow, retrieve_all_threads
import uuid

############################### UTILITY FUNCTIONS ################################################################
def generate_new_thread():
    return uuid.uuid4()

def generate_chat_title(message: str) -> str:
    return " ".join(message.split()[:5]) + "...." if message else "New Chat"

def add_thread(thread_id):
    if thread_id not in st.session_state['list_of_ids']:
        st.session_state['list_of_ids'].append(thread_id)

def get_chats_messages(thread_id):
    return workflow.get_state(
        config={"configurable": {"thread_id": thread_id}}
    ).values['messages']

def reset_chat():
    thread_id = generate_new_thread()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

##################################### SESSION STATE ############################################################

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_new_thread()

if 'list_of_ids' not in st.session_state:
    st.session_state['list_of_ids'] = retrieve_all_threads()

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}   # <-- store titles here

add_thread(st.session_state['thread_id'])

########################################### SIDEBAR FUNCTIONALITY ################################################

CONFIG = {"configurable": {"thread_id": st.session_state['thread_id']}}

st.sidebar.title("Langgraph Chatbot")

if st.sidebar.button("New Conversation"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['list_of_ids'][::-1]:
    title = st.session_state['chat_titles'].get(thread_id, str(thread_id))  # fallback to ID if no title yet
    if st.sidebar.button(title, key=f"btn_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        messages = get_chats_messages(thread_id)
        temp_messages = []
        for message in messages:
            role = 'user' if isinstance(message, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': message.content})
        st.session_state['message_history'] = temp_messages

####################################### MESSAGE SHOWING #########################################################

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type Here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    # ✅ If it's the first message in this thread, create a title
    if st.session_state['thread_id'] not in st.session_state['chat_titles']:
        st.session_state['chat_titles'][st.session_state['thread_id']] = generate_chat_title(user_input)

    with st.chat_message('user'):
        st.text(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in workflow.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )
        st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
