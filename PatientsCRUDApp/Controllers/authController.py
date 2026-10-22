from fastapi import APIRouter, Response

from Models.authModels import UserRegister,UserLogin

from Services.authSignup import registerUser
from Services.authLogin import loginUser

from Utils.responseHelper import successResponse, errorResponse

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
