
# Local Machine Deployment Guide

This guide provides instructions to set up and run the following locally:
1. ConnectedAI - Web App - Backend Server
2. ConnectedAI - Web App - Frontend Server
3. ConnectedAI - AI - Backend Server 

---

## 1. ConnectedAI - Web App - Backend Server

### **Overview**
The backend server handles:
- User authentication (with JWT tokens).
- Guest token generation.
- Chatbot message processing.

### **Features**
1. User login with JWT authentication.
2. Guest mode support with token issuance.
3. API to process chat messages.

### **Requirements**
- Node.js (v16 or higher)
- NPM or Yarn
- `.env` file with the following variables:
  ```plaintext
  PORT=5001
  SECRET_KEY=your_secret_key
  ```

## How to setup the NoSql Google Cloud Firestore collection

- Make sure you have the Service Account private key downloaded as JSON file `serviceAccount.json`
  > To use the Firebase Admin SDK on your own server (or any other Node.js environment), use a service account. Go to IAM & admin > Service accounts in the Google Cloud console. Generate a new private key and save the JSON file.
- The csv file with the Users data to be loaded into the Collection

1. Go to the `db-load` folder

   ```bash
   cd 8_code/apps/api-server/db-load
   ```

2. install dependencies
   ```bash
   npm install
   ```
3. Run the upload
   ```bash
   node index.js
   ```
4. The records will be uploaded to the Firestore `users` collection.
   
### **Installation**
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd 8_code/apps/api-server
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the server:
   ```bash
   npm start
   ```

By default, the server uses `PORT=5001` and the specified `SECRET_KEY`.

---

## 2. ConnectedAI - Web App - Frontend

### **Overview**
The React-based frontend allows:
- User login with a username and password.
- Guest mode for interacting with the chatbot without an account.
- A modern and responsive chat interface built with `@chatscope/chat-ui-kit-react`.
- JWT token-based authentication for secure API requests.

### **Features**
1. Login with username and password.
2. Guest mode for non-registered users.
3. Responsive chat UI.
4. Token-based authentication for requests to the backend.

### **Prerequisites**
- Node.js (v16 or higher)
- NPM or Yarn

### **Installation**
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd 8_code/apps/app-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure the backend API base URL:
   - Open `src/api/apiClient.js`.
   - Update the `BASE_URL` constant to match your backend server's URL:
     ```javascript
     const BASE_URL = 'http://localhost:5001';
     ```

4. Start the development server:
   ```bash
   npm start
   ```

5. To build the code for deployment:
   ```bash
   npm run build
   ```

---

### **Notes**
- Ensure both backend and frontend servers are running to enable full functionality.
- Configure the backend and frontend to communicate using consistent environment variables or configuration files.

---

## 3. ConnectedAI - AI - Backend Server

### Initialization

To install the necessary dependencies, run:
```sh
make init
```

### Running the Service

To start the service, use:
```sh
make run
```

### Calling the API

To call the API, execute:
```sh
make post
```

### Switch service
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

You will also need a local/local_config.py, use the one in example folder as a template.


### AI Backend Endpoints

#### API Endpoints
- `/chat`
- `/chat_mock`
- `/chat_free`
- `/chat_graph`

#### Streaming (WebSocket) Endpoints
- `/ws/chat`
- `/ws/chat_mock`
- `/ws/chat_free`
- `/ws/chat_graph`

#### Example API Request
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
example websocket request:
```json
{"chatMessage":"Hello","sessionId":"test_session","isAuthenticated":true,"customerId":123,"response":"\n"}
```
example websocket response as sequence:
```json
{"response":"","isCompleted":false}
{"response":"","isCompleted":false}
{"response":"Hi","isCompleted":false}
{"response":" there! How can I help you today?  I can assist with questions about","isCompleted":false}
{"response":" your orders or products.\n","isCompleted":false}
{"chatMessage":"Hello","sessionId":"test_session","isAuthenticated":true,"customerId":123,"response":"\n","isCompleted":true}
```


Note that JWT tokens are now used to encode and decode all messages. Please refer to convert_jwt_to_chat_item function in [ai-backend/core/server/main_server.py](ai-backend/core/server/main_server.py) for detail.
