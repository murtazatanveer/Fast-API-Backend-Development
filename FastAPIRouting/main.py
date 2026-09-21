from fastapi import FastAPI
from routes import products,carts

app = FastAPI()

app.include_router(products.router)
app.include_router(carts.router)

@app.get("/")
def intro():
    return{
        "message":"Welcome to Fast API Routing",
        "success":True
    }

