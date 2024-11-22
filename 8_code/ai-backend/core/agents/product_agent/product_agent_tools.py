from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_google_vertexai import VertexAIEmbeddings
from core.mongodb.utils_mongodb import get_mongodb_collection
from core.env import MONGODB_ATLAS_CLUSTER_URI, PROJECT_ID, LOCATION, PRODUCT_VECTOR_INDEX_NAME, PRODUCT_FULLTEXT_SEARCH_INDEX_NAME, GEMINI_FLASH
from langchain_mongodb import MongoDBAtlasVectorSearch
from loguru import logger
from typing import List, Dict, Union
from langchain_core.tools import tool
from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever 
from pydantic import BaseModel, Field
from core.utils.utils_llm import create_anthropic_llm_client, create_gemini_llm_client, run_chain_on_inputs
import asyncio
from langchain_core.prompts import PromptTemplate
from enum import Enum
import pprint
from core.agents.product_agent.product_mongo_pipelines import price_pipeline, rating_pipeline, stock_pipeline

parent_product_mongodb_collection = get_mongodb_collection(MONGODB_ATLAS_CLUSTER_URI, "connectedai", "katas_parent_product_data")
product_mongodb_collection = get_mongodb_collection(MONGODB_ATLAS_CLUSTER_URI, "connectedai", "katas_product_data")

embeddings = VertexAIEmbeddings(model="textembedding-gecko@003", project=PROJECT_ID, location=LOCATION)
vector_store = MongoDBAtlasVectorSearch(
    collection=product_mongodb_collection,
    embedding=embeddings,
    index_name=PRODUCT_VECTOR_INDEX_NAME,
    relevance_score_fn="cosine",
)

retriever = MongoDBAtlasHybridSearchRetriever(
    vectorstore = vector_store,
    search_index_name = PRODUCT_FULLTEXT_SEARCH_INDEX_NAME,
    top_k = 15,
    fulltext_penalty = 50,
    vector_penalty = 50
)

def retrieve_parent_product_details(product_id: Union[List[int], int]) -> List[Dict]:
    """
    Retrieve detailed product information for one or more product IDs from MongoDB.
    
    Use this tool when you need to look up specific products by their Product ID.
    Each product has attributes like name, description, price, etc.

    Args:
        product_id: Either a single product ID (integer) or a list of product IDs to look up.
                   Example: 12345 or [12345, 12346, 12347]
        
    Returns:
        A list of dictionaries containing product details for the requested product ID(s).
        Each dictionary contains product attributes like name, description, price, etc.
        The '_id' and 'embedding' fields are excluded from the results.

    Example:
        get_parent_product_details(12345)  # Returns details for product 12345
        get_parent_product_details([12345, 12346])  # Returns details for multiple products
    """
    logger.info(f"Retrieving parent product details for product ID: {product_id}")
    if isinstance(product_id, int):
        product_details = parent_product_mongodb_collection.find({"Product ID": product_id})
    else:
        product_details = parent_product_mongodb_collection.find({"Product ID": {"$in": product_id}})
        # $in returns the products in an arbitrary order, so we need to reorder them
        product_details = sorted(product_details, key=lambda x: product_id.index(x['Product ID']))
    product_details = [{k: v for k, v in i.items() if k not in ['_id', 'embedding']} for i in product_details]
    return product_details

@tool
def retrieve_cluster_details(cluster_id: Union[List[int], int]) -> List[Dict]:
    """
    Retrieve product details for products belonging to a specific cluster ID or list of cluster IDs from MongoDB.
    
    Use this tool when you need to find all products that belong to one or more product clusters.
    The cluster ID groups similar or related products together.

    Args:
        cluster_id: Either a single cluster ID (integer) or a list of cluster IDs to look up.
                   Example: 42 or [42, 43, 44]
        
    Returns:
        A list of dictionaries containing product details for all products in the specified cluster(s).
        Each dictionary contains product attributes like name, description, price, etc.
        The '_id' and 'embedding' fields are excluded from the results.

    Example:
        get_parent_cluster_details(42)  # Returns products in cluster 42
        get_parent_cluster_details([42, 43])  # Returns products in clusters 42 and 43
    """
    logger.info(f"Using retrieve_cluster_details tool to get products in cluster(s): {cluster_id}")
    if isinstance(cluster_id, int):
        cluster_details = parent_product_mongodb_collection.find({"Cluster ID": cluster_id})
    else:
        cluster_details = parent_product_mongodb_collection.find({"Cluster ID": {"$in": cluster_id}})
    cluster_details = [{k: v for k, v in i.items() if k not in ['_id', 'embedding']} for i in cluster_details]
    return cluster_details


