import asyncio
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from bson import ObjectId, json_util
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from database import get_db
from cache import get_redis

security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"

# FIX: get_current_user/get_optional_user раньше били в Mongo на КАЖДЫЙ
# авторизованный запрос (логин по _id — индексированный, но всё равно лишний
# круговой запрос при высокой частоте запросов одного юзера). Короткий TTL —
# чтобы бан/смена роли не "жили" в кэше дольше пары секунд.
USER_CACHE_TTL = 15

def _user_cache_key(user_id: str) -> str:
    return f"user:cache:{user_id}"

async def invalidate_user_cache(user_id: str) -> None:
    redis = get_redis()
    if redis:
        try:
            await redis.delete(_user_cache_key(user_id))
        except Exception:
            pass

async def _find_user_cached(user_id: str) -> Optional[dict]:
    redis = get_redis()
    if redis:
        try:
            cached = await redis.get(_user_cache_key(user_id))
            if cached:
                return json_util.loads(cached)
        except Exception:
            pass

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if redis and user is not None:
        try:
            await redis.setex(_user_cache_key(user_id), USER_CACHE_TTL, json_util.dumps(user))
        except Exception:
            pass

    return user

def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def _get_password_hash_sync(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt — синхронный и CPU-bound (~100-300мс на дефолтном cost).
    # Вызванный напрямую в async-хендлере, он блокирует весь event loop
    # воркера на время проверки — все остальные запросы этого воркера встают.
    return await asyncio.to_thread(_verify_password_sync, plain_password, hashed_password)

async def get_password_hash(password: str) -> str:
    return await asyncio.to_thread(_get_password_hash_sync, password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")
    
    user = await _find_user_cached(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_current_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return await _find_user_cached(user_id)
    except:
        pass
    return None
