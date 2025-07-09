import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Request Logger API", version="1.0.0")

@app.get("/test_get")
async def test(request: Request):
    """
    Root endpoint with API information
    """
    
    # Log headers in JSON format
    headers_dict = dict(request.headers)
    logger.info(f"Headers: {json.dumps(headers_dict, indent=2)}")
    
    # Log body in JSON format
    try:
        body = await request.body()
        body_str = body.decode('utf-8') if body else ""
        if body_str:
            try:
                # Try to parse as JSON for pretty printing
                body_json = json.loads(body_str)
                logger.info(f"Body: {json.dumps(body_json, indent=2)}")
            except json.JSONDecodeError:
                # If not valid JSON, log as string
                logger.info(f"Body: {json.dumps({'raw_body': body_str}, indent=2)}")
        else:
            logger.info(f"Body: {json.dumps({'body': 'empty'}, indent=2)}")
    except Exception as e:
        logger.error(f"Error reading body: {e}")
        logger.info(f"Body: {json.dumps({'error': 'Could not read body'}, indent=2)}")
    
    return JSONResponse(
        content={
            "message": "Request Logger API is running",
            "version": "1.0.0",
            "description": "Send any request to any path and it will be logged",
        }
    )

@app.post("/test_post")
async def catch_all_post(request: Request):
    """
    POST endpoint that logs all headers and body data
    """
    
    logger.info(f"POST request to /test_post")
    
    # Log headers in JSON format
    headers_dict = dict(request.headers)
    logger.info(f"Headers: {json.dumps(headers_dict, indent=2)}")
    
    # Log body in JSON format
    try:
        body = await request.body()
        body_str = body.decode('utf-8') if body else ""
        if body_str:
            try:
                # Try to parse as JSON for pretty printing
                body_json = json.loads(body_str)
                logger.info(f"Body: {json.dumps(body_json, indent=2)}")
            except json.JSONDecodeError:
                # If not valid JSON, log as string
                logger.info(f"Body: {json.dumps({'raw_body': body_str}, indent=2)}")
        else:
            logger.info(f"Body: {json.dumps({'body': 'empty'}, indent=2)}")
    except Exception as e:
        logger.error(f"Error reading body: {e}")
        logger.info(f"Body: {json.dumps({'error': 'Could not read body'}, indent=2)}")
    
    return JSONResponse(
        content={
            "message": "POST request to /test_post logged successfully",
            "path": "/test_post",
            "status": "logged"
        }
    )

@app.websocket("/test_ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint that logs connection headers and all incoming messages
    """
    
    await websocket.accept()
    
    # Log connection headers
    headers_dict = dict(websocket.headers)
    logger.info(f"WebSocket connection established")
    logger.info(f"WebSocket Headers: {json.dumps(headers_dict, indent=2)}")
    
    try:
        while True:
            # Receive message (can be text or bytes)
            try:
                # Try to receive as text first
                message = await websocket.receive_text()
                logger.info(f"WebSocket Text Message: {json.dumps({'type': 'text', 'message': message}, indent=2)}")
                
                # Echo back the message with confirmation
                await websocket.send_text(f"Logged: {message}")
                
            except:
                # If text fails, try bytes
                try:
                    message = await websocket.receive_bytes()
                    message_str = message.decode('utf-8', errors='ignore')
                    logger.info(f"WebSocket Bytes Message: {json.dumps({'type': 'bytes', 'message': message_str, 'length': len(message)}, indent=2)}")
                    
                    # Echo back confirmation
                    await websocket.send_text(f"Logged bytes message of length: {len(message)}")
                    
                except:
                    # Handle JSON messages or other formats
                    try:
                        message = await websocket.receive_json()
                        logger.info(f"WebSocket JSON Message: {json.dumps({'type': 'json', 'message': message}, indent=2)}")
                        
                        # Echo back the JSON
                        await websocket.send_json({"status": "logged", "original_message": message})
                        
                    except Exception as e:
                        logger.error(f"Error receiving WebSocket message: {e}")
                        break
                        
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 