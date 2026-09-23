from fastapi import FastAPI ,HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated , Literal , Optional
import json

def load_data():
    with open ("patients.json","r") as f:
        data=json.load(f)
        
    print("Patients Data Fetched from JSON File")
    return data;

data=load_data();

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

app = FastAPI()

@app.get("/")
def welcome():
    return {"message":"Welcome to Patients Management System","success":True}


@app.get("/patients")
def getPatients():
    print("Patients Data Retured to the Client")
    return {"message":"Patients Data Fetched","success":True,"data":data}

@app.get("/patient/{patientId}")
def getPatientWithId(patientId:str=Path(...,description="Id of Patient in the DB",examples=["P001"])):
    if patientId in data:
        print("Patient Found for Id ",patientId)
        return {"message":"Patient Found","success":True,"patient":data[patientId]}
    else:
        print("Patient Id ",patientId,"! doesnot Found")
        raise HTTPException(status_code=404,detail={"message":"Patient doesnot exist","success":False})


@app.get("/sort-patients")
def sortPatients(sortBy:str = Query(...,description="Sort on the basis of height , weight or bmi"), order:str=Query("asc",description="Sort in asc or desc order")):

    sortByFields = ["height","weight","bmi"]
    orderFields = ["asc","desc"]

    if sortBy not in sortByFields:
        raise HTTPException(status_code=400,detail={"message":f'Invalid sortby field select from {sortByFields}',"success":False})
        
    if order not in orderFields:
        raise HTTPException(status_code=400,detail={"message":f'Invalid order field select from {orderFields}',"success":False})

    sorted_data = dict(
    sorted(data.items(), key=lambda item: item[1][sortBy], reverse= True if order=="desc" else False)
    )    

    return {"message":f'Sorted Patients Fetched on the basis of {sortBy} and order is {order}',"success":True,"data":sorted_data}

class Patient(BaseModel):
    id : Annotated[str,Field(...,pattern=r"^P\d{3}$",description='ID of the patient', examples=['P001'])]
    name : Annotated[str,Field(...,max_length=50,description='Name of the patient')]
    city: Annotated[str,Field(...,max_length=50,description='City where the patient is living')]
    age: Annotated[int,Field(...,gt=0,lt=81,description="Patient Age",strict=True)]
    gender:Annotated[Literal["male","female","other"],Field(...,description="Gender of the patient; male, female or other")]
    height:Annotated[float,Field(...,gt=0,description="Patient height in meters",strict=True)]
    weight:Annotated[float,Field(...,gt=0,description="Patient height in kg's",strict=True)]

    @computed_field
    @property
    def bmi(self)->float: 
        return round(self.weight/(self.height**2),2)
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"


@app.post("/create-patient")
def createPatient(patient:Patient):
    
    if patient.id in data:
        # raise HTTPException(status_code=400,detail={"message":"Patient already exists","success":False})
        return JSONResponse(status_code=400,content={"message":"Patient already exists","success":False})

    newPatient = patient.model_dump(exclude=["id"])

    data[patient.id] = newPatient

    save_data(data)
    
    return JSONResponse(status_code=201,content={"message":"Patient Created Successfully","success":True,"data":newPatient})

class UpdatePatient(BaseModel):
    name : Annotated[Optional[str],Field(default=None,max_length=50,description='Name of the patient')]
    city: Annotated[Optional[str],Field(default=None,max_length=50,description='City where the patient is living')]
    age: Annotated[Optional[int],Field(default=None,gt=0,lt=81,description="Patient Age",strict=True)]
    gender:Annotated[Optional[Literal["male","female","other"]],Field(default=None,description="Gender of the patient; male, female or other")]
    height:Annotated[Optional[float],Field(default=None,gt=0,description="Patient height in meters",strict=True)]
    weight:Annotated[Optional[float],Field(default=None,gt=0,description="Patient height in kg's",strict=True)]

@app.put("/update-patient/{patientId}")
def updatePatient(patient:UpdatePatient,patientId:str=Path(...,description="Id of Patient in the DB",examples=["P001"])):
    print(patientId)

    if patientId not in data:
        raise HTTPException(status_code=404,detail={"message":"Patient doesnot exist","success":False})
    
    updatedPatient=patient.model_dump(exclude_unset=True);

    existingPatient = data[patientId]

    for key,value in updatedPatient.items():
        existingPatient[key] = value
    
    existingPatient["id"]=patientId
    existingPatient=Patient(**existingPatient).model_dump(exclude='id')

    data[patientId] = existingPatient

    save_data(data)
    
    return JSONResponse(status_code=200,content={"message":"Patient Updated Successfully","success":True,"data":existingPatient})

@app.delete("/remove-patient/{patientId}")
def deletePatient(patientId:str=Path(...,description="Id of Patient in the DB",examples=["P001"])):

    if patientId not in data:
        raise HTTPException(status_code=404,detail={"message":"Patient doesnot exist","success":False})
    
    delPatient = data[patientId]
    del data[patientId]

    save_data(data)

    return JSONResponse(status_code=200,content={"message":"Patient Deleted Successfully","success":True,"data":delPatient})


# @app.get("/exception-example")
# def exceptionExample():
#     a=10/0
#     return {"message":"Request Success","A value":a}







