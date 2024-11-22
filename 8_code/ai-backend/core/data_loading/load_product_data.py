from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_google_vertexai import VertexAIEmbeddings
from core.mongodb.utils_mongodb import get_mongodb_collection
from core.env import MONGODB_ATLAS_CLUSTER_URI, PROJECT_ID, LOCATION, PROCESSED_PRODUCT_DATA_PATH, PRODUCT_VECTOR_INDEX_NAME, PRODUCT_FULLTEXT_SEARCH_INDEX_NAME
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.index import create_fulltext_search_index
from langchain_core.documents import Document
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from typing import List, Dict

def product_data_from_csv(csv_path: str) -> List[Document]:
    """
    Load and process product data from CSV into Langchain Document chunks.
    
    Returns:
        List of Document chunks with product metadata and descriptions
    """
    logger.info(f"Loading product data from {csv_path}")
    df = pd.read_csv(csv_path)
    # Cast the df to a list of dicts
    product_data = df.to_dict(orient="records")
    return product_data

def product_data_to_documents(product_data: List[Dict]) -> List[Document]:
    # Prepare Langchain Document objects
    metadata = [{k: v for k, v in i.items() if k != 'Enhanced Description'} for i in product_data]
    page_content = [i['Enhanced Description'] for i in product_data]
    documents = [Document(page_content=content, metadata=metadata) for content, metadata in zip(page_content, metadata)]
    return documents

def product_data_to_chunks(documents: List[Document]) -> List[Document]:
    """
    Split the documents into chunks - we keep individual sentences as chunks

    Args:
        documents: List of Document objects

    Returns:
        List of Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=64, chunk_overlap=0, separators=["\. [A-Z]"], keep_separator=True, is_separator_regex=True)
    chunks = text_splitter.split_documents(documents)
    for i in chunks:
        # Remove the first character if it's a period
        if i.page_content[0] == ".":
            i.page_content = i.page_content[1:].lstrip().rstrip(".")
    logger.info(f"Loaded {len(chunks)} product data chunks")
    return chunks

def product_data_to_mongodb(csv_path: str, mongodb_uri: str, db_name: str, collection_name: str):
    """
    Load product data into MongoDB and create an index.
    """
    product_data = product_data_from_csv(csv_path)
    product_mongodb_collection = get_mongodb_collection(mongodb_uri, db_name, collection_name)
    # Delete existing data in the collection
    product_mongodb_collection.delete_many({})
    _ = product_mongodb_collection.insert_many(product_data)
    logger.info(f"Inserted {len(product_data)} product data into MongoDB")

    # Check for index and create if not exists
    indexes = product_mongodb_collection.list_indexes()
    index_exists_cluster = any("Cluster ID" in index['name'] for index in indexes)
    index_exists_product = any("Product ID" in index['name'] for index in indexes)
    index_exists_price = any("Price" in index['name'] for index in indexes)
    index_exists_rating = any("Rating" in index['name'] for index in indexes)
    if not index_exists_cluster:
        _ = product_mongodb_collection.create_index("Cluster ID")
        logger.info("Created index on Cluster ID")
    if not index_exists_product:
        _ = product_mongodb_collection.create_index("Product ID")
        logger.info("Created index on Product ID")
    if not index_exists_price:
        _ = product_mongodb_collection.create_index("Price")
        logger.info("Created index on Price")
    if not index_exists_rating:
        _ = product_mongodb_collection.create_index("Rating")
        logger.info("Created index on Rating")
    
    logger.info(f"Product data loaded to MongoDB")
    return product_mongodb_collection

def product_data_to_vector_store(csv_path: str, mongodb_uri: str, db_name: str, collection_name: str):
    """
    Load product data into MongoDB Atlas Vector Search and create vector and fulltext search indexes.
    
    Args:
        mongodb_uri: MongoDB connection URI
        db_name: Name of the database
        collection_name: Name of the collection
        
    Returns:
        MongoDBAtlasVectorSearch: The configured vector store
    """
    product_data = product_data_from_csv(csv_path)
    documents = product_data_to_documents(product_data)
    chunks = product_data_to_chunks(documents)
    embeddings = VertexAIEmbeddings(model="textembedding-gecko@003", project=PROJECT_ID, location=LOCATION)

    product_mongodb_collection = get_mongodb_collection(mongodb_uri, db_name, collection_name)
    # Delete existing data in the collection
    logger.info(f"Deleting existing data in the collection")
    product_mongodb_collection.delete_many({})

    # Create the vector store
    vector_store = MongoDBAtlasVectorSearch(
        collection=product_mongodb_collection,
        embedding=embeddings,
        index_name=PRODUCT_VECTOR_INDEX_NAME,
        relevance_score_fn="cosine",
    )

    logger.info(f"Inserting {len(chunks)} product data chunks into the vector store")
    # Insert the product data into the vector store
    vector_store.add_documents(chunks)
    logger.info(f"Inserted {len(chunks)} product data chunks into the vector store")

    # Create the index
    # Check if the index already exists
    # Check if index exists by getting list of indexes from collection
    search_indexes = product_mongodb_collection.list_search_indexes()
    indexes = product_mongodb_collection.list_indexes()
    index_exists_fulltext = any(index['name'] == PRODUCT_FULLTEXT_SEARCH_INDEX_NAME for index in search_indexes)
    index_exists_vector = any(index['name'] == PRODUCT_VECTOR_INDEX_NAME for index in search_indexes)
    index_exists_price = any("Price" in index['name'] for index in indexes)
    index_exists_rating = any("Rating" in index['name'] for index in indexes)

    if not index_exists_vector:
        logger.info(f"Creating the vector search index")
        vector_store.create_vector_search_index(dimensions=768, filters = ["Price", "Rating", "Category"])
        logger.info(f"Vector search index created")

    if not index_exists_fulltext:
        logger.info(f"Creating the fulltext search index")
        # Use helper method to create the search index
        create_fulltext_search_index(
            collection = product_mongodb_collection,
            field = "Enhanced Description",
            index_name = PRODUCT_FULLTEXT_SEARCH_INDEX_NAME
        )
        logger.info(f"Fulltext search index created")

    if not index_exists_price:
        _ = product_mongodb_collection.create_index("Price")
        logger.info("Created index on Price")

    if not index_exists_rating:
        _ = product_mongodb_collection.create_index("Rating")
        logger.info("Created index on Rating")

    return vector_store

if __name__ == "__main__":
    _ = product_data_to_mongodb(
        PROCESSED_PRODUCT_DATA_PATH,
        MONGODB_ATLAS_CLUSTER_URI,
        "connectedai",
        "katas_parent_product_data"
    )

    _ = product_data_to_vector_store(
        PROCESSED_PRODUCT_DATA_PATH,
        MONGODB_ATLAS_CLUSTER_URI,
        "connectedai",
        "katas_product_data"
    )

