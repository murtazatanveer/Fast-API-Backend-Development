# Dependencies/authDependency.py
from typing import Annotated
from fastapi import Header, HTTPException, status
from jose import JWTError, ExpiredSignatureError

from Utils.security import decodeAccessToken
from Configuration.firestore_client import get_db

async def getCurrentUser(
    authToken: Annotated[str, Header(..., description="Provide JWT Auth Token")]
) -> dict:
    
    try:
        # 1. Manually check the Bearer_ prefix
        if not authToken.startswith("Bearer_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        # 2. Extract the raw token
        token = authToken.split("Bearer_", 1)[1].strip()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing token"
            )

        # 3. Decode the Access Token (JWT)
        payload = decodeAccessToken(token)
        
        # 4. Extract the user ID
        userId: str = payload.get("uid")
        
        if userId is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is missing the user ID"
            )

    except HTTPException:
        raise  # Let our custom HTTPExceptions pass through

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired", 
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature or format",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred during authentication"
        )

    # 5. Get DB directly via getDb()
    db = get_db()

    # 6. Verify the user still exists in the database
    snap = await db.collection("Users").document(userId).get()
    if not snap.exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists",
        )

    # 7. Return the user data
    userData = snap.to_dict()
    return {
        "id": snap.id,
        "username": userData["username"],
        "email": userData["email"]
    }