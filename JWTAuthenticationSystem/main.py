from contextlib import asynccontextmanager

import Models  # noqa: F401
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from Configuration.supabaseClient import Base, closeDatabaseConnections, getDatabaseEngine
from Routes.authRoutes import authRouter
from Routes.patientsRoutes import patientsRouter
from Utils.responceHelper import errorResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🗄️  Initializing Supabase PostgreSQL Engine...")
    try:
        engine = getDatabaseEngine() 
        print("✅ PostgreSQL Engine ready (Async)")
        print("⏳ Creating tables if they don't exist...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables are ready.")
    except Exception as e:
        print(f"❌ PostgreSQL init failed: {type(e).__name__}: {e}")
        raise

    yield

    print("👋 Shutting down...")
    try:
        await closeDatabaseConnections()
        print("✅ PostgreSQL connections closed.")
    except Exception as e:
        print(f"❌ Error closing PostgreSQL: {e}")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "authToken"],
)
app.include_router(authRouter)
app.include_router(patientsRouter)


@app.exception_handler(StarletteHTTPException)
async def httpExceptionHandler(request: Request, exc: StarletteHTTPException):
    response = errorResponse(
        exc.status_code,
        str(exc.detail),
    )
    if exc.headers:
        response.headers.update(exc.headers)
    return response


@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    location = [str(part) for part in first_error.get("loc", []) if part != "body"]
    message = first_error.get("msg", "Invalid request data")
    if location:
        message = f"{'.'.join(location)}: {message}"
    return errorResponse(422, message)


@app.get("/")
def WelcomeMessage():
    return {
        "message":"Welcome to JWT Authenticaion System",
        "success":True
    }

