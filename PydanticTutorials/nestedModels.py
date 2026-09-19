from pydantic import BaseModel,Field
from typing import Annotated,Literal,Optional

class Address(BaseModel):
    city:Annotated[str,Field(max_length=30,title="City Name")]
    state:Annotated[str,Field(max_length=30,title="State Name")]
    pincode:int

class Patient(BaseModel):
    name: Annotated[str,Field(max_length=50,title="Patient Name",description="The full name of the patient")]
    age: Annotated[int,Field(gt=0, lt=81,strict=True)]
    gender: Annotated[Optional[Literal["male", "female"]],Field(default="male")]
    address:Address


patientAddress={
    "city":"P.D Khan",
    "state":"Jhelum",
    "pincode":4900
}

A1 = Address(**patientAddress)

patientName={
    "name":"Murtaza",
    "age":23,
    "address":A1
}

P1 = Patient(**patientName)

print(P1,"\t",type(P1))

temp = P1.model_dump()

print(temp,"\t",type(temp))

