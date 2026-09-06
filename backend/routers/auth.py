from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from datetime import datetime
from database import get_db
from models import UserCreate, UserLogin, Token
from auth import get_password_hash, verify_password, create_access_token, get_current_user, invalidate_user_cache

router = APIRouter(prefix="/api/auth", tags=["auth"])

def serialize_user(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
        doc.pop("password", None)
    return doc

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    db = get_db()
    
    existing = await db.users.find_one({
        "$or": [
            {"username": user_data.username},
            {"email": user_data.email}
        ]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    users_count = await db.users.count_documents({})
    role = "admin" if users_count == 0 else "user"
    
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "password": await get_password_hash(user_data.password),
        "role": role,
        "display_name": "",
        "bio": "",
        "avatar_original": None,
        "avatar_thumb": None,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await db.users.insert_one(user_doc)
    access_token = create_access_token(data={"sub": str(result.inserted_id)})
    
    return Token(access_token=access_token)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    db = get_db()
    
    user = await db.users.find_one({"username": credentials.username})
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not await verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return Token(access_token=access_token)

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return serialize_user(dict(current_user))

@router.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_db()
    cursor = db.users.find()
    users = []
    async for doc in cursor:
        users.append(serialize_user(dict(doc)))
    return users

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    db = get_db()
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    await invalidate_user_cache(user_id)
    return {"success": True}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if str(current_user["_id"]) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db = get_db()
    result = await db.users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    await invalidate_user_cache(user_id)
    return {"deleted": True}
