# FastAPI Request Logger

A simple FastAPI server that logs all incoming request headers and body data.

## Features

- **Catch-all endpoint**: Accepts any HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS) on any path
- **Header logging**: Logs all request headers
- **Body logging**: Logs request body (with JSON pretty-printing when applicable)
- **JSON content type support**: Handles JSON requests and responses
- **Docker support**: Includes Dockerfile for easy containerization

## Quick Start

### Using Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   docker build -t fastapi-logger .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 fastapi-logger
   ```

3. **Access the API:**
   - Root endpoint: http://localhost:8000
   - Send requests to any path: http://localhost:8000/your-path

### Using Python directly

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python main.py
   ```
   or
   ```bash
   uvicorn main:app --reload
   ```

## Usage Examples

### Test with curl:

```bash
# GET request
curl http://localhost:8000/test

# POST request with JSON
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{"key": "value", "number": 42}'

# PUT request with custom headers
curl -X PUT http://localhost:8000/users/123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token123" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## What gets logged

For each request, the server logs:
- **Request Headers**: All HTTP headers sent with the request
- **Request Body**: The complete request body (formatted as JSON if applicable)
- **Request Info**: HTTP method, URL, path, and query parameters

## API Endpoints

- `{method} /` and `{method} /{path:path}`: Single endpoint that logs and responds to any request on any path

## Configuration

The server runs on:
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8000

## Docker

The included Dockerfile:
- Uses Python 3.11 slim image
- Installs dependencies from requirements.txt
- Exposes port 8000
- Runs with auto-reload enabled for development 