import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional,Annotated

class CreateUserRequest(BaseModel):
    fullName: Annotated [str , Field(..., min_length=2, max_length=50,description="Enter Full Name")]
    
    username: Annotated [str , Field(..., min_length=8, max_length=50,description="Enter Username")]
    
    email: Annotated [EmailStr,Field(...,description="Enter User Email")]
        
    isMarried: Annotated[Optional[bool],Field(default=True,description="Is the User Married or not")]
    height: Annotated[Optional[float], Field(default=None)]
    weight: Annotated[Optional[float], Field(default=None)]

    @field_validator('fullName')
    @classmethod
    def validateFullName(cls, value: str) -> str:
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValueError("Full name may only contain alphabetic characters and spaces.")
        return value

    @field_validator('username')
    @classmethod
    def validateUsername(cls, value: str) -> str:
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$]).{8,}$'
        
        if not re.match(pattern, value):
            raise ValueError(
                "Username must be at least 8 characters long and include at least one uppercase letter, "
                "one lowercase letter, one number, and one special character (@ or $)."
            )
        return value
