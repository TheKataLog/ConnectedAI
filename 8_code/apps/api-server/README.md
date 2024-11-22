# Connected AI - Backend Server

This is the backend server for the Connected AI application. It handles user authentication, guest token generation, and chatbot message processing.

## Features

- User login with JWT authentication.
- Guest mode support with token issuance.
- API to process chat messages.

## Requirements

- Node.js v16 or higher
- NPM or Yarn
- `.env` file with:
  ```env
  PORT=5001
  SECRET_KEY=your_secret_key
  ```

## How to setup the NoSql Google Cloud Firestore collection

- Make sure you have the Service Account private key downloaded as JSON file `serviceAccount.json`
  > To use the Firebase Admin SDK on your own server (or any other Node.js environment), use a service account. Go to IAM & admin > Service accounts in the Google Cloud console. Generate a new private key and save the JSON file.
- The csv file with the Users data to be loaded into the Collection

1. Go to the `db-load` folder

   ```bash
   cd api-server/db-load
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

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd apps/api-server
   ```

2. Install dependencies:

   ```bash
    npm install
   ```

3. Server is configured with default Secret and Port

4. Start the server

   ```bash
    npm start
   ```
