from core.server.main_server import convert_jwt_to_chat_item


def test_convert_jwt_to_chat_item():
    data = {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiVXNlciIsInNlc3Npb25JZCI6IjQ2NjJmMmM3LTFkZWEtNGIzMi1iODkwLThkMGY5ZDA5YWNmZiIsImN1c3RvbWVySWQiOiIxMjEwIiwiZW1haWwiOiIyZXJrYTcxYzdAb3V0bG9vay5jb20iLCJpYXQiOjE3MzE5MjU0NDUsImV4cCI6MTczMTkyOTA0NX0.4FRDQknFDUGnEzgrrRcMm3LSmQna3tXJAGVRBqk9o7s",
        "chatMessage": "Hello"
    }
    result = convert_jwt_to_chat_item(data, "secret",  options={"verify_exp": False})
    assert result.sessionId == "4662f2c7-1dea-4b32-b890-8d0f9d09acff"
    assert result.isAuthenticated == True
    assert result.customerId == 1210
    assert result.chatMessage == "Hello"
