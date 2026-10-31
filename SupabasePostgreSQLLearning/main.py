from fastapi import FastAPI,Path
from typing import Annotated
from contextlib import asynccontextmanager

from Configuration.supabaseClient import getDatabaseEngine, closeDatabaseConnections, getSessionFactory, Base
 
from Schemas.userSchemas import CreateUserRequest
from Schemas.productSchemas import CreateProductRequest , UpdateProductRequest

from Models.userModels import UserModel
from Models.productModels import ProductModel

from Utils.responceHelper import successResponse, errorResponse

from sqlalchemy import select,delete,update

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

@app.get("/")
def WelcomeMessage():
    return {
        "message":"Welcome to Postgre SQL Learning",
        "success":True
    }


@app.post("/create-user")
async def createUser(data: CreateUserRequest):

    try: 
        sessionFactory = getSessionFactory()

        async with sessionFactory() as db:
            resultEmail = await db.execute(select(UserModel).where(UserModel.email == data.email))

            if resultEmail.scalar_one_or_none():
                return errorResponse(409, "Email Already Exists", displayUi=True)
            
            resultUserName = await db.execute(select(UserModel).where(UserModel.username == data.username))
            
            if resultUserName.scalar_one_or_none():
                return errorResponse(409, "User Name Already Exists", displayUi=True)
            userData = data.model_dump() 
            
            new_user = UserModel(**userData)

            try:
                db.add(new_user)
                await db.commit()
            except Exception:
                await db.rollback() 
                return errorResponse(409, "Email or Username already exists ", displayUi=True)
            return successResponse(
                statusCode=201,  
                message="User created successfully",
                displayUi=True,
            )
    except Exception:
        return errorResponse(500, "Internal Server Error",displayUi=True)
    
@app.post("/create-product/{uid}")
async def createProduct(uid: Annotated[
        str, 
        Path(
            ..., 
            description="The UID of the user creating the product", 
            min_length=36, 
            max_length=36
        )
    ], data: CreateProductRequest):

    try:
        sessionFactory = getSessionFactory()

        async with sessionFactory() as db:
            
            userCheck = await db.execute(select(UserModel).where(UserModel.uid == uid))
            if not userCheck.scalar_one_or_none():
                return errorResponse(404, "User doesnot exist", displayUi=False)

            productData = data.model_dump()
            newProduct = ProductModel(**productData, uid=uid)

            try:
                db.add(newProduct)
                await db.commit()

                return successResponse(
                    statusCode=201,
                    message="Product created successfully",
                    displayUi=True,
                )

            except Exception:
                await db.rollback()
                return errorResponse(500, "Failed to create product", displayUi=True)

    except Exception:
        return errorResponse(500, "Internal Server Error", displayUi=True)
    

@app.delete("/delete-product/{pid}")
async def deleteProduct(
    pid: Annotated[
        str, 
        Path(
            ..., 
            description="The PID of the product to delete", 
            min_length=36, 
            max_length=36
        )
    ]
):
    try:
        sessionFactory = getSessionFactory()

        async with sessionFactory() as db:
            
            stmt = delete(ProductModel).where(ProductModel.pid == pid)
            result = await db.execute(stmt)
            
            await db.commit()

            if result.rowcount == 0:
                return errorResponse(404, "Product not found or already deleted", displayUi=True)

            return successResponse(
                statusCode=200,
                message="Product deleted successfully",
                displayUi=True
            )

    except Exception as e:
        return errorResponse(500, "Internal Server Error", displayUi=True)


@app.get("/get-products/{uid}")
async def getProductsByUser(
    uid: Annotated[
        str, 
        Path(
            ..., 
            description="The UID of the user to fetch products for", 
            min_length=36, 
            max_length=36
        )
    ]
):
    try:
        sessionFactory = getSessionFactory()

        async with sessionFactory() as db:
            
            # 1. Optional but recommended: Check if the user actually exists
            userCheck = await db.execute(select(UserModel).where(UserModel.uid == uid))
            if not userCheck.scalar_one_or_none():
                return errorResponse(404, "User not found", displayUi=False)

            # 2. Fetch products, sorted by pid descending (newest first)
            query = (
                select(ProductModel)
                .where(ProductModel.uid == uid)
                .order_by(ProductModel.pid.desc())
            )
            
            result = await db.execute(query)
            products = result.scalars().all()

            # 3. Format the response
            productList = [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "quantity": p.quantity,
                    "price": p.price
                }
                for p in products
            ]

            return successResponse(
                statusCode=200,
                message=f"Found {len(productList)} products",
                displayUi=False,
                data={"products": productList}
            )

    except Exception as e:
        return errorResponse(500, "Internal Server Error", displayUi=True)
    

@app.put("/update-product/{pid}")
async def updateProduct(
    pid: Annotated[
        str, 
        Path(
            ..., 
            description="The PID of the product to update", 
            min_length=36, 
            max_length=36
        )
    ],
    data: UpdateProductRequest
):
    try:
        sessionFactory = getSessionFactory()

        async with sessionFactory() as db:
            
            # 1. Extract only the fields the client actually provided
            updateData = data.model_dump(exclude_unset=True)

            if not updateData:
                return errorResponse(400, "No fields provided to update", displayUi=False)

            # 2. Execute a direct SQL UPDATE statement
            stmt = (
                update(ProductModel)
                .where(ProductModel.pid == pid)
                .values(**updateData)
            )
            
            result = await db.execute(stmt)
            await db.commit()

            # 3. Check if a row was actually updated
            if result.rowcount == 0:
                return errorResponse(404, "Product not found", displayUi=True)

            return successResponse(
                statusCode=200,
                message="Product updated successfully",
                displayUi=True,
                data=updateData
            )

    except Exception:
        
        return errorResponse(500, "Internal Server Error", displayUi=True)