from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

class UserRegister(BaseModel):
    username: Annotated[str,Field(..., description="Enter Username", min_length=8, max_length=30)] 
    email: Annotated[EmailStr,Field(...,description="Enter Email")]
    password: Annotated[str,Field(..., min_length=8, max_length=20)]

class UserLogin(BaseModel):
    username: Annotated[str,Field(..., description="Enter Username", min_length=8, max_length=30)]
    password: Annotated[str,Field(..., min_length=8, max_length=20)]