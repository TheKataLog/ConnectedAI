from loguru import logger
from core.env import RAW_ORDER_DATA_PATH, PROCESSED_ORDER_DATA_PATH
import pandas as pd

def preprocess_order_data(order_data_path: str, processed_order_data_path: str):
    """
    Preprocess the order data by removing whitespace from column names and saving to a CSV file.
    """
    order_data_df = pd.read_csv(order_data_path)
    order_data_df.columns = [i.strip() for i in order_data_df.columns]
    order_data_df.to_csv(processed_order_data_path, index=False)

if __name__ == "__main__":
    logger.info(f"Preprocessing order data from {RAW_ORDER_DATA_PATH} to {PROCESSED_ORDER_DATA_PATH}")
    preprocess_order_data(RAW_ORDER_DATA_PATH, PROCESSED_ORDER_DATA_PATH)
    logger.info(f"Order data preprocessed and saved to {PROCESSED_ORDER_DATA_PATH}")
