import pytest
import uvicorn
import threading
import time
import json
import asyncio
import socket
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncIterator

# Define a global flag to control server lifecycle
_server_running = threading.Event()

def run_server(app, host, port):
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    
    # Run the server in a loop until the flag is cleared
    thread = threading.Thread(target=server.serve)
    thread.start()
    
    while not _server_running.is_set():
        time.sleep(0.1) # Wait for server to start
    
    server.should_exit = True
    thread.join()

@pytest.fixture(scope="session")
def mock_server():
    host = "127.0.0.1"
    
    # Find an available high-level port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]

    server_url = f"http://{host}:{port}"
    
    app = FastAPI()

    async def sse_generator(text: str) -> AsyncIterator[str]:
        text_len = len(text)
        if text_len < 8:
            chunk_texts = [text]
        else:
            base_len = text_len // 8
            chunk_texts = [text[i*base_len:(i+1)*base_len] for i in range(7)]
            chunk_texts.append(text[7*base_len:])  # 最后一份
        for chunk_text in chunk_texts:
            chunk_data = {
                "choices": [{"delta": {"content": chunk_text}}],
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
            await asyncio.sleep(0.01) # Simulate network delay
        yield "data: [DONE]\n\n"

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request):
        data = await request.json()
        last_message = data.get("messages", [])[-1]
        content = last_message.get("content", "")
        stream = data.get("stream", False)

        if stream:
            return StreamingResponse(
                sse_generator(content),
                media_type="text/event-stream"
            )
        else:
            response_data = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": content
                    }
                }]
            }
            return JSONResponse(content=response_data)
            
    server_thread = threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": host, "port": port},
        daemon=True
    )
    server_thread.start()
    time.sleep(1) # Give server time to start

    yield server_url

    # No explicit shutdown needed for daemon thread, but it's good practice
    # The session will end and the daemon thread will be terminated
