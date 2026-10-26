# Services/authLogout.py
from fastapi import Request, Response
from Configuration.firestore_client import get_db

async def logoutUser(request: Request, response: Response, currentUserId: str):
    db = get_db()

    # 1. Read the token from the httpOnly cookie
    refreshToken = request.cookies.get("refreshToken")
    if not refreshToken:
        print("2")
        return {"error": "No refresh token provided", "statusCode": 401}

    doc_ref = db.collection("refreshTokens").document(refreshToken)
    snap = await doc_ref.get()


    # 2. Check if it exists
    if not snap.exists:
        response.delete_cookie("refreshToken", httponly=True, secure=False, samesite="lax")
        return {"error": "Invalid or already revoked token", "statusCode": 401}

    # 🚨 3. SECURITY FIX: Verify the token belongs to the authenticated user
    tokenData = snap.to_dict()
    if tokenData.get("userId") != currentUserId:
        return {"error": "Token does not belong to this user", "statusCode": 401}

    # 4. Delete from Firestore
    await doc_ref.delete()

    # 5. Tell the browser to delete the cookie
    response.delete_cookie(
        key="refreshToken",
        httponly=True,
        secure=False, 
        samesite="lax" # Note: Use "lax" for dev, "strict" or "none" for prod
    )
    return { "message": "Logged out successfully"}