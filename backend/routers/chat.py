from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from datetime import datetime
from typing import List, Dict
from bson import ObjectId
from database import get_db
from auth import get_optional_user
from jose import jwt, JWTError
from config import settings
import json
import html
import re
import asyncio

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[Dict] = []  # {ws, user_info}

    async def connect(self, websocket: WebSocket, user_info: dict):
        await websocket.accept()
        self.active_connections.append({"ws": websocket, "user": user_info})
        await self.broadcast_online_count()

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [c for c in self.active_connections if c["ws"] != websocket]

    async def broadcast_online_count(self):
        count = len(self.active_connections)
        msg = json.dumps({"type": "online_count", "count": count})
        for conn in self.active_connections[:]:
            try:
                await conn["ws"].send_text(msg)
            except:
                pass

    async def broadcast(self, message: dict):
        text = json.dumps(message, default=str)
        for conn in self.active_connections[:]:
            try:
                await conn["ws"].send_text(text)
            except:
                self.active_connections.remove(conn)

manager = ConnectionManager()

# Rate limit: per user, max 1 msg / 1.5s
rate_limits: Dict[str, float] = {}
RATE_LIMIT_SECONDS = 1.5

# Message length
MAX_MSG_LENGTH = 500
MAX_STORED_MESSAGES = 200  # keep last N in DB


def sanitize(text: str) -> str:
    """Sanitize message text"""
    text = html.escape(text.strip())
    text = re.sub(r'\s+', ' ', text)  # collapse whitespace
    return text[:MAX_MSG_LENGTH]


def serialize_message(doc: dict) -> dict:
    return {
        "type": "message",
        "_id": str(doc["_id"]),
        "username": doc.get("username", "Guest"),
        "display_name": doc.get("display_name", ""),
        "avatar_thumb": doc.get("avatar_thumb"),
        "role": doc.get("role", "user"),
        "text": doc.get("text", ""),
        "created_at": doc.get("created_at", datetime.utcnow()).isoformat(),
    }


@router.get("/messages")
async def get_messages(limit: int = Query(50, le=100)):
    """Get recent chat messages"""
    db = get_db()
    cursor = db.chat_messages.find().sort("created_at", -1).limit(limit)
    messages = []
    async for doc in cursor:
        messages.append(serialize_message(doc))
    messages.reverse()
    return messages


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    db = get_db()

    # Try to authenticate
    user_info = {
        "user_id": None,
        "username": "Guest",
        "display_name": "",
        "avatar_thumb": None,
        "role": "guest",
    }

    if token:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id:
                user = await db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    user_info = {
                        "user_id": str(user["_id"]),
                        "username": user.get("username", "Guest"),
                        "display_name": user.get("display_name", ""),
                        "avatar_thumb": user.get("avatar_thumb"),
                        "role": user.get("role", "user"),
                    }
        except (JWTError, Exception):
            pass

    await manager.connect(websocket, user_info)

    try:
        # Send recent messages on connect
        cursor = db.chat_messages.find().sort("created_at", -1).limit(50)
        messages = []
        async for doc in cursor:
            messages.append(serialize_message(doc))
        messages.reverse()

        await websocket.send_text(json.dumps({
            "type": "history",
            "messages": messages,
        }, default=str))

        while True:
            data = await websocket.receive_text()

            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue

            if payload.get("type") == "message":
                # Must be logged in
                if not user_info.get("user_id"):
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "text": "Login required to send messages",
                    }))
                    continue

                text = payload.get("text", "").strip()
                if not text:
                    continue

                text = sanitize(text)
                if not text:
                    continue

                # Rate limit
                uid = user_info["user_id"]
                now = datetime.utcnow().timestamp()
                last = rate_limits.get(uid, 0)
                if now - last < RATE_LIMIT_SECONDS:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "text": "Slow down! Wait a moment.",
                    }))
                    continue
                rate_limits[uid] = now

                # Re-fetch user info (in case profile was updated)
                user = await db.users.find_one({"_id": ObjectId(uid)})
                if user:
                    user_info["display_name"] = user.get("display_name", "")
                    user_info["avatar_thumb"] = user.get("avatar_thumb")
                    user_info["username"] = user.get("username", "Guest")
                    user_info["role"] = user.get("role", "user")

                # Store message
                msg_doc = {
                    "user_id": uid,
                    "username": user_info["username"],
                    "display_name": user_info.get("display_name", ""),
                    "avatar_thumb": user_info.get("avatar_thumb"),
                    "role": user_info.get("role", "user"),
                    "text": text,
                    "created_at": datetime.utcnow(),
                }
                result = await db.chat_messages.insert_one(msg_doc)
                msg_doc["_id"] = result.inserted_id

                # Broadcast
                await manager.broadcast(serialize_message(msg_doc))

                # Cleanup old messages
                total = await db.chat_messages.count_documents({})
                if total > MAX_STORED_MESSAGES:
                    oldest = db.chat_messages.find().sort("created_at", 1).limit(total - MAX_STORED_MESSAGES)
                    ids = [doc["_id"] async for doc in oldest]
                    if ids:
                        await db.chat_messages.delete_many({"_id": {"$in": ids}})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_online_count()
    except Exception:
        manager.disconnect(websocket)
        await manager.broadcast_online_count()
