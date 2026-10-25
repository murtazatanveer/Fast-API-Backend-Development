# Services/authRefresh.py
from datetime import datetime, timezone
from fastapi import  Request
from Configuration.firestore_client import get_db
from Utils.security import createAccessToken

async def refreshUserToken(request: Request):
    db = get_db()

    # 1. Read the token from the httpOnly cookie
    refreshToken = request.cookies.get("refreshToken")
    print("Refresh Token : ",refreshToken)
    if not refreshToken:
        return {"error": "No refresh token provided", "statusCode": 401}

    # 2. Look up the token in Firestore
    snap = await db.collection("refreshTokens").document(refreshToken).get()
    
    if not snap.exists:
        return {"error": "Invalid refresh token", "statusCode": 401}

    tokenData = snap.to_dict()

    # 3. Check if the token has expired
    if tokenData["expiresAt"] < datetime.now(timezone.utc):
        # Clean up the expired token
        await snap.reference.delete()
        return {"error": "Refresh token expired. Please log in again.", "statusCode": 401}

    # 4. Verify the user still exists
    userSnap = await db.collection("Users").document(tokenData["userId"]).get()
    if not userSnap.exists:
        await snap.reference.delete()
        return {"error": "User account no longer exists", "statusCode": 401}

    # 5. Generate a NEW Access Token
    newAccessToken = createAccessToken(tokenData["userId"])

    # 6. Return the new Access Token (Cookie is NOT touched)
    return {
        "accessToken": newAccessToken,
        "user": {
            "id": userSnap.id,
            "username": userSnap.to_dict()["username"],
            "email": userSnap.to_dict()["email"]
        }
    }