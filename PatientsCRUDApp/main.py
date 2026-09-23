# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Query,Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel,computed_field,Field
from typing import Annotated,Literal,Optional
from google.cloud import firestore

from config import settings                       # MUST be first
from firestore_client import get_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the client at startup
    db = get_db()
    print(f"✅ Firestore client ready → {settings.gcp_project_id}")
    yield
    await close_db()
    print("🔌 Firestore client closed")


app = FastAPI(
    title="Patients CRUD API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def welcomeMessage():
    return {"message":"Welcome to Patients CRUD App Using Firestore","success":True}

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
async def createPatient(patient: Patient):

    try:
        db = get_db()

        doc_ref = db.collection("Patients").document(patient.id)

        snap = await doc_ref.get()

        if snap.exists:
            return JSONResponse(
                status_code=409,
                content={"message": "Patient ID already exists", "success": False}
            )

        await doc_ref.set(patient.model_dump(exclude=["id"]))

        return JSONResponse(
            status_code=201,
            content={
                "message": "Patient Created Successfully",
                "success": True,
                "docId": doc_ref.id,
                "docPath": doc_ref.path,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/patients")
async def getPatients():
    try:
        db = get_db()
        docs = db.collection("Patients").stream()

        patients = []
        async for doc in docs:
            data = doc.to_dict()           
            data["id"] = doc.id            
            patients.append(data)

        return JSONResponse(status_code=200,content={"message":"All Patients Data","success":True,"data":patients})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sort-patients")
async def sortPatients(sortBy:str = Query(...,description="Sort on the basis of height , weight or bmi"), order:str=Query("asc",description="Sort in asc or desc order")):
    
    try:
        sortByFields = ["height","weight","bmi"]
        orderFields = ["asc","desc"]

        if sortBy not in sortByFields:
            return JSONResponse(status_code=400,content={"message":f'Invalid sortby field select from {sortByFields}',"success":False})
        
        if order not in orderFields:
            return JSONResponse(status_code=400,content={"message":f'Invalid order field select from {orderFields}',"success":False})

        db = get_db()

        direction = firestore.Query.ASCENDING if order == "asc" else firestore.Query.DESCENDING

        query = db.collection("Patients").order_by(sortBy, direction=direction)

        patients = []
        async for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            patients.append(data)
        
        return JSONResponse(status_code=200,content={"message":f'Sorted Patients Fetched on the basis of {sortBy} and order is {order}',"success":False,"data":patients})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patient/{patientId}")
async def getPatientWithId(patientId:Annotated[str, Path(..., pattern=r"^P\d{3}$", description="ID of Patient in the DB", examples=["P001"])]):

    try:
        db=get_db()
        doc_ref = db.collection("Patients").document(patientId)
        snap = await doc_ref.get()

        if not snap.exists:
            return JSONResponse(
                status_code=404,
                content={"message": "Patient ID doesnot exists", "success": False}
            )
        
        return JSONResponse(status_code=200,content={"message":"Patient Found", "success": True , "data":snap.to_dict(),"docId":snap.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class UpdatePatient(BaseModel):
    name : Annotated[Optional[str],Field(default=None,max_length=50,description='Name of the patient')]
    city: Annotated[Optional[str],Field(default=None,max_length=50,description='City where the patient is living')]
    age: Annotated[Optional[int],Field(default=None,gt=0,lt=81,description="Patient Age",strict=True)]
    gender:Annotated[Optional[Literal["male","female","other"]],Field(default=None,description="Gender of the patient; male, female or other")]
    height:Annotated[Optional[float],Field(default=None,gt=0,description="Patient height in meters",strict=True)]
    weight:Annotated[Optional[float],Field(default=None,gt=0,description="Patient height in kg's",strict=True)]

@app.put("/update-patient/{patientId}")
async def updatePatient(
    patientId: Annotated[
        str,
        Path(..., pattern=r"^P\d{3}$", description="ID of Patient in the DB", examples=["P001"]),
    ],
    patient: UpdatePatient,
):
    try:
        db = get_db()
        doc_ref = db.collection("Patients").document(patientId)
        snap = await doc_ref.get()

        if not snap.exists:
            return JSONResponse(
                status_code=404,
                content={"message": "Patient ID does not exist", "success": False},
            )

        # 1. Only fields the client sent (drop None)
        updatedPatient = patient.model_dump(exclude_none=True)

        if not updatedPatient:
            return JSONResponse(
                status_code=400,
                content={"message": "No fields to update", "success": False},
            )

        # 2. Merge with existing doc
        currentPatient = snap.to_dict()
        tempPatient = {**currentPatient, **updatedPatient}
        tempPatient["id"] = patientId

        # 3. Recompute bmi and verdict  (⚠️ FIX: exclude={"id"} with braces)
        newPatient = Patient(**tempPatient).model_dump(exclude={"id"})

        # 4. Write: client changes + recomputed fields + timestamp
        write_payload = {
            **updatedPatient,
            "bmi": newPatient["bmi"],
            "verdict": newPatient["verdict"],
       
        }

        await doc_ref.update(write_payload)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Patient updated successfully",
                "success": True,
                "docId": doc_ref.id,
                "updated_fields": list(updatedPatient.keys()),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-patient/{patientId}")
async def deletePatient(patientId:Annotated[str, Path(..., pattern=r"^P\d{3}$", description="ID of Patient in the DB", examples=["P001"])]):
    try:
        db=get_db()
        doc_ref = db.collection("Patients").document(patientId)
        snap = await doc_ref.get()

        if not snap.exists:
            return JSONResponse(
                status_code=404,
                content={"message": "Patient ID doesnot exists", "success": False}
            )
        await doc_ref.delete()
        return JSONResponse(status_code=200,content={"message":"Patient Deleted Successfully", "success": True , "docId":doc_ref.id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
