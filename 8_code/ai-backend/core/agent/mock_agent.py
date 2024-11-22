# core/agent/mock_agent.py
import asyncio

from core.agent.base_agent import BaseAgent

class MockAgent(BaseAgent):
    def __init__(self, config, mock_data, **kwargs):
        super().__init__(config, **kwargs)
        self.order = 0
        self.mock_data = mock_data

    async def get_session_response(self, session_id, message, input_config={}):
        result = self.mock_data[self.order % len(self.mock_data)]
        self.order += 1
        return result["AI"]

    async def get_session_response_stream(self, session_id, message, delay=1, input_config={}):
        for i, result in enumerate(self.mock_data):
            yield result["AI"]
            if i < len(self.mock_data) - 1:
                await asyncio.sleep(delay)
