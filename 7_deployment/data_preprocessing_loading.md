# Data Preprocessing and Loading

## 1. Data Preprocessing

The data preprocessing is done in the `preprocessing/preprocess_order_data.py` and `preprocessing/preprocess_product_data.py` scripts.
- The `preprocess_order_data.py` script is used to preprocess the order data.
    - It simply cleans the column names before saving back to a csv file.
- The `preprocess_product_data.py` script is used to preprocess the product data.
    - It uses a LLM to clean the product names and descriptions, enhancing the data quality for hybrid retrieval.
- The processed data is saved to the `data` directory.

## 2. Data Loading

The data loading is done in the `data_loading/load_order_data.py` and `data_loading/load_product_data.py` scripts.
- The data is loaded into a MongoDB Atlas cluster, the connection string for which is defined in the `core/locals/envs/.env.dev` file.
- These scripts handle the creation of the collections, insertion of the data, and the creation of the indexes.
