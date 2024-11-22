from core.env import PROJECT_ID, LOCATION
from pydantic import BaseModel, Field
import pandas as pd
from langchain.prompts import PromptTemplate
from core.utils.utils_llm import run_chain_on_inputs
from core.preprocessing.prompts import DESCRIPTION_ENRICHMENT_PROMPT, PRODUCT_NAME_ENRICHMENT_PROMPT
from core.utils.utils_llm import create_gemini_llm_client
import asyncio
from core.utils.chat_model import ChatVertexAIWX
from loguru import logger
from core.env import RAW_PRODUCT_DATA_PATH, PROCESSED_PRODUCT_DATA_PATH

async def enhance_product_names(product_data_df: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Enhance the product names by correcting spelling and grammar errors, and combining across multiple entries.
    Utilizes the product category and description to help with the name correction.

    Args:
        product_data_df (pd.DataFrame): The product data frame.
        chat_model (ChatVertexAIWX): The chat model to use for the name correction chain.

    Returns:
        pd.DataFrame: The product data frame with the enhanced product names.
    """
    logger.info("Enhancing product names...")
    logger.info(f"Product data frame shape: {product_data_df.shape}")

    class CorrectedProductName(BaseModel):
        """
        Corrected product name.
        """
        reasoning: str = Field(description="Reasoning about the corrections applied name.")
        product_name: str = Field(description="The corrected product name.")


    prompt = PromptTemplate(template=PRODUCT_NAME_ENRICHMENT_PROMPT, input_variables=["product_names", "product_category", "product_descriptions"])
    name_correction_chain = prompt | chat_model.with_structured_output(CorrectedProductName)

    name_correction_inputs = []
    cluster_id_list = []
    for id in product_data_df['Cluster ID'].unique():
        # Filter the dataframe for the current cluster
        cluster_df = product_data_df[product_data_df['Cluster ID'] == id]

        # Get the category, cluster label, price, description, and product name
        category_list = cluster_df['Category'].unique()
        assert len(category_list) == 1
        category = category_list[0]

        cluster_label = cluster_df['Cluster Label'].unique()
        assert len(cluster_label) == 1
        cluster_label = cluster_label[0]

        price_list = list(cluster_df['Price'].unique())
        description_list = list(cluster_df['Description'].unique())
        product_name_list = list(cluster_df['ProductName'].unique())

        # Collect all the inputs for the name correction chain
        name_correction_inputs.append({
            "product_names": product_name_list, 
            "product_category": category, 
            "product_descriptions": description_list
        })
        cluster_id_list.append(id)

    # Run the name correction chain asynchronously and update the product data frame
    results, estimated_cost, est_input_tokens, est_output_tokens = await run_chain_on_inputs(name_correction_chain, name_correction_inputs, CorrectedProductName)
    id_name_map = dict(zip(cluster_id_list, [i.product_name for i in results]))
    for id, name in id_name_map.items():
        product_data_df.loc[product_data_df['Cluster ID'] == id, 'Enhanced Product Name'] = name

    logger.info(f"Product data frame shape after enhancing product names: {product_data_df.shape}")
    logger.info(f"Estimated cost: ${estimated_cost} AUD")

    return product_data_df

async def enhance_product_descriptions(product_data_df: pd.DataFrame, chat_model: ChatVertexAIWX) -> pd.DataFrame:
    """
    Enhance the product descriptions by correcting spelling and grammar errors, and ensuring the description is fully formed.
    
    Args:
        product_data_df (pd.DataFrame): The product data frame.
        chat_model (ChatVertexAIWX): The chat model to use for the description correction chain.

    Returns:
        pd.DataFrame: The product data frame with the enhanced product descriptions.
    """
    logger.info("Enhancing product descriptions...")
    logger.info(f"Product data frame shape: {product_data_df.shape}")

    class FullyFormedSentences(BaseModel):
        """
        Fully formed description for the product.
        """
        fully_formed_description: str

    prompt = PromptTemplate(template=DESCRIPTION_ENRICHMENT_PROMPT, input_variables=["product_name", "product_category", "product_description"])
    chat_model = ChatVertexAIWX(model_name="gemini-1.5-pro-002", project_id=PROJECT_ID, location=LOCATION, temperature=0.0)
    description_chain = prompt | chat_model.with_structured_output(FullyFormedSentences)

    product_labels = list(product_data_df["Cluster Label"])
    product_categories = list(product_data_df["Category"])
    product_descriptions = list(product_data_df["Description"])

    description_inputs = []
    for i in range(len(product_labels)):
        description_inputs.append({
            "product_name": product_labels[i], 
            "product_category": product_categories[i], 
            "product_description": product_descriptions[i]
        })

    results, estimated_cost, est_input_tokens, est_output_tokens = await run_chain_on_inputs(description_chain, description_inputs, FullyFormedSentences)

    description_list = [i.fully_formed_description for i in results]
    product_data_df['Enhanced Description'] = description_list

    logger.info(f"Product data frame shape after enhancing product descriptions: {product_data_df.shape}")
    logger.info(f"Estimated cost: ${estimated_cost} AUD")

    return product_data_df


if __name__ == "__main__":
    # Prepare the product data
    logger.info(f"Preprocessing product data from {RAW_PRODUCT_DATA_PATH} to {PROCESSED_PRODUCT_DATA_PATH}")
    product_data_df = pd.read_csv(RAW_PRODUCT_DATA_PATH)
    product_data_df.columns = [i.strip() for i in product_data_df.columns]

    # Enhance the product names and descriptions
    chat_model = create_gemini_llm_client(project_id=PROJECT_ID, location=LOCATION, requests_per_second = 5, max_bucket_size = 5)
    product_data_df = asyncio.run(enhance_product_names(product_data_df, chat_model))
    product_data_df = asyncio.run(enhance_product_descriptions(product_data_df, chat_model))
    product_data_df.to_csv(PROCESSED_PRODUCT_DATA_PATH, index=False)
    logger.info(f"Product data preprocessed and saved to {PROCESSED_PRODUCT_DATA_PATH}")
