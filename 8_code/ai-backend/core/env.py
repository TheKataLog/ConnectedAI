import os
from dotenv import load_dotenv
from loguru import logger

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
# Use absolute path to ensure .env file is found
from pathlib import Path

root_dir = Path(__file__).parent.parent
env_path = root_dir / "local" / "envs" / f".env.{ENVIRONMENT}"

if env_path.exists():
    logger.info(f"Loaded environment variables from {env_path}")
    load_dotenv(env_path)
else:
    # raise FileNotFoundError(f"Environment file not found at {env_path}")
    logger.warning(f"Environment file not found at {env_path}")

# environment-specific variables
PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
MONGODB_ATLAS_CLUSTER_URI = os.environ["MONGODB_ATLAS_CLUSTER_URI"]

SERVICE_API_KEY = os.environ.get("SERVICE_API_KEY")
TRACK_LLM = os.environ.get("TRACK_LLM") == "True"
JWS_SECRET_KEY = os.environ.get("JWS_SECRET_KEY")

LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

DEFAULT_GOOGLE_MODEL = os.environ.get("DEFAULT_GOOGLE_MODEL", "gemini-1.5-flash")
SERVER_PORT= int(os.environ.get("SERVER_PORT", 8000))

# constants across environments
GEMINI_PRO_FAMILY = "gemini-1.5-pro"
GEMINI_PRO = "gemini-1.5-pro-002"
GEMINI_FLASH_FAMILY = "gemini-1.5-pro"
GEMINI_FLASH = "gemini-1.5-flash-002"

# Data paths
RAW_ORDER_DATA_PATH = "data/synthetic-orders-data.csv"
RAW_PRODUCT_DATA_PATH = "data/synthetic-product-data.csv"
PROCESSED_ORDER_DATA_PATH = "data/synthetic-orders-data-processed.csv"
PROCESSED_PRODUCT_DATA_PATH = "data/synthetic-product-data-processed.csv"
PRODUCT_VECTOR_INDEX_NAME = "product_vector_index"
PRODUCT_FULLTEXT_SEARCH_INDEX_NAME = "product_fulltext_search_index"

# test only
LANGCHAIN_ENDPOINT = os.environ.get("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.environ.get("LANGCHAIN_PROJECT")
