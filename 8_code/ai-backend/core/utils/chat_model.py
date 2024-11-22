from langchain_core.runnables import Runnable, RunnablePassthrough
from typing import Optional, Union, Any, Dict, Type
from langchain_core.messages import BaseMessage
from langchain_google_vertexai.functions_utils import (
    _ToolConfigDict,
    _ToolChoiceType,
    _ToolsType,
    _format_to_gapic_tool,
)
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.language_models import LanguageModelInput
from langchain_google_vertexai.functions_utils import PydanticFunctionsOutputParser
from langchain_google_vertexai.chat_models import _get_tool_name
from operator import itemgetter
from pydantic import BaseModel, Field
from typing import List
from langchain_google_vertexai import ChatVertexAI

class ChatVertexAIWX(ChatVertexAI): 
    def with_structured_output(
        self,
        schema: Union[Dict, Type[BaseModel]],
        *,
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, Union[Dict, BaseModel]]:
        """Model wrapper that returns outputs formatted to match the given schema.

        Adapted from langchain_google_vertexai.chat_models.ChatVertexAI.with_structured_output
            - Replaced PydanticToolsParser (typically used for OpenAI tools) with PydanticFunctionsOutputParser
            - Removed JSON mode
        """  # noqa: E501

        if kwargs:
            raise ValueError(f"Received unsupported arguments {kwargs}")

        parser: OutputParserLike

        tool_name = _get_tool_name(schema)

        parser = PydanticFunctionsOutputParser(pydantic_schema=schema)

        tool_choice = tool_name if self._is_gemini_advanced else None

        llm = self.bind_tools([schema], tool_choice=tool_choice)

        if include_raw:
            parser_with_fallback = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | parser, parsing_error=lambda _: None
            ).with_fallbacks(
                [RunnablePassthrough.assign(parsed=lambda _: None)],
                exception_key="parsing_error",
            )
            return {"raw": llm} | parser_with_fallback
        else:
            return llm | parser
        
    def bind_tools(
        self,
        tools: _ToolsType,
        tool_config: Optional[_ToolConfigDict] = None,
        *,
        tool_choice: Optional[Union[_ToolChoiceType, bool]] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tool-like objects to this chat model.

        Assumes model is compatible with Vertex tool-calling API.

        Adapted from langchain_google_vertexai.chat_models.ChatVertexAI.bind_tools
            - Removed try-except, to avoid converting to OpenAI tools

        Args:
            tools: A list of tool definitions to bind to this chat model.
                Can be a pydantic model, callable, or BaseTool. Pydantic
                models, callables, and BaseTools will be automatically converted to
                their schema dictionary representation.
            **kwargs: Any additional parameters to pass to the
                :class:`~langchain.runnable.Runnable` constructor.
        """
        if tool_choice and tool_config:
            raise ValueError(
                "Must specify at most one of tool_choice and tool_config, received "
                f"both:\n\n{tool_choice=}\n\n{tool_config=}"
            )
        
        # ! Removed try-except, to avoid converting to OpenAI tools
        formatted_tools = [_format_to_gapic_tool(tools)]
        if tool_choice:
            kwargs["tool_choice"] = tool_choice
        elif tool_config:
            kwargs["tool_config"] = tool_config
        else:
            pass
        return self.bind(tools=formatted_tools, **kwargs)



if __name__ == "__main__":
    # Example usage
    class UserDetails(BaseModel):
        """
        Extract the name, age and friendliness from the message.
        Friendliness is a number between 0 and 100, higher is more friendly.
        If you don't know the name, do not return it.
        If you don't know the age, do not return it.
        If you don't know the siblings, do not return them.
        """
        friendliness: int
        name: str = Field(default="None")
        age: int = Field(default=-1)
        siblings: List[str] = Field(default=[])
    chat_model = ChatVertexAIWX(model_name="gemini-1.5-flash-002", project_id=PROJECT_ID, location=LOCATION)
    chat_model.with_structured_output(UserDetails, include_raw=True).invoke("test")

