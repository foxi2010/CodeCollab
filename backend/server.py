from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

active_sessions = {}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    if session_id not in active_sessions:
        active_sessions[session_id] = {"users": set(), "code": "# Start coding!\n"}
    active_sessions[session_id]["users"].add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("UPDATE:"):
                active_sessions[session_id]["code"] = data.split(":", 1)[1]
                for user in active_sessions[session_id]["users"]:
                    if user != websocket:
                        await user.send_text(f"SYNC:{active_sessions[session_id]['code']}")
    except:
        active_sessions[session_id]["users"].remove(websocket)