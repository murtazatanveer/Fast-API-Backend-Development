# Services/authLogoutAll.py
from fastapi import Request
from google.cloud import firestore
from Configuration.firestore_client import get_db

async def logoutOtherDevices(request: Request, currentUserId: str):
    db = get_db()

    # 1. Read the current device's token from the cookie
    currentRefreshToken = request.cookies.get("refreshToken")
    
    if not currentRefreshToken:
        return {"error": "No refresh token provided", "statusCode": 401}

    # 2. Query all tokens for this user
    tokens_query = db.collection("refreshTokens").where(
        filter=firestore.FieldFilter("userId", "==", currentUserId)
    )
    
    matching_tokens = await tokens_query.get()

    # 3. Batch delete all tokens EXCEPT the current one
    batch = db.batch()
    deleted_count = 0
    
    for token_doc in matching_tokens:
        if token_doc.id != currentRefreshToken: # <-- THE KEY CONDITION
            batch.delete(token_doc.reference)
            deleted_count += 1
            
    if deleted_count > 0:
        await batch.commit()

    # 4. Return success (Cookie is NOT cleared)
    return {
        "success": True, 
        "message": f"Logged out from {deleted_count} other device(s) successfully"
    }