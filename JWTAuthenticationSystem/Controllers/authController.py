import logging

from fastapi import Request

from Schemas.authSchema import LoginRequest, SignupRequest, UserPublic
from Services.loginService import login
from Services.signupService import signup
from Utils.errors import ServiceError
from Utils.responceHelper import errorResponse, successResponse
from Utils.security import getRefreshCookieSettings

logger = logging.getLogger(__name__)


def buildAuthResponse(status_code: int, message: str, result: dict):
    user_data = UserPublic.model_validate(result["user"]).model_dump(
        by_alias=True, mode="json"
    )
    response = successResponse(
        status_code,
        message,
        data={
            "user": user_data,
            "accessToken": result["access_token"],
            "tokenType": result["token_type"],
            "expiresIn": result["expires_in"],
        },
    )
    response.set_cookie(
        value=result["refresh_token"],
        **getRefreshCookieSettings(),
    )
    return response


async def signupController(payload: SignupRequest, request: Request):
    try:
        result = await signup(payload, request)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Signup failed")
        return errorResponse(
            500,
            "An unexpected error occurred. Please try again.",
            displayUi=True,
        )

    return buildAuthResponse(201, "Account created successfully", result)


async def loginController(payload: LoginRequest, request: Request):
    try:
        result = await login(payload, request)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Login failed")
        return errorResponse(
            500,
            "An unexpected error occurred. Please try again.",
            displayUi=True,
        )

    return buildAuthResponse(200, "Logged in successfully", result)
