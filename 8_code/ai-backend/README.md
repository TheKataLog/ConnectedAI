# Usage

## Initialization

To install the necessary dependencies, run:
```sh
make init
```

## Running the Service

To start the service, use:
```sh
make run
```

## Calling the API

To call the API, execute:
```sh
make post
```

## Switch service
Comment the lines in [start_service.py](start_service.py) to switch between the agents.
```
from core.server.main_gemini import app
# from core.server.main_mock import app
```

main_gemini service is using Gemini model, either the free Google Gemini model or VertexAI. 

main_mock service is using the mock model, which is a simple model that returns a fixed response.

You will need to create local/mock_data.py contains the mock output data. i.e.
```
outputs=[
    {"user":"Hello","AI":"How can I help you!"},
    {"user":"Hello","AI":"How can I help you 2!"},
    {"user":"Hello","AI":"How can I help you 3!"},
]
```

You will also need a local/envs/.env.<env> file to define the configuration.


## AI Backend Endpoints

### API Endpoints
- `/chat`
- `/chat_mock`
- `/chat_free`
- `/chat_graph`

### Streaming (WebSocket) Endpoints
- `/ws/chat`
- `/ws/chat_mock`
- `/ws/chat_free`
- `/ws/chat_graph`

### Example API Request
```json
{
  "chatMessage": "Hello",
  "sessionId": "test_session",
  "isAuthenticated": true,
  "customerId": 123
}
```

or
```json
{"chatMessage":"Hello","sessionId":"test_session","isAuthenticated":false}
```
example api response:
```json
{"chatMessage":"Hello","sessionId":"test_session","isAuthenticated":true,"customerId":123,"response":"\n","isCompleted":true}
```
example ws request:
```json
{"chatMessage":"Hello","sessionId":"test_session","isAuthenticated":true,"customerId":123,"response":"\n"}
```
example ws response as sequence:
```json
{"response":"","isCompleted":false}
{"response":"","isCompleted":false}
{"response":"Hi","isCompleted":false}
{"response":" there! How can I help you today?  I can assist with questions about","isCompleted":false}
{"response":" your orders or products.\n","isCompleted":false}
{"chatMessage":"Hello","sessionId":"test_session","isAuthenticated":true,"customerId":123,"response":"\n","isCompleted":true}
```
