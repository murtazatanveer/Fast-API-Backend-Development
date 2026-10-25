# Services/authLogin.py
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import Response
from google.cloud import firestore

from Models.authModels import UserLogin
from Utils.security import verifyPassword, createAccessToken
from Configuration.config import settings
from Configuration.firestore_client import get_db   

async def loginUser(userData: UserLogin, response: Response):
    db = get_db()

    usersRef = db.collection("Users")
    
    # 1. Find the user by username
    userQuery = await usersRef.where(filter=firestore.FieldFilter("username", "==", userData.username.lower())).limit(1).get()
    
    if not userQuery:
        return {"error": "Invalid username or password", "statusCode": 401}

    userDoc = userQuery[0]
    userDict = userDoc.to_dict()
    userId = userDoc.id

    # 2. Verify the password
    if not verifyPassword(userData.password, userDict["hashedPassword"]):
        return {"error": "Invalid username or password", "statusCode": 401}

    # 3. Generate Access Token
    accessToken = createAccessToken(userId)

    # 4. Generate Refresh Token & Save to Firestore
    refreshToken = secrets.token_urlsafe(64)
    expiresAt = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    await db.collection("refreshTokens").document(refreshToken).set({
        "userId": userId,
        "expiresAt": expiresAt
    })

    # 5. Set httpOnly Cookie
    response.set_cookie(
        key="refreshToken",
        value=refreshToken,
        httponly=True,
        secure=False, # Set to True in production
         samesite="lax", 
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60
    )

    # 6. Return success data
    return {
        "accessToken": accessToken,
        "user": {
            "id": userId,
            "username": userDict["username"],
            "email": userDict["email"]
        }
    }