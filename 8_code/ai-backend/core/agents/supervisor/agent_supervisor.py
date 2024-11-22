from core.agents.state.chatbot_state import ChatBotState
from loguru import logger
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from core.utils.utils_llm import create_anthropic_llm_client, create_gemini_llm_client
from core.env import PROJECT_ID, LOCATION, GEMINI_FLASH
from datetime import datetime
from langchain_core.messages import trim_messages
from typing import Literal
from langchain_core.messages import HumanMessage

def supervisor(state: ChatBotState):
    """Key routing node to determine the intent of the customer's message.

    Directly updates the state with the next node to route to, under the "last_route" key.
    """
    logger.info("Entering router node.")

    class QueryHandler(Enum):
        ORDER_TEAM = "Order"
        PRODUCT_TEAM = "Product"
        UNKNOWN = "Unknown"
        FINISH = "Finish"

    class MessageIntentResult(BaseModel):
        reasoning: str = Field(description="The reasoning for the selected intent.")
        query_handler: QueryHandler
    
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.

    -- Role --
    You are a customer service supervisor tasked with managing a conversation between the customer and the most appropriate agent.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are responsible for routing the customer service request to the most appropriate agent, based on their intent.
    - The possible teams you can route to are:
        - Order: Customer is seeking information about their order.
        - Product: Customer is seeking information about products.
        - Finish: Customer has no further questions and the conversation is complete.
        - Unknown: The customer's message is not clear or does not match any of the available options.
    - You will respond with a structured output containing your reasoning for the selected team, and the team that should handle the request.
    - Consider the entire conversation history when determining the intent of the customer's message.

    -- Examples --

    Customer: "I'm having trouble with my order. Can you help me?"
    reasoning: "The customer is seeking information about their order, so we should route to the order team."
    query_handler: "Order"

    Customer: "What is the difference between the Samsung Galaxy S21 and the iPhone 12?"
    reasoning: "The customer is asking about the difference between two specific products, so we should route to the product team."
    query_handler: "Product"

    Customer: "I notice you have mobile phones and digital cameras. For someone interested in photography, would you recommend the Sony Xperia XA2 Ultra or the Pentax K-1 camera? Please explain the pros and cons of each for photography.?"
    reasoning: "The customer is asking about the pros and cons of two specific products, so we should route to the product team."
    query_handler: "Product"

    Customer: "I see there are some Sony TVs in your catalogue. Can you compare the features and prices between the Sony KD75XF8596BU and other TV models you have?"
    reasoning: "The customer is asking about the features and prices of two specific products, so we should route to the product team."
    query_handler: "Product"

    Customer: "Looking at the ratings distribution across different product categories, which category would you recommend for the most reliable purchases based on customer satisfaction?"
    reasoning: "The customer is asking about the ratings distribution across different product categories, so we should route to the product team."
    query_handler: "Product"

    Customer: "Can you tell me more about the product I ordered?"
    reasoning: "The customer is asking about the details of a product, so we should route to the product team."
    query_handler: "Product"
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Invoke the LLM, forcing the output to be a structured output via tool calling
    gemini_model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name=GEMINI_FLASH)
    # Clean the messages by removing trailing "." which can cause issues in an edge case
    state['messages'] = [m if not (isinstance(m, HumanMessage) and m.content.endswith(".")) else HumanMessage(content=m.content[:-1]) for m in state['messages']]

    trimmer = trim_messages(
        max_tokens=250,
        strategy="last",
        token_counter=len, # not compatible with anthropic
        include_system=True,
    )
    chain = prompt | trimmer | gemini_model.with_structured_output(MessageIntentResult, include_raw=True)

    response = chain.invoke({"messages": state['messages']})
    return {"last_route": response['parsed'].query_handler.value}


def supervisor_output_router(state: ChatBotState) -> Literal["order_inquiry_agent", "fallback", "exit", "product_supervisor"]:
    """Router node to determine the next node to route to based on the supervisor's response."""
    last_route = state['last_route']
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_route == "Order":
        return "order_inquiry_agent"
    elif last_route == "Product":
        return "product_supervisor"
    elif last_route == "Finish":
        return "exit"
    else:   
        return "fallback"
