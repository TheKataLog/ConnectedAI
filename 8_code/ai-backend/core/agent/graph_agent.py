from core.agent.base_agent import BaseAgent
from core.agents.agent_graph import app


class GraphAgent(BaseAgent):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.order = 0
        self.llm_app = app
        self.agent_config = config

    async def get_session_response(self, session_id, message, input_config={}):
        result = await app.ainvoke(
            {"messages": [("user", message)]},
            {**input_config},
        )
        return result['messages'][-1].content

    async def get_session_response_stream(self, session_id, message, input_config={}):
        async for event in app.astream_events({"messages": [("user", message)]}, config=input_config, version="v2"):
            kind = event.get("event")
            if kind == 'on_chat_model_stream':
                result = extract_text(event["data"]["chunk"].content)
                if len(result) > 0:
                    yield result

def extract_text(response):
    if isinstance(response, str):
        return response
    elif isinstance(response, list):
        if len(response) == 0:
            return ""
        elif isinstance(response[0], dict) and 'text' in response[0]:
            return response[0]['text']
    return ""