class RankBy(Enum):
    RELEVANCE = "relevance"
    CHEAP = "cheap"
    EXPENSIVE = "expensive"
    HIGH_RATED = "high_rated"
    LOW_RATED = "low_rated"

class Category(Enum):
    FRIDGES = "Fridges"
    TVS = "TVs"
    MOBILE_PHONES = "Mobile Phones"
    DIGITAL_CAMERAS = "Digital Cameras"
    FRIDGE_FREEZERS = "Fridge Freezers"
    DISHWASHERS = "Dishwashers"
    CPUS = "CPUs"
    FREEZERS = "Freezers"
    WASHING_MACHINES = "Washing Machines"
    MICROWAVES = "Microwaves"

class RetrieveProductDetails(BaseModel):
    query: str = Field(description="A natural language search query describing what products to find. For example: 'red running shoes' or 'small portable speakers'")
    k: int = Field(default=5, description="The maximum number of unique products to return in the results. Increase this number if you need more options to compare.")
    rank_by: RankBy = Field(default="relevance", description="How to sort the results: 'relevance' for best match to query, 'cheap' for lowest price first, 'expensive' for highest price first, 'high_rated' for highest rated first, or 'low_rated' for lowest rated first.")
    category: Category = Field(default=None, description="The category of products to search for. For example: 'Fridges' or 'Mobile Phones'")
    price_limit: float = Field(default=None, description="The maximum price of products to search for. For example: 1000.00")
    rating_limit: float = Field(default=None, description="The minimum rating of products to search for. For example: 4.5")

