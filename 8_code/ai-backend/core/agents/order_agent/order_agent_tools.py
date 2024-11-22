from typing import List, Dict
from core.mongodb.utils_mongodb import get_mongodb_collection
from core.env import MONGODB_ATLAS_CLUSTER_URI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from pprint import pformat
from loguru import logger
order_mongodb_collection = get_mongodb_collection(MONGODB_ATLAS_CLUSTER_URI, "connectedai", "katas_order_data")
parent_product_mongodb_collection = get_mongodb_collection(MONGODB_ATLAS_CLUSTER_URI, "connectedai", "katas_parent_product_data")
class OrderIDSchema(BaseModel):
    order_id: int = Field(description="The ID of the order in question.")

@tool(args_schema=OrderIDSchema)
def get_order_details(order_id: int) -> List[Dict]:
    """
    Get product details for a specific order ID from MongoDB.
    
    Args:
        order_id: The ID of the order to look up
        
    Returns:
        List of product details associated with the order ID
    """
    logger.info(f"Using get_order_details tool to get products in order: {order_id}")
    order_details = order_mongodb_collection.find({"OrderID": order_id})
    order_details_string = ""
    for i in order_details:
        order_details_string += pformat(i)
        order_details_string += "\n"
    return order_details_string

class CustomerIDSchema(BaseModel):
    customer_id: int = Field(description="The ID of the customer in question.")

@tool(args_schema=CustomerIDSchema)
def get_customer_orders(customer_id: int) -> str:
    """
    Get all orders for a specific customer from MongoDB.
    
    Args:
        customer_id: The ID of the customer to look up

    Returns:
        List of orders associated with the customer ID
    """
    logger.info(f"Using get_customer_orders tool to get orders for customer: {customer_id}")
    customer_orders = order_mongodb_collection.find({"CustomerID": customer_id})
    customer_orders_string = ""
    for i in customer_orders:
        customer_orders_string += pformat(i)
        customer_orders_string += "\n\n"
    return customer_orders_string

class ProductIDSchema(BaseModel):
    product_id: int = Field(description="The ID of the product in question.")

@tool(args_schema=ProductIDSchema)
def get_product_details(product_id: int) -> str:
    """
    Get details for a specific product from MongoDB.
    
    Args:
        product_id: The ID of the product to look up

    Returns:
        Details of the product
    """
    logger.info(f"Using get_product_details tool to get details for product: {product_id}")
    product_details = parent_product_mongodb_collection.find({"Product ID": product_id})
    product_details_string = ""
    for i in product_details:
        product_details_string += pformat(i)
        product_details_string += "\n\n"
    return product_details_string
