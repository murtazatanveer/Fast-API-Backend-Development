from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, computed_field

from Schemas.authSchema import CamelModel


class PatientBase(CamelModel):
    name: str = Field(max_length=50)
    city: str = Field(max_length=50)
    age: Annotated[int, Field(gt=0, lt=81, strict=True)]
    gender: Literal["male", "female", "other"]
    height: Annotated[float, Field(gt=0, strict=True)]
    weight: Annotated[float, Field(gt=0, strict=True)]


class Patient(PatientBase):
    id: Annotated[str, Field(pattern=r"^P\d{3}$")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"


class UpdatePatient(CamelModel):
    name: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=50)
    age: Annotated[int, Field(gt=0, lt=81, strict=True)] | None = None
    gender: Literal["male", "female", "other"] | None = None
    height: Annotated[float, Field(gt=0, strict=True)] | None = None
    weight: Annotated[float, Field(gt=0, strict=True)] | None = None


class PatientResponse(PatientBase):
    id: Annotated[str, Field(pattern=r"^P\d{3}$")]
    bmi: float
    verdict: str
    created_by: UUID
