# Deployment Instructions

### Clone the Repository

Clone the application repository to your local machine.

```bash
git clone <repository-url>

```

## Backend API Deployment

#### Prerequisites  
- gcloud CLI installed 
- gcloud auth login

### 1. Go to the Backend API directory
```bash
cd 8_code/apps/app-server
```

### 2. Build the Docker Image
Navigate to the backend project directory and build the Docker image.
```bash
docker build -t gcr.io/<gcp-project-id>/shopwise-api-server:latest .
```
### 3. Push the Image to Google Container Registry
Push the Docker image to your Google Container Registry.
```bash
docker push gcr.io/<gcp-project-id>/shopwise-api-server:latest
```

### 4. Deploy to Cloud Run
Deploy the service to Cloud Run using the pushed Docker image.
Note: The Service handles the Authentication
```bash
gcloud run deploy shopwise-api-server \
  --image gcr.io/<gcp-project-id>/shopwise-api-server:latest \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated
```

#### After deployment, Cloud Run will provide a service URL. 


## WebApp Deployment

### 1. Deploy the React WebApp
```bash
cd 8_code/apps/app-ui
```
Set the Cloud run service URL into the apiClient.js `BASE_URL`

### 2. Install Dependencies
```bash
npm install
```

### 3. Build the Application
Generate the production build for deployment.
```bash
npm run build
```
This creates a build folder containing the compiled application.

### 4. **Firebase CLI**: Install the Firebase CLI if you haven’t already.
   ```bash
   npm install -g firebase-tools
```

### 5. Initialize Firebase Hosting
Run the Firebase initialization command to set up hosting for your project.

```bash
firebase init hosting
```
During Initialization:
- Select Firebase Project: Choose the Firebase project you want to deploy to.
- ? What do you want to use as your public directory? build
- ? Configure as a single-page app (rewrite all urls to /index.html)? No
- ? Set up automatic builds and deploys with GitHub? No
- ✔  Wrote build/404.html
- ? File build/index.html already exists. Overwrite? No

### 5. Deploy to Firebase
Deploy the application to Firebase Hosting.

```bash
firebase deploy --only hosting
```

6. Verify Deployment
After deployment, Firebase will provide a Hosting URL. Open this URL in your browser to view the live application.

Example:
```bash
Hosting URL: https://your-project-id.web.app
```

## 3. ConnectedAI - AI - Backend Server

The AI Backend Server for ConnectedAI is deployed using Google Cloud Run. The Docker image for this service is built by the CI/CD pipeline defined in `.github/workflows/build_docker.yaml`.

### Deployment Steps

1. **Build Docker Image**
   - The Docker image is automatically built by the CI/CD pipeline whenever changes are pushed to the `ai-backend` directory. The pipeline is defined in `.github/workflows/build_docker.yaml`.

2. **Deploy to Google Cloud Run**
   - The built Docker image is deployed as a Cloud Run service in Google Cloud Platform (GCP).
   - The service listens on port `8000`.

3. **Start Command**
   - The service is started with the following command:
     ```sh
     make run
     ```

4. **Environment Variables**
   - The Cloud Run instance needs to set all the environment variables defined in [ai-backend/example/env.example](ai-backend/example/env.example).
   - Ensure that these environment variables are correctly configured in the Cloud Run service settings.
5. Enable [claude-3-5-sonnet-v2 API](https://console.cloud.google.com/marketplace/product/anthropic/claude-3-5-sonnet-v2) in Vertex AI console


