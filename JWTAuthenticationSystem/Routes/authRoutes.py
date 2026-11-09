from fastapi import APIRouter, Depends, Request

from Controllers.authController import (
    loginController,
    logoutController,
    logoutOtherDevicesController,
    refreshController,
    signupController,
    verifyLoginController,
)
from Dependencies.authDependency import verifyAccessToken
from Schemas.authSchema import (
    AccessTokenPayload,
    LoginRequest,
    SignupRequest,
    VerifyLoginRequest,
)

authRouter = APIRouter(prefix="/auth", tags=["Auth"])


@authRouter.post("/signup", status_code=200)
async def signupRoute(payload: SignupRequest):
    return await signupController(payload)


@authRouter.post("/login", status_code=200)
async def loginRoute(payload: LoginRequest):
    return await loginController(payload)


@authRouter.post("/verify-login", status_code=200)
async def verifyLoginRoute(payload: VerifyLoginRequest, request: Request):
    return await verifyLoginController(payload, request)


@authRouter.post("/refresh", status_code=200)
async def refreshRoute(request: Request):
    return await refreshController(request)


@authRouter.delete("/logout", status_code=200)
async def logoutRoute(
    request: Request,
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await logoutController(request, current_user)


@authRouter.delete("/logout-other-devices", status_code=200)
async def logoutOtherDevicesRoute(
    request: Request,
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await logoutOtherDevicesController(request, current_user)
