require('dotenv').config();
const http = require('http');
const WebSocket = require('ws');
const jwt = require('jsonwebtoken');

const app = require('./src/app');

const SECRET_KEY = process.env.SECRET_KEY || 'secret';
const PORT = process.env.PORT || 5001;

// HTTP server to attach WebSocket
const server = http.createServer(app);

// Initialize WebSocket server
const wss = new WebSocket.Server({ server });

// Validate and process incoming WebSocket messages
wss.on('connection', (ws, req) => {
  ws.on('message', (message) => {
    console.log('received');
    try {
      const { token, payload } = JSON.parse(message);

      // Validate the token
      const decoded = jwt.verify(token, SECRET_KEY);
      const { sessionId, customerId, email } = decoded;

      console.log(`Authenticated user: ${email}, Session: ${sessionId}`);

      // Simulate a streaming response
      const responses = [
        'Let me think...',
        "Alright, here's what I came up with:",
        `Hello ${email}, your message was: "${payload.message}"`,
      ];

      responses.forEach((response, index) => {
        setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ sessionId, response }));
          }
        }, index * 1000); // Simulate delay between responses
      });
    } catch (error) {
      console.error('WebSocket error:', error.message);
      ws.send(JSON.stringify({ error: 'Unauthorized or invalid token.' }));
    }
  });

  ws.on('close', () => {
    console.log('WebSocket connection closed.');
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
