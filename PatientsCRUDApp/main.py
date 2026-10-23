# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Query,Path,Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel,computed_field,Field
from typing import Annotated,Literal,Optional
from google.cloud import firestore

from Configuration.config import settings                       
from Configuration.firestore_client import get_db, close_db

from Dependencies.authDependency import getCurrentUser

from Utils.responseHelper import errorResponse,successResponse

from routes import authRoutes

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db()
    print(f"✅ Firestore client ready → {settings.gcp_project_id}")
    yield
    close_db()
    print("🔌 Firestore client closed")


app = FastAPI(
    title="Patients CRUD API",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def welcomeMessage():
    return {"message":"Welcome to Patients CRUD App Using Firestore","success":True}

app.include_router(authRoutes.router)

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
async def createPatient(patient: Patient, currentUser: dict = Depends(getCurrentUser)):
    try:
        db = get_db()
        doc_ref = db.collection("Patients").document(patient.id)
        snap = await doc_ref.get()

        # 1. Check if Patient ID already exists
        if snap.exists:
            return errorResponse(
                statusCode=409,
                message="Patient ID already exists",
                displayUi=True
            )

        # 2. Prepare the data
        patientData = patient.model_dump(exclude=["id"])
        patientData["createdBy"] = currentUser["id"]

        # 3. Save to Firestore
        await doc_ref.set(patientData)

        # 4. Return Success
        return successResponse(
            statusCode=201,
            message="Patient Created Successfully",
            data={
                "docId": doc_ref.id,
                "docPath": doc_ref.path,
                "createdBy": currentUser["id"]
            },
            displayUi=True
        )

    except Exception as e:
        return errorResponse(
            statusCode=500,
            message="An unexpected error occurred while creating the patient.",
            displayUi=False
        )
    
@app.get("/patients")
async def getPatients(currentUser: dict = Depends(getCurrentUser)):
    try:
        db = get_db()

        # 1. Query only the patients created by the logged-in user
        query = db.collection("Patients").where(
            filter=firestore.FieldFilter("createdBy", "==", currentUser["id"])
        )
        docs = query.stream()

        patients = []
        async for doc in docs:
            data = doc.to_dict()           
            data["id"] = doc.id            
            patients.append(data)

        # 2. Return success response
        return successResponse(
            statusCode=200,
            message="Patients fetched successfully",
            data=patients,
            displayUi=False
        )

    except Exception as e:
        # 3. Return error response
        return errorResponse(
            statusCode=500,
            message="An error occurred while fetching patients",
            displayUi=False
        )

@app.get("/sort-patients")
async def sortPatients(
    sortBy: str = Query(..., description="Sort on the basis of height, weight or bmi"), 
    order: str = Query("asc", description="Sort in asc or desc order"),
    currentUser: dict = Depends(getCurrentUser)
):
    try:
        sortByFields = ["height", "weight", "bmi"]
        orderFields = ["asc", "desc"]

        # 1. Validate Query Parameters
        if sortBy not in sortByFields:
            return errorResponse(
                statusCode=400,
                message=f"Invalid sortBy field. Select from {sortByFields}",
                displayUi=True
            )
        
        if order not in orderFields:
            return errorResponse(
                statusCode=400,
                message=f"Invalid order field. Select from {orderFields}",
                displayUi=True
            )

        db = get_db()
        direction = firestore.Query.ASCENDING if order == "asc" else firestore.Query.DESCENDING

        # 2. Combine the Filter (by user) and the Sort (by query)
        query = (
            db.collection("Patients")
            .where(filter=firestore.FieldFilter("createdBy", "==", currentUser["id"]))
            .order_by(sortBy, direction=direction)
        )

        patients = []
        async for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            patients.append(data)
        
        # 3. Return Success
        return successResponse(
            statusCode=200,
            message=f"Patients sorted by {sortBy} in {order} order",
            data=patients,
            displayUi=False
        )

    except Exception as e:
        # 3. Return Error
        return errorResponse(
            statusCode=500,
            message="An error occurred while sorting patients",
            displayUi=False
        )


@app.get("/patient/{patientId}")
async def getPatientWithId(
    patientId: Annotated[str, Path(..., pattern=r"^P\d{3}$", description="ID of Patient in the DB", examples=["P001"])],
    currentUser: dict = Depends(getCurrentUser) # <-- 1. Auth Dependency
):
    try:
        db = get_db()
        doc_ref = db.collection("Patients").document(patientId)
        snap = await doc_ref.get()

        # 2. Error Response if not found
        if not snap.exists:
            return errorResponse(
                statusCode=404,
                message="Patient ID does not exist",
                displayUi=True
            )
        
        # 3. Success Response
        patientData = snap.to_dict()
        patientData["id"] = snap.id

        return successResponse(
            statusCode=200,
            message="Patient Found",
            data=patientData,
            displayUi=True
        )

    except Exception as e:
        # 4. Error Response for server failure
        return errorResponse(
            statusCode=500,
            message="An error occurred while fetching the patient",
            displayUi=False
        )
    
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
    currentUser: dict = Depends(getCurrentUser) # <-- Auth Dependency
):
    try:
        db = get_db()
        doc_ref = db.collection("Patients").document(patientId)
        snap = await doc_ref.get()

        if not snap.exists:
            return errorResponse(
                statusCode=404,
                message="Patient ID does not exist",
                displayUi=True
            )

        # 1. Only fields the client sent (drop None)
        updatedPatient = patient.model_dump(exclude_none=True)

        if not updatedPatient:
            return errorResponse(
                statusCode=400,
                message="No fields to update",
                displayUi=True
            )

        # 2. Merge with existing doc
        currentPatient = snap.to_dict()
        tempPatient = {**currentPatient, **updatedPatient}
        tempPatient["id"] = patientId

        # 3. Recompute bmi and verdict
        newPatient = Patient(**tempPatient).model_dump(exclude={"id"})

        # 4. Write: client changes + recomputed fields
        write_payload = {
            **updatedPatient,
            "bmi": newPatient["bmi"],
            "verdict": newPatient["verdict"],
        }

        await doc_ref.update(write_payload)

        return successResponse(
            statusCode=200,
            message="Patient updated successfully",
            data={
                "docId": doc_ref.id,
                "updatedFields": list(updatedPatient.keys())
            },
            displayUi=True
        )

    except Exception as e:
        return errorResponse(
            statusCode=500,
            message="An error occurred while updating the patient",
            displayUi=False
        )
    

@app.delete("/delete-patient/{patientId}")
async def deletePatient(
    patientId: Annotated[str, Path(..., pattern=r"^P\d{3}$", description="ID of Patient in the DB", examples=["P001"])],
    currentUser: dict = Depends(getCurrentUser) # <-- Auth Dependency
):
    try:
        db = get_db()
        doc_ref = db.collection("Patients").document(patientId)
        snap = await doc_ref.get()

        if not snap.exists:
            return errorResponse(
                statusCode=404,
                message="Patient ID does not exist",
                displayUi=True
            )
            
        await doc_ref.delete()
        
        return successResponse(
            statusCode=200,
            message="Patient Deleted Successfully",
            data={"docId": doc_ref.id},
            displayUi=True
        )
        
    except Exception as e:
        return errorResponse(
            statusCode=500,
            message="An error occurred while deleting the patient",
            displayUi=False
        )
