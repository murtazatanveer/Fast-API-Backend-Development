from fastapi.responses import JSONResponse

def errorResponse(statusCode: int, message: str, displayUi:bool = False, **extra) -> JSONResponse:
    content = {"success": False, "message": message,"displayUi":displayUi}
    if extra:
        content.update(extra)
    return JSONResponse(status_code=statusCode, content=content)


def successResponse(statusCode: int, message: str,displayUi:bool=False, data: dict | None = None,
                    **extra) -> JSONResponse:
    content = {"success": True, "message": message,"displayUi":displayUi}
    if data is not None:
        content["data"] = data
    if extra:
        content.update(extra)
    return JSONResponse(status_code=statusCode, content=content)