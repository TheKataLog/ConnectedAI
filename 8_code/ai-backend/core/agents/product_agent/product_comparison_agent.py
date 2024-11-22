from core.agents.state.chatbot_state import ChatBotState
from loguru import logger
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.utils.utils_llm import create_anthropic_llm_client, create_gemini_llm_client, create_openai_llm_client
from core.env import PROJECT_ID, LOCATION, GEMINI_FLASH
from langchain_core.messages import trim_messages
from typing import Literal
from core.agents.product_agent.product_agent_tools import retrieve_product_details, compare_products, recommend_similar_products
from core.utils.utils_tools import create_tool_node_with_fallback
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import HumanMessage
product_comparison_agent_tool_node = create_tool_node_with_fallback([retrieve_product_details, compare_products, recommend_similar_products])

def product_comparison_agent(state: ChatBotState, config: RunnableConfig):
    """Product comparison agent."""
    logger.info("Entering product comparison agent.")
    
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n

    -- Role --
    You are a friendly customer service agent tasked answering questions about comparing products.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are only responsible for answering questions about comparing products.
    - You will determine the most applicable product lookup queries based on the customer's messages
        - First, you should determine each product that the customer has identified.
        - If the customer is asking to compare specific products and has provided the names, you should use the compare_products tool.
        - If the customer is asking to find similar products and has provided the name of a specific product, you should use the recommend_similar_products tool.
        - Otherwise, if no specific product names are provided or no useful results are found, you should use the retrieve_product_details tool multiple times each time to retrieve the details of a given product.
            - Each time search for a product's details, you must inform the customer what you are doing and why to keep them engaged.
        - Once you have the details of all the products, you should compare the products based on the customer's question.
    - Based on the product details, you should provide a friendly and purely factual answer to the customer's question, using only the product details.
        - All prices are in USD ($).
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

    model = model.bind_tools([retrieve_product_details, compare_products, recommend_similar_products])
    chain = prompt | trimmer | model
    response = chain.invoke({"messages": state['messages']})
    return {"messages": [response]}

def product_comparison_agent_output_router(state: ChatBotState) -> Literal["ask_human", "product_comparison_agent_tool_node"]:
    """Router node to determine the next node to route to based on the product agent's response.
    
    If a tool call was made, then we route to the "tool_node" node to fetch the information.
    Otherwise, we route to the "ask_human" node to return the response to the customer, or ask a follow up question.
    """
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        if last_message.tool_calls[0].get("name") == "retrieve_product_details":
            return "product_comparison_agent_tool_node"
        elif last_message.tool_calls[0].get("name") == "compare_products":
            return "product_comparison_agent_tool_node"
        elif last_message.tool_calls[0].get("name") == "recommend_similar_products":
            return "product_comparison_agent_tool_node"
    return "ask_human"
