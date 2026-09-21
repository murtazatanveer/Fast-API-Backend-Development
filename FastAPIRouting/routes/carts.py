from fastapi import APIRouter

router = APIRouter(prefix="/carts",tags=["carts"])

@router.get("")
def list_carts():
    return {"cart_id": 1, "items": 3}