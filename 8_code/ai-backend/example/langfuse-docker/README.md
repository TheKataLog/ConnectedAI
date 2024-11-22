# Local Deployment Instructions

## Overview
This project uses Langfuse for tracking and monitoring. To deploy the service locally, you can use Docker Compose.

## Prerequisites
- Ensure Docker and Docker Compose are installed on your local machine.

## Steps to Deploy Locally

1. **Clone the Repository**
   ```sh
   git clone https://github.com/your-repo/your-project.git
   cd your-project


## Start the Service

Use the following command to deploy the service locally:
```
sh docker compose up
```
## Access the Service

Once the service is up and running, you can access it on the specified port (default is 8000).
## Tracking with Langfuse
Langfuse is integrated into the project for tracking and monitoring purposes. Ensure you have the necessary configurations set up for Langfuse in your environment variables.

## Stopping the Service
To stop the service, use: 
```
sh docker compose down
```