from core.agents.state.chatbot_state import ChatBotState
from loguru import logger
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.utils.utils_llm import create_anthropic_llm_client, create_gemini_llm_client, create_openai_llm_client
from core.env import PROJECT_ID, LOCATION, GEMINI_FLASH
from langchain_core.messages import trim_messages
from typing import Literal
from core.agents.product_agent.product_agent_tools import retrieve_product_details
from core.agents.order_agent.order_agent_tools import get_product_details
from core.utils.utils_tools import create_tool_node_with_fallback
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage

product_attributes_agent_tool_node = create_tool_node_with_fallback([retrieve_product_details, get_product_details])

def product_attributes_agent(state: ChatBotState, config: RunnableConfig):
    """Product attributes agent."""
    logger.info("Entering product attributes agent.")
    
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n

    -- Role --
    You are a friendly customer service agent tasked answering questions about products.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are only responsible for answering questions about products.
    - You will determine the most applicable product lookup query from the customer's messages. Think step by step to determine what the customer is inquiring about.
        - If the customer is asking about a specific Product ID, use the get_product_details tool to retrieve the details of the specific Product ID.
        - Else, use the retrieve_product_details tool to retrieve the details of the product the customer is inquiring about.
        - If you cannot determine the query, you should ask the customer to clarify their query.
    - Based on the product details, you should provide a friendly and purely factual answer to the customer's question, using only the product details.
    - End your response with a sign off, such as "Let me know if you have any other questions."
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

    trimmer = trim_messages(
        max_tokens=250,
        strategy="last",
        token_counter=len, # not compatible with anthropic
        include_system=True,
    )

    model = model.bind_tools([retrieve_product_details, get_product_details])
    chain = prompt | trimmer | model
    response = chain.invoke({"messages": state['messages']})
    return {"messages": [response]}

def product_attributes_agent_output_router(state: ChatBotState) -> Literal["ask_human", "product_attributes_agent_tool_node"]:
    """Router node to determine the next node to route to based on the product agent's response.
    
    If a tool call was made, then we route to the "tool_node" node to fetch the information.
    Otherwise, we route to the "ask_human" node to return the response to the customer, or ask a follow up question.
    """
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        if last_message.tool_calls[0].get("name") == "retrieve_product_details":
            return "product_attributes_agent_tool_node"
        elif last_message.tool_calls[0].get("name") == "get_product_details":
            return "product_attributes_agent_tool_node"
    return "ask_human"
