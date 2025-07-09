import logging
from fastapi import FastAPI, Request
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

@app.get("/test")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 