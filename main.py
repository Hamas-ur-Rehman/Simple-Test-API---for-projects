import logging
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import json
import binascii
import re
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Request Logger API", version="1.0.0")

# TCP Server Configuration
TCP_HOST = "0.0.0.0"
TCP_PORT = 8000

class DataProcessor:
    """
    Enhanced data processor that handles various data types and formats
    """
    
    @staticmethod
    def try_decode_text(data: bytes) -> Optional[str]:
        """
        Try to decode bytes as text using various encodings
        """
        encodings = ['utf-8', 'ascii', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return None
    
    @staticmethod
    def detect_protocol(data: bytes) -> str:
        """
        Attempt to detect the protocol/format of the data
        """
        if not data:
            return "empty"
        
        # Try to decode as text first
        text = DataProcessor.try_decode_text(data)
        if text:
            text_lower = text.lower().strip()
            
            # HTTP detection
            if text_lower.startswith(('get ', 'post ', 'put ', 'delete ', 'head ', 'options ', 'patch ')):
                return "http"
            
            # JSON detection
            if text_lower.startswith(('{', '[')):
                try:
                    json.loads(text)
                    return "json"
                except:
                    pass
            
            # XML detection
            if text_lower.startswith('<?xml') or text_lower.startswith('<'):
                return "xml"
            
            # Email detection
            if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
                return "email"
            
            # URL detection
            if re.search(r'https?://[^\s]+', text):
                return "url"
            
            # CSV detection
            if ',' in text and '\n' in text:
                lines = text.split('\n')
                if len(lines) > 1 and all(',' in line for line in lines[:3] if line.strip()):
                    return "csv"
            
            return "text"
        
        # Binary format detection
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            return "png"
        elif data.startswith(b'\xff\xd8\xff'):
            return "jpeg"
        elif data.startswith(b'GIF8'):
            return "gif"
        elif data.startswith(b'%PDF'):
            return "pdf"
        elif data.startswith(b'PK\x03\x04'):
            return "zip"
        elif data.startswith(b'\x1f\x8b'):
            return "gzip"
        elif data.startswith(b'BM'):
            return "bmp"
        elif data.startswith(b'RIFF') and b'WAVE' in data[:12]:
            return "wav"
        elif data.startswith(b'\x00\x00\x00\x18ftypmp4') or data.startswith(b'\x00\x00\x00\x1cftyp'):
            return "mp4"
        else:
            return "binary"
    
    @staticmethod
    def format_binary_data(data: bytes, max_bytes: int = 64) -> str:
        """
        Format binary data for logging with hex dump
        """
        if len(data) <= max_bytes:
            hex_dump = binascii.hexlify(data).decode('ascii')
            return f"hex: {hex_dump}"
        else:
            hex_dump = binascii.hexlify(data[:max_bytes]).decode('ascii')
            return f"hex (first {max_bytes} bytes): {hex_dump}... (total: {len(data)} bytes)"
    
    @staticmethod
    def process_data(data: bytes) -> dict:
        """
        Process and analyze incoming data
        """
        if not data:
            return {"type": "empty", "message": "No data received"}
        
        protocol = DataProcessor.detect_protocol(data)
        result = {
            "type": protocol,
            "size": len(data),
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if protocol in ["text", "json", "xml", "http", "email", "url", "csv"]:
            text = DataProcessor.try_decode_text(data)
            if text:
                result["content"] = text
                if protocol == "json":
                    try:
                        result["parsed_json"] = json.loads(text)
                    except:
                        pass
        else:
            result["content"] = DataProcessor.format_binary_data(data)
            
        return result

async def handle_tcp_client(reader, writer):
    """
    Enhanced TCP client handler that accepts every sort of data
    """
    client_addr = writer.get_extra_info('peername')
    logger.info(f"TCP client connected from {client_addr}")
    
    try:
        # Send welcome message
        welcome_msg = "Connected to Enhanced TCP Logger Server - Send any data!\n"
        writer.write(welcome_msg.encode('utf-8'))
        await writer.drain()
        
        # Buffer for accumulating data
        data_buffer = b""
        message_count = 0
        
        while True:
            try:
                # Read data from client with timeout
                data = await asyncio.wait_for(reader.read(4096), timeout=30.0)
                
                if not data:
                    logger.info(f"TCP client {client_addr} closed connection")
                    break
                
                # Add to buffer
                data_buffer += data
                message_count += 1
                
                # Process the data
                processed_data = DataProcessor.process_data(data)
                
                # Log the processed data
                log_entry = {
                    "client": str(client_addr),
                    "message_number": message_count,
                    "data": processed_data
                }
                
                logger.info(f"TCP Data: {json.dumps(log_entry, indent=2)}")
                
                # Send acknowledgment back to client
                ack_msg = f"✓ Logged {processed_data['type']} data ({processed_data['size']} bytes) - Message #{message_count}\n"
                writer.write(ack_msg.encode('utf-8'))
                await writer.drain()
                
                # If we've accumulated a lot of data, log buffer summary
                if len(data_buffer) > 1024 * 1024:  # 1MB
                    buffer_summary = {
                        "client": str(client_addr),
                        "buffer_summary": {
                            "total_size": len(data_buffer),
                            "message_count": message_count,
                            "protocols_detected": list(set([DataProcessor.detect_protocol(chunk) for chunk in [data_buffer[i:i+1024] for i in range(0, min(len(data_buffer), 10240), 1024)]]))
                        }
                    }
                    logger.info(f"TCP Buffer Summary: {json.dumps(buffer_summary, indent=2)}")
                    # Reset buffer to prevent memory issues
                    data_buffer = b""
                
            except asyncio.TimeoutError:
                logger.info(f"TCP client {client_addr} timeout - no data received in 30 seconds")
                timeout_msg = "No data received in 30 seconds. Connection still open.\n"
                writer.write(timeout_msg.encode('utf-8'))
                await writer.drain()
                continue
                
            except Exception as read_error:
                logger.error(f"Error reading from TCP client {client_addr}: {read_error}")
                break
                
    except asyncio.CancelledError:
        logger.info(f"TCP client {client_addr} connection cancelled")
    except Exception as e:
        logger.error(f"TCP client {client_addr} error: {e}")
    finally:
        # Log final session summary
        if message_count > 0:
            session_summary = {
                "client": str(client_addr),
                "session_summary": {
                    "total_messages": message_count,
                    "total_data_size": len(data_buffer),
                    "session_duration": "ended"
                }
            }
            logger.info(f"TCP Session Summary: {json.dumps(session_summary, indent=2)}")
        
        logger.info(f"TCP client {client_addr} disconnected")
        try:
            writer.close()
            await writer.wait_closed()
        except:
            pass

async def start_tcp_server():
    """
    Start the TCP server
    """
    server = await asyncio.start_server(
        handle_tcp_client,
        TCP_HOST,
        TCP_PORT
    )
    
    logger.info(f"TCP server started on {TCP_HOST}:{TCP_PORT}")
    
    async with server:
        await server.serve_forever()

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
    
    async def main():
        """
        Run TCP server on port 8000
        """
        logger.info("Starting TCP server on port 8000...")
        
        # Start only the TCP server
        await start_tcp_server()
    
    # Run the main async function
    asyncio.run(main()) 