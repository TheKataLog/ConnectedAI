import jwt

from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect, WebSocketState

from core.agent.base_agent import BaseAgent
# from core.agent.gemini_agent import GeminiAgent
from core.agent.google_free_agent import GoogleFreeAgent
from core.agent.mock_agent import MockAgent
from core.env import SERVICE_API_KEY, TRACK_LLM, JWS_SECRET_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
from core.agent.graph_agent import GraphAgent
from fastapi import WebSocket
from langfuse.callback import CallbackHandler

# from mock_data import outputs

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional


class ChatItem(BaseModel):
    sessionId: str
    customerId: Optional[int] = None
    isAuthenticated: bool
    chatMessage: str

class JWSChatItem(BaseModel):
    token: str
    chatMessage: str

mock_outputs=[
    {"user":"Hello","AI":"How can I help you!"},
    {"user":"Hello","AI":"How can I help you 2!"},
    {"user":"Hello","AI":"How can I help you 3!"},
]

# agent = GeminiAgent(None)
# agent = GoogleFreeAgent(None)
graph_agent = GraphAgent({})
api_key = SERVICE_API_KEY
free_agent = GoogleFreeAgent({})
mock_agent = MockAgent({}, mock_data=mock_outputs)

def convert_jwt_to_chat_item(data: dict, secret: str, algorithms=["HS256"], **kwargs):
    token = data['token']
    token_data = jwt.decode(token, secret, algorithms, **kwargs)
    is_authenticated = token_data.get('role') == 'User'
    chat_item = ChatItem(
        sessionId=token_data['sessionId'],
        customerId=token_data.get('customerId', -1) if is_authenticated else -1,
        isAuthenticated=is_authenticated,
        chatMessage=data['chatMessage']
    )
    return chat_item


def get_config_by_message(message: ChatItem):
    result = {
        "configurable": {
            "customer_id": message.customerId if message.customerId else -1,
            "thread_id": message.sessionId,
        },
    }
    if TRACK_LLM:
        langfuse_handler = CallbackHandler(
            secret_key=LANGFUSE_SECRET_KEY,
            public_key=LANGFUSE_PUBLIC_KEY,
            host=LANGFUSE_HOST,  # 🇪🇺 EU region
            session_id=message.sessionId
        )
            # host="https://us.cloud.langfuse.com", # 🇺🇸 US region
        result["callbacks"] = [langfuse_handler]
    print(result)
    return result


@app.post("/chat")
async def post_chat(jwt_message: JWSChatItem, request: Request):
    message = convert_jwt_to_chat_item(jwt_message.model_dump(), JWS_SECRET_KEY)
    return await post_chat_graph(message, request)
    # return await post_chat_free(message, request)


@app.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await ws_chat_graph(websocket)
    # await ws_chat_free(websocket)


async def process_chat(message: ChatItem, request: Request, agent):
    # key= request.headers.get("X-Chat-Key","")
    # if key != api_key:
    #     return{"user": message.user,
    #         "AI": "Error: Unauthorized"}
    return {"chatMessage": message.chatMessage,
            "sessionId": message.sessionId,
            "isAuthenticated": message.isAuthenticated,
            "customerId": message.customerId,
            "response": await agent.get_session_response(message.sessionId, message.chatMessage,
                                                         get_config_by_message(message)), }


async def process_ws(websocket, agent: BaseAgent):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if "token" in data:
                jwt_message = JWSChatItem(**data)
                message = convert_jwt_to_chat_item(jwt_message.model_dump(), JWS_SECRET_KEY)
            else:
                message = ChatItem(**data)
            async for response in agent.get_session_response_stream(message.sessionId, message.chatMessage,
                                                                    get_config_by_message(message)):
                ws_response = {
                    "response": response,
                    "isCompleted": False}
                await websocket.send_json(ws_response)
            ws_response = {
                "chatMessage": message.chatMessage,
                "sessionId": message.sessionId,
                "isAuthenticated": message.isAuthenticated,
                "customerId": message.customerId,
                "response": "",
                "isCompleted": True}
            await websocket.send_json(ws_response)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(e.__class__)
        print(e)
    finally:
        if not websocket.client_state == WebSocketState.DISCONNECTED:
            await websocket.close()


@app.post("/chat_mock")
async def post_chat_mock(message: ChatItem, request: Request):
    return await process_chat(message, request, mock_agent)


@app.post("/chat_free")
async def post_chat_free(message: ChatItem, request: Request):
    return await process_chat(message, request, free_agent)


@app.post("/chat_graph")
async def post_chat_graph(message: ChatItem, request: Request):
    return await process_chat(message, request, graph_agent)


@app.websocket("/ws/chat_mock")
async def ws_chat_mock(websocket: WebSocket):
    await process_ws(websocket, mock_agent)


@app.websocket("/ws/chat_free")
async def ws_chat_free(websocket: WebSocket):
    await process_ws(websocket, free_agent)


@app.websocket("/ws/chat_graph")
async def ws_chat_graph(websocket: WebSocket):
    await process_ws(websocket, graph_agent)
