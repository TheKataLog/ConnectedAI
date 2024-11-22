from core.env import SERVER_PORT
from core.server.main_server import app
# from core.server.main_mock import app


def start_service():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)

if __name__ == '__main__':
    start_service()