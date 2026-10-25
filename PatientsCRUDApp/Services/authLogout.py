# Services/authLogout.py
from fastapi import Request, Response
from Configuration.firestore_client import get_db

async def logoutUser(request: Request, response: Response):
    db = get_db()

    # 1. Read the token from the httpOnly cookie
    refreshToken = request.cookies.get("refreshToken")
    
    if not refreshToken:
        return {"error": "No refresh token provided", "statusCode": 401}

    doc_ref = db.collection("refreshTokens").document(refreshToken)
    snap = await doc_ref.get()

    if not snap.exists:
        response.delete_cookie(
            key="refreshToken",
            httponly=True,
            secure=False, 
            samesite="lax"
        )
        return {"error": "Invalid or already revoked token", "statusCode": 401}

    # 3. Delete from Firestore
    await doc_ref.delete()

    # 4. Tell the browser to delete the cookie
    response.delete_cookie(
        key="refreshToken",
        httponly=True,
        secure=False, 
        samesite="strict"
    )

    return {"success": True, "message": "Logged out successfully"}