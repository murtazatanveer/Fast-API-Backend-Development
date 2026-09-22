from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.middleware("http")
async def simpleMiddleware(request:Request,call_next):

    print("🔵 Middleware: request received")

    res = await call_next(request)

    res.headers["X-Powered-By"] = "MyFastAPI"

    print("🟢 Middleware: response sent")

    return res

@app.get("/")
def home():
    print("⭐ Endpoint: home() is running")
    return {"message": "This is home endpoint"}


@app.get("/about")
def about():
    print("⭐ Endpoint: about() is running")
    return {"message": "This is the about endpoint"}

@app.get("/error")
def error():
    print("⭐ Endpoint: error() is running")
    # raise HTTPException(status_code=500,detail="internal server error")
    # return JSONResponse(status_code=500,content={"message":"internal server error"})
    return JSONResponse(status_code=500,content="internal server error")
    
    