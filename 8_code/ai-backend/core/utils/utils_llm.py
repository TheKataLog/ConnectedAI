from langchain_google_vertexai import HarmCategory, HarmBlockThreshold
from core.utils.chat_model import ChatVertexAIWX
from langchain_google_vertexai.model_garden import ChatAnthropicVertex
from vertexai.preview.tokenization import get_tokenizer_for_model
import random
from typing import List, Any, Tuple
from core.env import GEMINI_PRO, GEMINI_PRO_FAMILY, GEMINI_FLASH, GEMINI_FLASH_FAMILY
import asyncio
from langchain_core.rate_limiters import InMemoryRateLimiter
from pydantic import BaseModel
from loguru import logger
from typing import List
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    trim_messages,
)
tokenizer = get_tokenizer_for_model(GEMINI_PRO_FAMILY)
from langchain_openai import ChatOpenAI

def create_openai_llm_client(requests_per_second: int = 5, max_bucket_size: int = 5, model_name: str = "gpt-4o-mini") -> ChatOpenAI:
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=requests_per_second,  # Requests per second
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check,
        max_bucket_size=max_bucket_size,  # Controls the maximum burst size.
    )

    model = ChatOpenAI(
        rate_limiter=rate_limiter,
        model_name=model_name,
        temperature=0,
        top_p=0,
    )

    return model

def create_anthropic_llm_client(project_id: str, location: str = "us-east5", requests_per_second: int = 5, max_bucket_size: int = 5, model_name: str = "claude-3-5-sonnet-v2@20241022") -> ChatAnthropicVertex:
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=requests_per_second,  # Requests per second
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check,
        max_bucket_size=max_bucket_size,  # Controls the maximum burst size.
    )

    model = ChatAnthropicVertex(
        project_id=project_id,
        location=location,
        rate_limiter=rate_limiter,
        model_name=model_name,
        max_tokens=8000,
        temperature=0,
        top_p=0,
    )

    return model

def create_gemini_llm_client(project_id: str, location: str, requests_per_second: int = 5, max_bucket_size: int = 5, model_name: str = GEMINI_FLASH) -> ChatVertexAIWX:
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=requests_per_second,  # Requests per second
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check,
        max_bucket_size=max_bucket_size,  # Controls the maximum burst size.
    )
    safety_settings = {
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }

    model = ChatVertexAIWX(
        project_id=project_id,
        location=location,
        rate_limiter=rate_limiter,
        model_name=model_name,
        temperature=0,
        top_p=0,
        max_output_tokens=8192,
        streaming=False,
        safety_settings=safety_settings,
    )

    return model


def get_token_count(text: str) -> int:
    response = tokenizer.count_tokens(text)
    return response.total_tokens


def calculate_vertex_ai_cost(input_tokens: int, output_tokens: int) -> float:
    INPUT_PRICE_PER_MILLION_TOKENS = 0.075  # $0.075 per 1M input tokens
    OUTPUT_PRICE_PER_MILLION_TOKENS = 0.30  # $0.30 per 1M output tokens
    USD_TO_AUD_RATE = 1.5  # Fixed exchange rate for estimate

    input_cost = (input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION_TOKENS
    output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION_TOKENS

    total_cost_usd = input_cost + output_cost
    total_cost_aud = total_cost_usd * USD_TO_AUD_RATE

    return total_cost_aud


async def apply_chain_to_input(chain: Any, input: Any, default_model: BaseModel) -> Any:
    """
    Apply a chain to a single input asynchronously.

    Args:
        chain (Any): The chain to apply.
        input (Any): The input to process.

    Returns:
        Any: The result of applying the chain to the input.
    """
    try:
        answer = await chain.ainvoke(input=input, config={"max_concurrency": 10})
        return answer
    except Exception as e:
        logger.error(f"Error processing input: {input}. Error: {str(e)}")
        return default_model.get_default(input)


async def run_chain_on_inputs(
    chain: Any, inputs: List[Any], default_model: BaseModel
) -> Tuple[List[Any], float, int, int]:
    """
    Run a chain on a list of inputs asynchronously and estimate the cost.

    Args:
        chain (Any): The chain to run.
        inputs (List[Any]): The list of inputs to process.

    Returns:
        Tuple[List[Any], float, int, int]: A tuple containing:
            - The list of results
            - The estimated cost
            - The estimated input tokens
            - The estimated output tokens
    """
    tasks = [apply_chain_to_input(chain, input, default_model=default_model) for input in inputs]
    results = await asyncio.gather(*tasks)
    estimated_cost, est_input_tokens, est_output_tokens = estimate_cost_from_sample(
        inputs, results, chain
    )
    return results, estimated_cost, est_input_tokens, est_output_tokens


def estimate_cost_from_sample(
    inputs: List[Any], outputs: List[Any], chain: Any
) -> Tuple[float, int, int]:
    total_items = len(inputs)
    sample_size = min(100, total_items)  # Use 100 or all items if less than 100

    # Create indices for sampling
    indices = random.sample(range(total_items), sample_size)

    # Sample inputs and outputs
    sampled_inputs = [
        chain.get_prompts()[0].format(**inputs[i])
        for i in indices
    ]
    sampled_outputs = [outputs[i] for i in indices]

    # Get token counts for samples
    input_tokens = sum(get_token_count(str(input_)) for input_ in sampled_inputs)
    output_tokens = sum(get_token_count(str(output_)) for output_ in sampled_outputs)

    # Estimate total tokens
    estimated_input_tokens = (input_tokens / sample_size) * total_items
    estimated_output_tokens = (output_tokens / sample_size) * total_items

    # Calculate estimated cost
    estimated_cost = calculate_vertex_ai_cost(estimated_input_tokens, estimated_output_tokens)

    return estimated_cost, estimated_input_tokens, estimated_output_tokens

create_llm_client=create_gemini_llm_client