from fastapi import APIRouter, Request

from Controllers.authController import loginController, signupController
from Schemas.authSchema import LoginRequest, SignupRequest

authRouter = APIRouter(prefix="/auth", tags=["Auth"])


@authRouter.post("/signup", status_code=201)
async def signupRoute(payload: SignupRequest, request: Request):
    return await signupController(payload, request)


@authRouter.post("/login", status_code=200)
async def loginRoute(payload: LoginRequest, request: Request):
    return await loginController(payload, request)
