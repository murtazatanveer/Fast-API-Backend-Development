import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class CreateProductRequest(BaseModel):
    
    name: str = Field(..., min_length=1, max_length=100,description="The Name of the product")
    
    quantity: int = Field(..., ge=0,description="The UID of the user creating theproduct")
    price: int = Field(..., ge=0)

    @field_validator('name')
    @classmethod
    def validateName(cls, value: str) -> str:
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise ValueError("Product name must contain alphabetic characters and spaces only.")
        return value


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[int] = Field(None, ge=0)

    @field_validator('name')
    @classmethod
    def validateName(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not re.match(r'^[a-zA-Z\s]+$', value):
                raise ValueError("Product name must contain alphabetic characters and spaces only.")
        return value
