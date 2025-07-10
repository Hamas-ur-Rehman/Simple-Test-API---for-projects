#!/usr/bin/env python3
"""
Test script to simulate 3cx call flow designer socket component behavior
"""

import socket
import json
import time

def test_tcp_connection():
    """
    Test TCP connection to simulate 3cx socket component
    """
    host = "localhost"
    port = 8001
    
    # Sample call flow data
    test_data = {
        "call_id": "12345",
        "caller_number": "+1234567890",
        "called_number": "+0987654321",
        "action": "incoming_call",
        "timestamp": time.time(),
        "extension": "101",
        "caller_name": "John Doe"
    }
    
    try:
        # Create socket connection (similar to 3cx socket component)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            # Receive welcome message
            welcome = sock.recv(1024).decode('utf-8')
            print(f"Welcome message: {welcome.strip()}")
            
            # Send JSON data (as 3cx would)
            message = json.dumps(test_data)
            sock.send(message.encode('utf-8'))
            print(f"Sent: {message}")
            
            # Wait for response (WaitForResponse = True)
            response = sock.recv(1024).decode('utf-8')
            print(f"Response: {response.strip()}")
            
            # Parse response
            try:
                response_data = json.loads(response.strip())
                print(f"Parsed response: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Plain text response: {response}")
                
    except Exception as e:
        print(f"Error: {e}")

def test_plain_text():
    """
    Test plain text message
    """
    host = "localhost"
    port = 8001
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            # Receive welcome message
            welcome = sock.recv(1024).decode('utf-8')
            print(f"Welcome message: {welcome.strip()}")
            
            # Send plain text
            message = "Hello from 3cx call flow test"
            sock.send(message.encode('utf-8'))
            print(f"Sent: {message}")
            
            # Wait for response
            response = sock.recv(1024).decode('utf-8')
            print(f"Response: {response.strip()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing 3cx Call Flow Integration")
    print("=" * 40)
    
    print("\n1. Testing JSON call flow data:")
    test_tcp_connection()
    
    print("\n2. Testing plain text message:")
    test_plain_text()
    
    print("\nTest completed!") 