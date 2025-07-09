This project is a **simple API service for quick testing** that allows applications to interact with it and verify if they can connect to the internet.

## Purpose

This lightweight FastAPI service is designed to:
- **Test Internet Connectivity**: Applications can make requests to this service to verify they have internet access
- **Request Logging**: All incoming requests are logged with detailed information including headers and body content
- **Simple Testing**: Provides a straightforward endpoint for connectivity and integration testing

## Features

- **FastAPI-based**: Modern, fast web framework for building APIs
- **Request Logging**: Automatically logs all incoming requests with headers and body data
- **JSON Response**: Returns structured JSON responses for easy parsing
- **Docker Support**: Includes Docker configuration for easy deployment
- **Lightweight**: Minimal dependencies and simple setup

## Quick Start

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the service:
   ```bash
   python main.py
   ```

3. The API will be available at `http://localhost:8000`

### Docker

1. Build the Docker image:
   ```bash
   docker build -t call-flow-test .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 call-flow-test
   ```

## API Endpoints

### GET /test

**Purpose**: Main endpoint for testing connectivity and logging requests

**Response**:
```json
{
    "message": "Request Logger API is running",
    "version": "1.0.0",
    "description": "Send any request to any path and it will be logged"
}
```

**Usage**: Applications can make GET requests to `/test` to verify:
- Internet connectivity is working
- The service is accessible and responding
- Request details are being logged properly

## Use Cases

This service is particularly useful for:
- **Network Testing**: Verify applications can reach external services
- **Integration Testing**: Test API connectivity in development/staging environments
- **Debugging**: Log and analyze request patterns during development
- **Health Checks**: Simple endpoint for monitoring and health verification

## Logging

All requests are logged with:
- Complete request headers
- Request body content (JSON formatted when possible)
- Timestamp and detailed formatting
- Error handling for malformed requests

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

See `requirements.txt` for exact dependencies.

---

*This is a simple, no-frills API service designed specifically for quick connectivity testing and request logging.*
