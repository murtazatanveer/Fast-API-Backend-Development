# Services/authLogoutAll.py
from fastapi import Request
from google.cloud import firestore
from Configuration.firestore_client import get_db

async def logoutOtherDevices(request: Request, currentUserId: str):
    db = get_db()

    currentRefreshToken = request.cookies.get("refreshToken")
    
    if not currentRefreshToken:
        return {"error": "No refresh token provided", "statusCode": 401}

    # 🚨 SECURITY FIX: Verify the current token actually exists in DB and belongs to the user
    current_token_ref = db.collection("refreshTokens").document(currentRefreshToken)
    current_token_snap = await current_token_ref.get()

    if not current_token_snap.exists:
        return {"error": "Invalid session token", "statusCode": 401}
        
    # Double-check that the token belongs to this user
    token_data = current_token_snap.to_dict()
    if token_data.get("userId") != currentUserId:
        return {"error": "Token mismatch", "statusCode": 401}

    # 2. Query all tokens for this user
    tokens_query = db.collection("refreshTokens").where(
        filter=firestore.FieldFilter("userId", "==", currentUserId)
    )
    
    matching_tokens = await tokens_query.get()

    # 3. Batch delete all tokens EXCEPT the current one
    batch = db.batch()
    deleted_count = 0
    
    for token_doc in matching_tokens:
        if token_doc.id != currentRefreshToken: 
            batch.delete(token_doc.reference)
            deleted_count += 1
            
    if deleted_count > 0:
        await batch.commit()

    return {
        "message": f"Logged out from {deleted_count} other devices successfully"
    }