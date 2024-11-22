# Connected AI - Frontend

This is the React-based frontend for the ShopWise application. It allows users to log in with a username and password or continue in guest mode to interact with the chatbot.

## Features

- **Login:** Users can log in with a username and password.
- **Guest Mode:** Allows users to chat without creating an account.
- **Responsive Chat UI:** Integrated with `@chatscope/chat-ui-kit-react` for a modern chat interface.
- **Token-Based Authentication:** JWT tokens are used to validate and authenticate requests to the backend.

## Prerequisites

- **Node.js** (v16 or higher)
- **NPM** or **Yarn**

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd apps/app-ui
   ```

2. Install dependencies:

   ```bash
    npm install
   ```

3. Configure the backend API base URL:

   - Edit src/api/apiClient.js and update the BASE_URL constant to match your backend server URL.

4. Start the development server:

   ```bash
   npm start
   ```

5. To build the code for deployment
   ```bash
   npm run build
   ```
