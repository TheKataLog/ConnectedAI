
from typing import Annotated

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from core.agent.base_agent import BaseAgent
from core.env import GOOGLE_API_KEY, DEFAULT_GOOGLE_MODEL

llm = ChatGoogleGenerativeAI(
    temperature=0.7,
    max_tokens=256,
    google_api_key=GOOGLE_API_KEY,
    model=DEFAULT_GOOGLE_MODEL  # Assuming "gemini-pro" is a valid model name
)

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

class GoogleFreeAgent(BaseAgent):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        self.graph_builder = StateGraph(State)
        self.graph_builder.add_node("chatbot", chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)
        self.graph = self.graph_builder.compile()

    def get_session(self,session_id):
        return self.sessions.get(session_id,[])

    async def get_session_response(self,session_id, message, input_config={}):
        actual_input = f'Response below question in maximum 3 sentences without using any emoji: {message}'
        result = await self.graph.ainvoke(
            {"messages": [("user", actual_input)]},
            config=input_config
        )
        return result['messages'][-1].content

    async def get_session_response_stream(self,session_id, message, input_config={}):
        # history=self.build_session_chat(session_id)
        actual_input = f'Response below question in maximum 3 sentences without using any emoji: {message}'
        async for event in self.graph.astream({"messages": ("user", actual_input)}, config=input_config):
            for value in event.values():
                # print("Assistant:", value["messages"][-1].content)
                yield value["messages"][-1].content

    def add_session_item(self,session_id, item):
        session=self.sessions.get(session_id,[])
        session.insert(0,item)
        # self.sessions[session_id]=session

    def build_session_chat(self,session_id):
        session = self.sessions.get(session_id, [])
        history=""
        for item in session:
            history=history+"User: "+item["user"]+"\n"
            history=history+"AI: " +item["AI"]+"\n"
        return history


