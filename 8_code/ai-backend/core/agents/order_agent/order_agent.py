from core.agents.state.chatbot_state import ChatBotState
from loguru import logger
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.utils.utils_llm import create_anthropic_llm_client, create_gemini_llm_client, create_openai_llm_client
from core.env import PROJECT_ID, LOCATION, GEMINI_FLASH
from langchain_core.messages import trim_messages
from typing import Literal
from core.agents.order_agent.order_agent_tools import get_order_details, get_customer_orders, get_product_details
from core.utils.utils_tools import create_tool_node_with_fallback
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage, ToolMessage
import re

order_agent_tool_node = create_tool_node_with_fallback([get_order_details, get_customer_orders, get_product_details])

def order_inquiry_agent(state: ChatBotState, config: RunnableConfig):
    """Order inquiry agent."""
    logger.info("Entering order inquiry agent.")
    
    customer_id: int = int(config["configurable"].get("customer_id", -1))

    customer_id_str = f"Customer ID {str(customer_id)}" if customer_id != -1 else "Guest"

    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n

    -- Role --
    You are a friendly customer service agent tasked answering questions about customer orders.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are only responsible for answering questions about orders.
    - You will determine the most applicable OrderID or CustomerID based on the customer's messages with you.
        - The customer is logged in as {customer_id_str}.
        - You can use the get_order_details tool to retrieve the details of the order based on an OrderID, which should be found in the customer's messages.
        - You can use the get_customer_orders tool to retrieve the details of the customer's orders based on their CustomerID, unless they are a guest.
        - You can use the get_product_details tool to retrieve the details of the product based on a ProductID, which is found in the OrderID.
        - If you cannot determine the ID, carefully check the conversation history for a previously mentioned ID.
            - If no such ID is found, you should ask the customer to provide the necessary ID.
        - If the ID is invalid, you should ask the customer to provide the correct ID.
    - Based on the order details, you should provide a friendly and purely factual answer to the customer's question, using only the order details.
        - All prices are in USD ($).
    - End your response with a sign off, such as "Let me know if you have any other questions."

    -- Example -- 
    "Based on the order details, I can see that your order (ID: 1927) for a Bosch Serie 4 KIL22VF30G integrated fridge is not eligible for return. 
    The order was shipped on October 25th, 2024, and our system indicates that it's marked as non-returnable.
    Please let me know if you have any other questions!"
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Get the model name from the config
    model_name = config["configurable"].get("model", "claude-3-5-sonnet-v2@20241022")


    logger.warning(f"Using model: {model_name}")
    if "claude" in model_name:
        model = create_anthropic_llm_client(project_id=PROJECT_ID, model_name=model_name)
    elif "gemini" in model_name:
        model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name=model_name)
        # Clean the messages by removing trailing "." which can cause issues in an edge case
        state['messages'] = [m if not (isinstance(m, HumanMessage) and m.content.endswith(".")) else HumanMessage(content=m.content[:-1]) for m in state['messages']]
    elif "gpt" in model_name:
        model = create_openai_llm_client(model_name=model_name)

    # If a tool call is made, then we need to check if the customer_id matches the returned customer_id
    for i, message in enumerate(state['messages']):
        if isinstance(message, ToolMessage):
            pattern = r"'CustomerID':\s*(\d+)"
            match = re.search(pattern, message.content)
            if match:
                customer_id_from_tool = int(match.group(1))
                if customer_id_from_tool != customer_id:
                    logger.warning(f"Customer ID mismatch at message {i}")
                    state['messages'][i] = ToolMessage(content=f"Error: The Customer ID from the tool call does not match the logged in customer ID {customer_id}. Inform the customer that they are logged in as {customer_id_str}, and the provided OrderID was not from their account.",
                                                       tool_call_id=message.tool_call_id)



    trimmer = trim_messages(
        max_tokens=250,
        strategy="last",
        token_counter=len, # not compatible with anthropic
        include_system=True,
    )

    model = model.bind_tools([get_order_details, get_customer_orders, get_product_details])
    chain = prompt | trimmer | model
    response = chain.invoke({"messages": state['messages']})
    return {"messages": [response]}

def order_agent_output_router(state: ChatBotState) -> Literal["ask_human", "order_agent_tool_node"]:
    """Router node to determine the next node to route to based on the order agent's response.
    
    If a tool call was made, then we route to the "tool_node" node to fetch the information.
    Otherwise, we route to the "ask_human" node to return the response to the customer, or ask a follow up question.
    """
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        if last_message.tool_calls[0].get("name") == "get_order_details":
            return "order_agent_tool_node"
        if last_message.tool_calls[0].get("name") == "get_customer_orders":
            return "order_agent_tool_node"
        if last_message.tool_calls[0].get("name") == "get_product_details":
            return "order_agent_tool_node"
    return "ask_human"
