import pandas as pd
import json
from core.mongodb.utils_mongodb import get_mongodb_collection
from core.env import MONGODB_ATLAS_CLUSTER_URI, PROCESSED_ORDER_DATA_PATH
from loguru import logger

def load_order_data_to_mongodb(mongodb_uri: str, db_name: str, collection_name: str, csv_path: str):
    """
    Load order data from CSV into MongoDB and create an index.
    
    Args:
        mongodb_uri: MongoDB connection URI
        db_name: Name of the database
        collection_name: Name of the collection
        csv_path: Path to the CSV file containing order data
    """
    logger.info(f"Loading order data from {csv_path} to MongoDB")
    # Get the collection
    order_mongodb_collection = get_mongodb_collection(mongodb_uri, db_name, collection_name)
    # Delete existing data in the collection
    order_mongodb_collection.delete_many({})
    
    # Preprocess into mongo friendly format
    df = pd.read_csv(csv_path)
    result = df.to_dict(orient="records")
    
    # Insert the order data into the MongoDB collection
    _ = order_mongodb_collection.insert_many(result)
    logger.info(f"Inserted {len(result)} order data into MongoDB")
    
    # Check for index and create if not exists
    indexes = order_mongodb_collection.list_indexes()
    index_exists = any("OrderID" in index['name'] for index in indexes)
    if not index_exists:
        # Create an index on the OrderID field for faster lookups
        _ = order_mongodb_collection.create_index("OrderID")
        logger.info("Created index on OrderID")

    logger.info(f"Order data loaded to MongoDB")
    return order_mongodb_collection


if __name__ == "__main__":
    order_mongodb_collection = load_order_data_to_mongodb(
        MONGODB_ATLAS_CLUSTER_URI,
        "connectedai",
        "katas_order_data",
        PROCESSED_ORDER_DATA_PATH
    )
