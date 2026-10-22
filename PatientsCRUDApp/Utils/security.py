import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from Configuration.config import settings

def hashPassword(password: str) -> str:
    pwdBytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwdBytes, salt)
    return hashed.decode('utf-8')

def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return bcrypt.checkpw(
        plainPassword.encode('utf-8'), 
        hashedPassword.encode('utf-8')
    )

def createAccessToken(userId: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"uid": userId, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decodeAccessToken(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])