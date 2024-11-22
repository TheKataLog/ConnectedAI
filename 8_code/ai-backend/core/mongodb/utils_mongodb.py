from pymongo import MongoClient

def get_mongodb_collection(cluster_uri: str, db_name: str, collection_name: str):
    client = MongoClient(cluster_uri)
    return client[db_name][collection_name]

