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

def product_supervisor(state: ChatBotState):
    """Key routing node to determine the intent of the customer's message.

    Directly updates the state with the next node to route to, under the "last_route" key.
    """
    logger.info("Entering product supervisor node.")

    class ProductQueryHandler(Enum):
        COMPARISON = "Comparison"
        ATTRIBUTES = "Attributes"
        STATISTICS = "Statistics"

    class MessageIntentResult(BaseModel):
        reasoning: str = Field(description="The reasoning for the selected intent.")
        query_handler: ProductQueryHandler
    
    system_prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n

    -- Role --
    You are a customer service supervisor tasked with managing a conversation between the customer and the most appropriate product service agent.

    -- Company Information --
    ShopWise Solutions is an innovative and fast-growing e-commerce company based in Austin, Texas, USA. 
    Our online platform hosts a wide range of consumer products, spanning electronics, apparel, home goods, and much more. 
    ShopWise Solutions has built a reputation for exceptional customer experience, streamlined order fulfillment, and a diverse catalog of quality products.

    -- Instructions --
    - You are responsible for routing the customer service request to the most appropriate agent, based on their intent.
    - The possible teams you can route to are:
        - Comparison: Customer is seeking information about product comparisons, such as "what is the difference between product A and product B?"
        - Attributes: Customer is seeking information a specific product and it's attributes.
        - Statistics: Customer is seeking information pertaining to a category of products, such as price ranges for categories, rating distributions, etc.
    - You will respond with a structured output containing your reasoning for the selected team, and the team that should handle the request.
    - Consider the entire conversation history when determining the intent of the customer's message.

    -- Product Categories --
    The following are the product categories available on our platform: 
        - Fridges
        - Freezers
        - Fridge Freezers
        - TVs
        - Mobile Phones
        - Digital Cameras
        - Dishwashers
        - CPUs
        - Washing Machines
        - Microwaves

    -- Examples --

    Customer: "What is the difference between the Samsung Galaxy S21 and the iPhone 12?"
    reasoning: "The customer is asking about the difference between two specific products, so we should route to the comparison team."  
    query_handler: "Comparison"

    Customer: "What is the price range for fridges?"
    reasoning: "The customer is asking about the price range (an aggregated metric) for a category of products, so we should route to the statistics team."  
    query_handler: "Statistics"

    Customer: "What is the price of the Samsung Galaxy S21?"
    reasoning: "The customer is asking about the price of a specific product, so we should route to the attributes team."  
    query_handler: "Attributes"

    Customer: "I notice you have mobile phones and digital cameras. For someone interested in photography, would you recommend the Sony Xperia XA2 Ultra or the Pentax K-1 camera? Please explain the pros and cons of each for photography.?"
    reasoning: "The customer is asking about the pros and cons of two specific products, so we should route to the comparison team."  
    query_handler: "Comparison"

    Customer: "I see there are some Sony TVs in your catalogue. Can you compare the features and prices between the Sony KD75XF8596BU and other TV models you have?"
    reasoning: "The customer is asking about the features and prices of two specific products, so we should route to the comparison team."  
    query_handler: "Comparison"

    Customer: "Looking at the ratings distribution across different product categories, which category would you recommend for the most reliable purchases based on customer satisfaction?"
    reasoning: "The customer is asking about the ratings distribution across different product categories, so we should route to the statistics team."  
    query_handler: "Statistics"

    Customer: "Based on the stock quantities and prices shown in your inventory, which TV models offer the best value for money while still being readily available?"
    reasoning: "The customer is asking for a recommendation for a product (TVs) based on a criterion (best value for money and availability), so we should route to the attributes team."  
    query_handler: "Attributes"

    Customer: "I'm looking for a laptop under $1,000 with at least 16GB RAM."
    reasoning: "The customer is asking for a recommendation for a product (laptop) based on a criterion (price and RAM), so we should route to the attributes team."  
    query_handler: "Attributes"

    Customer: "Is the Liebherr CUfr 3311 available in red?"
    reasoning: "The customer is asking about the availability of a specific product in a specific color, so we should route to the attributes team."  
    query_handler: "Attributes"

    Customer: "Can you recommend a smartphone with a good camera and tell me if it's compatible with wireless charging?"
    reasoning: "The customer is asking for a recommendation for a product (smartphone) based on a criterion (good camera and wireless charging), so we should route to the attributes team."  
    query_handler: "Attributes"
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


def product_supervisor_output_router(state: ChatBotState) -> Literal["product_comparison_agent", "product_attributes_agent", "product_statistics_agent", "fallback"]:
    """Router node to determine the next node to route to based on the supervisor's response."""
    last_route = state['last_route']
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_route == "Comparison":
        return "product_comparison_agent"
    elif last_route == "Attributes":
        return "product_attributes_agent"
    elif last_route == "Statistics":
        return "product_statistics_agent"
    else:   
        return "fallback"
