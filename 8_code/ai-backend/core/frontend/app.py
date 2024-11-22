import os
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import asyncio
from core.frontend.astream_events_handler import invoke_graph
import uuid
st.title("ConnectedAI - ShopWise Shopping Assistant")
# Capture user input from chat input
prompt = st.chat_input()

# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [AIMessage(content="How can I help you?")]
if "config" not in st.session_state:
    thread_id = str(uuid.uuid4())
    st.session_state["config"] = {
        "configurable": {
            "customer_id": "1234567890",
            "thread_id": thread_id,
        }
    }
# Loop through all messages in the session state and render them as a chat on every st.refresh mech
for msg in st.session_state.messages:
    # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
    # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

# Handle user input if provided
if prompt:
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        # create a placeholder container for streaming and any other events to visually render here
        placeholder = st.container()
        response = asyncio.run(invoke_graph(st.session_state.messages, placeholder, st.session_state.config))
        st.session_state.messages.append(response)
