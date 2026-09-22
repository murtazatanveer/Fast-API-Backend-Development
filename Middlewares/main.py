from fastapi import FastAPI,Request,Header,Depends,Path,HTTPException
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
    
    
@app.get("/token")
def printToken(token: str = Header(description="Enter Token",default="secret_token")):
    return {"token_received": token}

# Dependency Injection 

def getGreeting(greetMsg:str=Path(...,description="Give Greeting message",title="Greeting Message",example="Good Afternoon"))->str:
    return greetMsg

@app.get("/greeting/{greetMsg}")
def greeting(msg:str=Depends(getGreeting)):
    return JSONResponse(status_code=200,content={"message":msg,"sucess":True})

# No Code Repetition Using Dependency 

TOKEN = "MyPrivateToken"

def verifyToken(token: str=Header(...,description="Provide Token")):
    if token != TOKEN:
        raise HTTPException(status_code=401,detail="Invalid Token",)
    return token

@app.get("/products")
def getProducts(tok:str = Depends(verifyToken)):
    return {"message": "Products list","success":True}
    
@app.get("/orders")
def list_orders(token: str = Depends(verifyToken)):
    return {"message": "Orders list"}