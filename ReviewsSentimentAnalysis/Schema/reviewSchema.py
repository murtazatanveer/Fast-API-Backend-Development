from pydantic import BaseModel, Field
from typing import Annotated , Dict
class Review(BaseModel):
    review: Annotated[str,Field(..., min_length=5, max_length=800,description="Customer review text",examples=["This place was amazing"])]

class PredictionResponce(BaseModel):
    message:Annotated[str,Field(...,description="Responce message of Prediction endpoint")]
    success:Annotated[bool,Field(...,description="Returns True or False depending upon the responce")]
    prediction:Annotated[Dict[str,int],Field(...,description="Prediction Resutls dictionary")]