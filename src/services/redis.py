from fastapi import HTTPException, Request, status
from redis.asyncio import Redis
import uuid
import json
from src.auth.schemas import UserSessionInfo
from src.config import REDIS_HOST, REDIS_PORT
from src.utils.logger import logger

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

SESSION_TTL = 1800


async def remove_session(session_key):

    session = f"session:{session_key}"

    if await redis_client.exists(session):
        await redis_client.delete(session)
        logger.info(f"Deleted session {session_key}")
    else:
        logger.warning(f"Session {session_key} does not exists")
        return None
    user_id, session_uuid = session_key.split(":")

    user_sessions_key = f"user_sessions:{user_id}"
    if await redis_client.srem(user_sessions_key, session_uuid):
        logger.info(f"Deleted session uuid {session_uuid} from set {user_sessions_key}")
    else:
        logger.warning(
            f"Session id {session_uuid} does not found in set {user_sessions_key}"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def remove_all_user_session(user_id: int):
    user_sessions_key = f"user_sessions:{user_id}"
    if await redis_client.exists(user_sessions_key):
        session_uuids = await redis_client.smembers(user_sessions_key)
        for session_uuid in session_uuids:
            session_key = f"session:{user_id}:{session_uuid}"
            if await redis_client.exists(session_key):
                await redis_client.delete(session_key)
                logger.info(f"Deleted session {session_key}")
            else:
                logger.warning(f"Session {session_key} does not exist")

        await redis_client.delete(user_sessions_key)
        logger.info(f"Deleted sessions of user {user_id}")


async def create_session(user_id: int, email: str, is_superuser: bool):
    session_uuid = str(uuid.uuid4())
    session_key = f"session:{user_id}:{session_uuid}"
    session_data = json.dumps({"email": email, "is_superuser": is_superuser})

    await redis_client.setex(session_key, SESSION_TTL, session_data)
    await redis_client.sadd(f"user_sessions:{user_id}", session_uuid)

    logger.info(f"Create session for user {user_id}")
    return f"{user_id}:{session_uuid}"


async def get_user_info(request: Request) -> UserSessionInfo:
    session = request.cookies.get("authcook")
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    try:
        user_id, session_uuid = session.split(":", 1)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session format"
        )

    session_key = f"session:{user_id}:{session_uuid}"
    session_data = await redis_client.get(session_key)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found",
        )

    await redis_client.expire(session_key, SESSION_TTL)

    data = json.loads(session_data)
    return UserSessionInfo(
        id=int(user_id),
        email=data["email"],
        is_superuser=data["is_superuser"],
    )


async def get_current_user(request: Request) -> UserSessionInfo:
    return await get_user_info(request)


async def get_current_superuser(request: Request) -> UserSessionInfo:
    user = await get_user_info(request)
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user


async def delete_session_from_set(message):
    expired_key = message["data"]
    logger.info(f"start deleting{expired_key}")
    if expired_key.startswith("session:"):
        _, user_id, session_uuid = expired_key.split(":")

        user_sessions_key = f"user_sessions:{user_id}"
        if await redis_client.srem(user_sessions_key, session_uuid):
            logger.info(f"Removed session {session_uuid} from {user_sessions_key}")
        else:
            logger.info(f"Session {session_uuid} not found in {user_sessions_key}")


keyspace_channel = "__keyevent@0__:expired"


async def listen_for_expiration_keys():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(keyspace_channel)

    async for message in pubsub.listen():
        if message["type"] == "message":
            await delete_session_from_set(message)
