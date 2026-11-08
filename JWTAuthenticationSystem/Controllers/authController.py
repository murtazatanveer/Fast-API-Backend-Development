import logging

from fastapi import Request

from Schemas.authSchema import AccessTokenPayload, LoginRequest, SignupRequest
from Services.loginService import login
from Services.logoutOtherDevicesService import logoutOtherDevices
from Services.logoutService import logout
from Services.refreshService import refresh
from Services.signupService import signup
from Utils.errors import ServiceError
from Utils.responceHelper import errorResponse, successResponse
from Utils.security import getClearRefreshCookieSettings, getRefreshCookieSettings

logger = logging.getLogger(__name__)


def buildAuthResponse(status_code: int, message: str, result: dict):
    response = successResponse(
        status_code,
        message,
        displayUi=True,
        data={"accessToken": result["access_token"]},
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
            "Server Error. Please try again later",
            displayUi=True,
        )

    return buildAuthResponse(201, "Account Created Successfully", result)


async def loginController(payload: LoginRequest, request: Request):
    try:
        result = await login(payload, request)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Login failed")
        return errorResponse(
            500,
            "Server Error. Please try again later",
            displayUi=True,
        )

    return buildAuthResponse(200, "User Login Successfully", result)


async def refreshController(request: Request):
    try:
        result = await refresh(request)
    except ServiceError as exc:
        response = errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
        response.delete_cookie(**getClearRefreshCookieSettings())
        return response
    except Exception:
        logger.exception("Refresh failed")
        return errorResponse(
            500,
            "Server Error. Please try again later",
            displayUi=True,
        )

    response = successResponse(
        200,
        "Token Refreshed Successfully",
        displayUi=True,
        data={"accessToken": result["access_token"]},
    )
    response.set_cookie(
        value=result["refresh_token"],
        **getRefreshCookieSettings(),
    )
    return response


async def logoutController(request: Request, current_user: AccessTokenPayload):
    try:
        await logout(request, current_user)
    except Exception:
        logger.exception("Logout failed")
        return errorResponse(
            500,
            "Server Error. Please try again later",
            displayUi=True,
        )

    response = successResponse(
        200,
        "User Logged Out Successfully",
        displayUi=True,
    )
    response.delete_cookie(**getClearRefreshCookieSettings())
    return response


async def logoutOtherDevicesController(
    request: Request, current_user: AccessTokenPayload
):
    try:
        other_devices = await logoutOtherDevices(request, current_user)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Logout other devices failed")
        return errorResponse(
            500,
            "An unexpected error occurred. Please try again.",
            displayUi=True,
        )

    if other_devices == 0:
        message = "No other devices to log out"
    elif other_devices == 1:
        message = "Logged out from 1 device"
    else:
        message = f"Logged out from {other_devices} devices"

    return successResponse(200, message, displayUi=True)
