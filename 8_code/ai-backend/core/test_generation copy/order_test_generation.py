from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from core.utils.utils_llm import create_llm_client
from langchain_core.prompts import PromptTemplate

def order_test_set_generation(
        sample_question: str, 
        n_questions: int,
        project_id: str,
        location: str,
        order_data_df: pd.DataFrame):
    """
    Generate a test set for an order data question.

    Args:
        sample_question (str): An example question to generate the test set.
        n_questions (int): The number of questions to generate.
        order_data_df (pd.DataFrame): The order data.
        product_data_df (pd.DataFrame): The product data.

    Returns:
        pd.DataFrame: A dataframe with the test set.
    """
    class TestQuestion(BaseModel):
        """
        A question and evolution type for the test set.
        The Order ID MUST be kept anonymously as XXX in the question.
        """
        question: str
        evolution_type: str

    class TestSet(BaseModel):
        f"""
        List of 10 test questions.
        """
        questions: List[TestQuestion]

    ORDER_HISTORY_PROMPT = """You are an expert quality assurance agent.
    You are given an example question. 
    Your task is to generate a set of questions that are similar to the example question to create a test set for a chatbot.

    Example question: {example_question}
    """

    question_list = []
    context_ground_truth_list = []

    while len(question_list) < n_questions:
        prompt = PromptTemplate(template=ORDER_HISTORY_PROMPT, input_variables=["example_question"])
        chat_model = create_llm_client(model_name="gemini-1.5-pro-002", project_id=project_id, location=location)
        chain = prompt | chat_model.with_structured_output(TestSet, include_raw=True)
        result = chain.invoke({"example_question": sample_question})
        # Prepare the question list for the test set
        question_list.extend([q.question for q in result['parsed'].questions])
        # Replace XXX with a sampled customer id from the order data
        sampled_order_ids = order_data_df['OrderID'].unique()
        np.random.shuffle(sampled_order_ids)
        sampled_order_ids = sampled_order_ids[0:len(question_list)]
        question_list = [q.replace("XXX", str(sampled_order_id)) for q, sampled_order_id in zip(question_list, sampled_order_ids)]

        # Prepare the ground truth context for the test set
        for id in sampled_order_ids:
            order_dict = {}
            order_dict["orders"] = order_data_df[order_data_df['OrderID'] == id].to_dict(orient="records")
            context_ground_truth_list.extend([order_dict])

    df = pd.DataFrame({"question": question_list[0:n_questions], "context_ground_truth": context_ground_truth_list[0:n_questions]})

    return df

