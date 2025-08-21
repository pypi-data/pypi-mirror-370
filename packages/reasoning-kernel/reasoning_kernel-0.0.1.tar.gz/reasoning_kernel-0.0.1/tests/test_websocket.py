#!/usr/bin/env python3
"""Test WebSocket streaming functionality"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_streaming():
    uri = "ws://localhost:5000/api/v2/ws/reasoning/stream/test_session_123"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] Connected to WebSocket")
            
            # Send test reasoning request
            request = {
                "type": "start_reasoning",
                "vignette": "A company must decide whether to launch a new product in a competitive market with uncertain demand",
                "config": {
                    "enable_thinking_mode": True,
                    "thinking_detail_level": "detailed",
                    "generate_reasoning_sentences": True
                }
            }
            
            await websocket.send(json.dumps(request))
            print(f"[{datetime.now()}] Sent reasoning request")
            
            # Listen for responses
            timeout = 30  # 30 second timeout
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "stage_update":
                        print(f"[{datetime.now()}] Stage: {data.get('stage')} - {data.get('status')}")
                        if data.get('message'):
                            print(f"  Message: {data['message']}")
                            
                    elif data.get("type") == "thinking_update":
                        print(f"[{datetime.now()}] Thinking: {data.get('sentence')}")
                        
                    elif data.get("type") == "sandbox_update":
                        print(f"[{datetime.now()}] Sandbox: {data.get('message')}")
                        
                    elif data.get("type") == "error":
                        print(f"[{datetime.now()}] Error: {data.get('message')}")
                        break
                        
                    # Check if complete
                    if data.get("stage") == "complete":
                        print(f"[{datetime.now()}] Reasoning completed!")
                        print(f"  Confidence: {data.get('overall_confidence')}")
                        print(f"  Total time: {data.get('total_time')}s")
                        break
                        
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    await websocket.send(json.dumps({"type": "ping"}))
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing MSA Reasoning Engine WebSocket Streaming...")
    asyncio.run(test_streaming())