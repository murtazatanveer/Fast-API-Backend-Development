# Services/authSignup.py
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import Response
from google.cloud import firestore

from Models.authModels import UserRegister
from Utils.security import hashPassword, createAccessToken
from Configuration.config import settings
from Configuration.firestore_client import get_db

async def registerUser(userData: UserRegister, response: Response):
    db = get_db()

    usersRef = db.collection("Users")
    
    # 1. Check if Email already exists
    emailQuery = await usersRef.where(filter=firestore.FieldFilter("email", "==", userData.email)).limit(1).get()
    if emailQuery:
        return {"error": "Email already registered", "statusCode": 409}

    # 2. Check if Username already exists
    usernameQuery = await usersRef.where(filter=firestore.FieldFilter("username", "==", userData.username)).limit(1).get()
    if usernameQuery:
        return {"error": "Username already taken", "statusCode": 409}

    # 3. Hash Password & Create User in Firestore
    hashedPw = hashPassword(userData.password)
    newUserRef = usersRef.document()
    userId = newUserRef.id

    userDoc = {
        "username": userData.username,
        "email": userData.email,
        "hashedPassword": hashedPw,
        "createdAt": datetime.now(timezone.utc)
    }
    await newUserRef.set(userDoc)

    # 4. Generate Tokens
    accessToken = createAccessToken(userId)
    refreshToken = secrets.token_urlsafe(64)
    expiresAt = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    # 5. Save Refresh Token to Firestore
    await db.collection("refreshTokens").document(refreshToken).set({
        "userId": userId,
        "expiresAt": expiresAt,
    })

    # 6. Set httpOnly Cookie
    response.set_cookie(
        key="refreshToken",
        value=refreshToken,
        httponly=True, 
        secure=False, # During deployment set this t True
        samesite="strict",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )
    # 7. Return success data
    return {
        "accessToken": accessToken,
        "user": {
            "id": userId,
            "username": userData.username,
            "email": userData.email
        }
    }