class BaseAgent:
    def __init__(self, config, **kwargs):
        self.config = config
        self.sessions = {}

    def get_session(self,session_id):
        raise NotImplementedError

    async def get_session_response(self,session_id, message, input_config={}):
        raise NotImplementedError

    async def get_session_response_stream(self, session_id, message, input_config={}):
        raise NotImplementedError