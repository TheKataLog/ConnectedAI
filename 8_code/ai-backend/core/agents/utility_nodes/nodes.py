from loguru import logger
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from core.agents.state.chatbot_state import ChatBotState
from langchain_core.tools import tool
from core.utils.utils_llm import create_anthropic_llm_client, create_gemini_llm_client
from core.env import PROJECT_ID, LOCATION, GEMINI_FLASH
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import trim_messages
from core.agents.order_agent.order_agent_tools import get_order_details

def fallback_node(state: ChatBotState): 
    """Fallback node to handle any customer message.""" 
    logger.info("Entering fallback node.")
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n

    -- Role --
    You are a friendly customer service agent tasked answering questions about customer orders.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are only responsible for responding to the customer's message, with a friendly answer indicating that you are unable to answer their question.
    - You will inform the customer that you can help them with questions about orders, or products.
    - You are not allowed to make any tool calls.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    gemini_model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name=GEMINI_FLASH)

    trimmer = trim_messages(
        max_tokens=250,
        strategy="last",
        token_counter=len, # not compatible with anthropic
        include_system=True,
    )
    gemini_model = gemini_model.bind_tools([get_order_details]) # Needs a tool to be bound if tools are in the messages
    chain = prompt | trimmer | gemini_model
    response = chain.invoke({"messages": state['messages']})
    return {"messages": [AIMessage(content=response.content)]}

def exit_node(state: ChatBotState): 
    """Exit node to handle any customer message.""" 
    logger.info("Entering exit node.")
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n

    -- Role --
    You are a friendly customer service agent tasked answering questions about customer orders.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are only responsible for thanking the customer for contacting ShopWise Solutions and wishing them a great day.
    - Include any relevant context such as the answer to the customer's question in your response to make it more engaging and human-like.
    - You are not allowed to make any tool calls.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    gemini_model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name=GEMINI_FLASH)

    trimmer = trim_messages(
        max_tokens=250,
        strategy="last",
        token_counter=len, # not compatible with anthropic
        include_system=True,
    )

    gemini_model = gemini_model.bind_tools([get_order_details]) # Needs a tool to be bound if tools are in the messages
    chain = prompt | trimmer | gemini_model
    response = chain.invoke({"messages": state['messages']})
    return {"messages": [AIMessage(content=response.content)]}

def ask_human_node(state: ChatBotState):
    pass
