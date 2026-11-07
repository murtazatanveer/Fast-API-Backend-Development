from contextlib import asynccontextmanager

import Models  # noqa: F401
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from Configuration.supabaseClient import Base, closeDatabaseConnections, getDatabaseEngine
from Routes.authRoutes import authRouter
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
app.include_router(authRouter)


@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    location = [str(part) for part in first_error.get("loc", []) if part != "body"]
    message = first_error.get("msg", "Invalid request data")
    if location:
        message = f"{'.'.join(location)}: {message}"
    return errorResponse(422, message, displayUi=True)


@app.get("/")
def WelcomeMessage():
    return {
        "message":"Welcome to JWT Authenticaion System",
        "success":True
    }