@tool(args_schema=RetrieveProductDetails)
def retrieve_product_details(query: str, k: int = 5, rank_by: str = "relevance", category: str = None, price_limit: float = None, rating_limit: float = None) -> str:
    """
    Search for parent products using a natural language query and retrieve their details.
    Use this tool when you need to search for products based on keywords, descriptions, or other attributes.
    The search combines semantic similarity and keyword matching to find the most relevant products.
    The results are sorted by the rank_by parameter.
        
    Example:
        {"query": "phone with good battery life", "k": 5, "rank_by": "relevance", "category": "Mobile Phones", "price_limit": 1000.0, "rating_limit": None}
        Returns details for the 5 most relevant mobile phone products with good battery life, under $1000.00, with no limit on rating

        {"query": "phone with good battery life", "k": 5, "rank_by": "cheap", "category": "Mobile Phones", "price_limit": None, "rating_limit": 3}
        Returns details for the 5 cheapest mobile phone products with good battery life, with no limit on price, rated at least 3 stars
    """
    logger.info(f"Using retrieve_product_details tool to search for products: {query}")
    # ====================================================================================
    # Retrieve the product details - hybrid parent child retrieval
    # ====================================================================================
    # Increase the top_k of the child retriever to retrieve more products
    # To ensure we get k unique products
    retriever.top_k = k*10

    pre_filter = {}
    if category is not None:
        pre_filter["Category"] = category.value
    if price_limit is not None:
        pre_filter["Price"] = {"$lte": price_limit}
    if rating_limit is not None:
        pre_filter["Rating"] = {"$gte": rating_limit}
    retriever.pre_filter = pre_filter

    logger.info(f"Retrieving parent product details for query: {query}")
    results = retriever.invoke(query)

    # ====================================================================================
    # Rerank the results based on the rank_by parameter
    # ====================================================================================
    if rank_by == RankBy.CHEAP:
        results = sorted(results, key=lambda x: x.metadata['Price'])
    elif rank_by == RankBy.EXPENSIVE:
        results = sorted(results, key=lambda x: x.metadata['Price'], reverse=True)
    elif rank_by == RankBy.HIGH_RATED:
        results = sorted(results, key=lambda x: x.metadata['Rating'], reverse=True)
    elif rank_by == RankBy.LOW_RATED:
        results = sorted(results, key=lambda x: x.metadata['Rating'])
    elif rank_by == RankBy.RELEVANCE:
        results = sorted(results, key=lambda x: x.metadata['score'], reverse=True)

    # ====================================================================================
    # Get the parent product details
    # Keep 2x the number of products to ensure we get k unique products after aspect filtering
    # ====================================================================================
    products = []
    for i in results:
        if i.metadata['Product ID'] not in products:
            products.append(i.metadata['Product ID'])

    products = products[:k*2]
    product_details = retrieve_parent_product_details(product_id = products)

    # ====================================================================================
    # Aspect filtering - determine if the product matches the customer query
    # ====================================================================================
    aspect_summary_prompt = """
    You are an expert product manager working for a large online retailer.
    You are given a customer query, and some product details.
    Your task is to determine whether or not the product is a match for the customer query.
    You should return a boolean value, and a short explanation for your reasoning.

    Customer query: {query}
    Product details: {product_details}
    """

    prompt = PromptTemplate(template=aspect_summary_prompt, input_variables=["query", "product_details"])

    class ProductMatch(BaseModel):
        reasoning: str = Field(description="A short explanation for your reasoning.")
        is_match: bool = Field(description="Whether or not the product is a match for the customer query.")

    model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, model_name=GEMINI_FLASH)
    chain = prompt | model.with_structured_output(ProductMatch)

    # Prepare the chain inputs
    chain_inputs = [{"query":query, "product_details":product_detail} for product_detail in product_details]
    product_matches, _, _, _ = asyncio.run(run_chain_on_inputs(chain, chain_inputs, default_model=RetrieveProductDetails))
    product_details = [product_detail for product_detail, product_match in zip(product_details, product_matches) if product_match.is_match][:k]

    # ====================================================================================
    # Format the product details
    # ====================================================================================
    product_details_string = ""
    for i, product in enumerate(product_details):
        product_details_string += f"Product {i+1}:\n"
        product_details_string += f"Product Name: {product['Enhanced Product Name']}\n"
        product_details_string += f"Product Description: {product['Enhanced Description']}\n"
        product_details_string += f"Product Rating: {product['Rating']}\n"
        product_details_string += f"Product Price: {product['Price']}\n"
        product_details_string += f"Product Category: {product['Category']}\n"
        product_details_string += f"Product Stock Quantity: {product['StockQuantity']}\n"
        product_details_string += "\n"

    return product_details_string

def get_product_from_name(product_name: str) -> Dict:
    """
    Retrieves product details from MongoDB or hybrid search if not found.

    Args:
        product_name: The name of the product to look up. Can be partial name.

    Returns:
        A dictionary containing product details.
    """
    product = parent_product_mongodb_collection.find_one({"ProductName": {"$regex": f"^{product_name}.*", "$options": "i"}})
    if not product:
        product = retriever.invoke(product_name, k=1)[0]
        # Unpack the metadata
        product = product.metadata
        logger.info(f"Hybrid search fallback used to find product: {product}")

    if not product:
        raise ValueError(f"No product found matching: {product_name}")
    return product

class ProductNameList(BaseModel):
    product_names: List[str] = Field(description="A list of product names to compare")

