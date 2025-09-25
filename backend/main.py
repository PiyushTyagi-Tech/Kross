from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

waiting_users = []
active_chats = {}

@app.websocket("/ws")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Pair user if someone is waiting
    if waiting_users:
        partner = waiting_users.pop(0)
        active_chats[websocket] = partner
        active_chats[partner] = websocket

        await websocket.send_text("✅ Connected with a stranger!")
        await partner.send_text("✅ Connected with a stranger!")
    else:
        waiting_users.append(websocket)
        await websocket.send_text("⌛ Waiting for a stranger to connect...")

    try:
        while True:
            data = await websocket.receive_text()
            if websocket in active_chats:
                partner = active_chats[websocket]
                await partner.send_text(f"Stranger: {data}")
    except WebSocketDisconnect:
        # Cleanup on disconnect
        if websocket in active_chats:
            partner = active_chats.pop(websocket)
            del active_chats[partner]
            await partner.send_text("❌ Stranger disconnected.")
        elif websocket in waiting_users:
            waiting_users.remove(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
