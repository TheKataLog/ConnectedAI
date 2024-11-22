from typing import Annotated, Optional, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END, add_messages

class ChatBotState(TypedDict):
    customer_id: str
    order_id: Optional[str]
    customer_context: Optional[str]
    product_context: Optional[str]
    messages: Annotated[list[AnyMessage], add_messages]
    last_route: Optional[str]

