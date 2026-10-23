from fastapi import APIRouter, Response , Depends , Request

from Models.authModels import UserRegister,UserLogin

from Services.authSignup import registerUser
from Services.authLogin import loginUser
from Services.authRefresh import refreshUserToken
from Services.authLogout import logoutUser
from Services.authLogoutAll import logoutOtherDevices

from Utils.responseHelper import successResponse, errorResponse

from Dependencies.authDependency import getCurrentUser

router = APIRouter()

@router.post("/signup")
async def signup(
    userData: UserRegister, 
    response: Response
):
    
    try:
        result = await registerUser(userData, response)

        if "error" in result:
            return errorResponse(
                statusCode=result["statusCode"], 
                message=result["error"], 
                displayUi=True
            )

        return successResponse(
            statusCode=201,
            message="Account created successfully",
            data={
                "accessToken": result["accessToken"],
                "user": result["user"]
            },
            displayUi=True
        )
    except Exception as e:
        errorResponse(statusCode=500,message=f'Internal Server Error , {str(e)}')


@router.post("/login")
async def login(userData: UserLogin, response: Response):
    try:
        result = await loginUser(userData, response)

        if "error" in result:
            return errorResponse(
                statusCode=result["statusCode"], 
                message=result["error"], 
                displayUi=True
            )

        return successResponse(
            statusCode=200,
            message="Logged in successfully",
            data={
                "accessToken": result["accessToken"],
                "user": result["user"]
            },
            displayUi=True
        )
    except Exception as e:
        errorResponse(statusCode=500,message=f'Internal Server Error , {str(e)}')


@router.post("/refresh")
async def refresh(request: Request):
    try:
        result = await refreshUserToken(request)

        if "error" in result:
            # displayUi=False because React interceptors handle this silently
            return errorResponse(
                statusCode=result["statusCode"], 
                message=result["error"], 
                displayUi=False 
            )

        return successResponse(
            statusCode=200,
            message="Token refreshed successfully",
            data={
                "accessToken": result["accessToken"],
                "user": result["user"]
            },
            displayUi=False
        )
    except Exception as e:
        errorResponse(statusCode=500,message=f'Internal Server Error , {str(e)}')


@router.post("/logout")
async def logout(
    request: Request, 
    response: Response,
    currentUser: dict = Depends(getCurrentUser)
):
    try:
        result = await logoutUser(request, response)

        if "error" in result:
            return errorResponse(
                statusCode=result["statusCode"],
                message=result["error"],
            )

        return successResponse(
            statusCode=200,
            message=result["message"],
        )
    except Exception as e:
        errorResponse(statusCode=500,message=f'Internal Server Error , {str(e)}')
    

@router.get("/protected")
async def getProtectedUser(currentUser: dict = Depends(getCurrentUser)):
   
    return successResponse(
        statusCode=200,
        message="Access granted to protected route",
        data={"user": currentUser},
        displayUi=False
    )


@router.post("/logout-other-devices")
async def logoutoOtherDevices(
    request: Request, 
    currentUser: dict = Depends(getCurrentUser)
):
    try :
        result = await logoutOtherDevices(request, currentUser["id"])

        if "error" in result:
            return errorResponse(
                statusCode=result["statusCode"],
                message=result["error"],
            )

        return successResponse(
            statusCode=200,
            message=result["message"],
        )
    except Exception as e:
        errorResponse(statusCode=500,message=f'Internal Server Error , {str(e)}')