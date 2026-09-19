from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator, model_validator
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name: Annotated[str,Field(max_length=50,title="Patient Name",description="The full name of the patient")]
    age: Annotated[int,Field(gt=0, lt=81,strict=True)]
    email: EmailStr
    linkedinUrl: Annotated[Optional[AnyUrl] , Field(default=None)]
    isMarried: Annotated[Optional[bool],Field(default=True,description="Is the Petient Married or not")];
    weight: Annotated[float , Field(gt=3)]
    allergies: Annotated[Optional[List[str]] , Field(default=None, max_length=5)]
    contactDetails: Dict[str, str]

    @field_validator("email")
    @classmethod
    def emailValidator(cls,value,):

        validDomainNames=["ici.com","hbl.com"]

        if value.split("@")[-1] not in validDomainNames:
            raise ValueError("Not a Valid Domain")

        return value;

    @field_validator("name",mode="before")
    @classmethod
    def transformName(cls,value):
        return value.upper()

    @model_validator(mode="after")
    def validateEmergencyContact(cls,model):
        if model.age>60 and "emergencyNo" not in model.contactDetails:
            raise ValueError("Age is greator then 60 but emergency contact no is not provided")
        return model;


patientData = {
    "name": "Murtaza",
    "age": 65,
    "linkedinUrl": "https://www.linkedin.com/",
    "isMarried":False,
    "email": "murtaza@ici.com",
    "weight": 70,
    "allergies": ["Avocado", "Venoms", "mold spores"],
    "contactDetails": {
        "cell no": "12345678",
        "address": "Abbottabad",
        "emergencyNo":"87654321"
    }
}

p1 = Patient(**patientData)

def addPatientData(patient: Patient):
    print(patient, "\nData Added")
addPatientData(p1)