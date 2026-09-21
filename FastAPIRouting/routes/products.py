from fastapi import APIRouter,Path
from fastapi.responses import JSONResponse

products = {
    "P1":{"name": "Coffee", "price": 4.99},
    "P2":{"name": "Tea", "price": 2.99},
}

router = APIRouter(prefix="/products",tags=["products"])

@router.get("")
def getProducts():
    return JSONResponse(status_code=200,content=products)


@router.get("/{productId}")
def getProductById(productId:str=Path(...,description="Id of Products in the DB",examples=["P1","P2"])):

    if productId not in products:
        return JSONResponse(status_code=404,content={"message":"Product Doesnot exist","success":False})
    
    return JSONResponse(status_code=200, content={"message":"Product found","success":True,"data":products[productId]})
