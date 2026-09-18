from fastapi import FastAPI ,HTTPException, Path, Query
import json

def load_data():
    with open ("patients.json","r") as f:
        data=json.load(f)
        
    print("Patients Data Fetched from JSON File")
    return data;

data=load_data();

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




