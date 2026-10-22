from fastapi import APIRouter
from Controllers.authController import router as auth_controller_router

router = APIRouter(prefix="/auth", tags=["JWT Authentication"])
router.include_router(auth_controller_router)