@tool(args_schema=ProductNameList)
def compare_products(product_names: List[str]) -> List[Dict]:
    """Retrieves details for multiple products, using their names, from MongoDB to enable comparison.

    Args:
        product_names: A list of product names to look up and compare. Each name will be matched
                      against the start of product names in the database (case-insensitive).
                      Example: ["samsung fridge", "lg fridge"]

    Returns:
        A list of dictionaries containing details for each matched product, including:
        - name: Full product name
        - description: Detailed product description
        - price: Product price
        - category: Product category
        - rating: Customer rating (0-5)
        - stock_quantity: Current inventory level
    """
    logger.info(f"Using compare_products tool to compare products: {product_names}")
    if not product_names:
        raise ValueError("No product name configured.")
    
    # Execute 
    products = [get_product_from_name(name) for name in product_names]


    # Format the results
    results = []
    for product in products:
        if product:
            results.append(
                {
                    "name": product["ProductName"],
                    "description": product["Description"],
                    "price": product["Price"],
                    "category": product["Category"],
                    "rating": product["Rating"],
                    "stock_quantity": product["StockQuantity"],
                }
            )

    return results
class BaseProduct(BaseModel):
    product_name: str = Field(description="The name of a specific product to find similar items for recommendation.")
    k: int = Field(description="The number of similar products to return.", default=5)

@tool(args_schema=BaseProduct)
def recommend_similar_products(product_name: str, k: int = 5) -> List[Dict]:
    """Finds similar products based on category and price range of a specific product.

    This tool helps find products that are similar to a specific product by:
    1. Finding products in the same category
    2. Filtering for products within 80-150% of the original product's price range
    3. Sorting results by customer rating (highest first)

    Args:
        product_name: The name of the product to find similar items for. Can be partial name.
        k: The maximum number of similar products to return (default: 5)

    Returns:
        A list of dictionaries containing similar products, each with:
        - name: Product name
        - description: Detailed product description  
        - price: Product price
        - category: Product category
        - rating: Customer rating (0-5)
        - stock_quantity: Current inventory level
    """
    logger.info(f"Using recommend_similar_products tool to find similar products for product: {product_name}")
    if not product_name:
        raise ValueError("No product name configured.")

    # Find the matching products
    original_product = get_product_from_name(product_name)

    #Calculate the price variation
    # Calculate price bounds
    lower_bound = original_product["Price"] * 0.8
    upper_bound = original_product["Price"] * 1.5

    # Using category and price as the condition
    query = {
    "Category": original_product["Category"],
    "Price": {"$gte": lower_bound, "$lte": upper_bound}}
    

    # Find products in similar category
    similar_products = list(parent_product_mongodb_collection.find(query))
    # Order by rating
    similar_products = sorted(similar_products, key=lambda x: x["Rating"], reverse=True)

    # Format the results
    results = []
    for product in similar_products:
        results.append(
            {
                "name": product["ProductName"],
                "description": product["Enhanced Description"],
                "price": product["Price"],
                "category": product["Category"],
                "rating": product["Rating"],
                "stock_quantity": product["StockQuantity"],
            }
        )

    return results[:k]

class SummaryStatisticsField(Enum):
    PRICE = "Price"
    RATING = "Rating"
    STOCK = "Stock"
class CategorySchema(BaseModel):
    field: SummaryStatisticsField = Field(description="The field to get the summary statistics for, either 'Price' or 'Rating'.")

@tool(args_schema=CategorySchema)
def get_category_summary_statistics(field: SummaryStatisticsField) -> str:
    """
    Get the summary statistics for a specific field for each category in the product database.
    
    Args:
        field: The field to get the summary statistics for, either 'Price' or 'Rating'.
        
    Returns:
        A string containing the summary statistics for each category.
        The string is formatted as a table, with the category name in the first column, and the average value of the field in the second column.
    """
    pipeline = []
    if field == SummaryStatisticsField.PRICE:
        pipeline = price_pipeline
    elif field == SummaryStatisticsField.RATING:
        pipeline = rating_pipeline
    elif field == SummaryStatisticsField.STOCK:
        pipeline = stock_pipeline
    results = parent_product_mongodb_collection.aggregate(pipeline)
    summary_statistics_string = ""
    for i in results:
        summary_statistics_string += pprint.pformat(i)
        summary_statistics_string += "\n"
    return summary_statistics_string


if __name__ == "__main__":
    pass