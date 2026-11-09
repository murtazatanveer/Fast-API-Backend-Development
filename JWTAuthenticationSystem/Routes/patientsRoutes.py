from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from Controllers.patientsController import (
    createPatientController,
    deletePatientController,
    getPatientByIdController,
    getPatientsController,
    sortPatientsController,
    updatePatientController,
)
from Dependencies.authDependency import verifyAccessToken
from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import Patient as PatientSchema
from Schemas.patientsSchema import UpdatePatient

patientsRouter = APIRouter(prefix="/patients", tags=["Patients"])


@patientsRouter.post("", status_code=201)
async def createPatientRoute(
    payload: PatientSchema,
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await createPatientController(payload, current_user)


@patientsRouter.get("", status_code=200)
async def getPatientsRoute(
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await getPatientsController(current_user)


@patientsRouter.get("/sorted", status_code=200)
async def sortPatientsRoute(
    sort_by: Annotated[
        str,
        Query(
            ...,
            alias="sortBy",
            description="Sort on the basis of height, weight or bmi",
        ),
    ],
    order: Annotated[
        str, Query(description="Sort in asc or desc order")
    ] = "asc",
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await sortPatientsController(sort_by, order, current_user)


@patientsRouter.get("/{patientId}", status_code=200)
async def getPatientByIdRoute(
    patient_id: Annotated[
        str,
        Path(
            ...,
            alias="patientId",
            pattern=r"^P\d{3}$",
            description="ID of Patient in the DB",
            examples=["P001"],
        ),
    ],
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await getPatientByIdController(patient_id, current_user)


@patientsRouter.put("/{patientId}", status_code=200)
async def updatePatientRoute(
    patient_id: Annotated[
        str,
        Path(
            ...,
            alias="patientId",
            pattern=r"^P\d{3}$",
            description="ID of Patient in the DB",
            examples=["P001"],
        ),
    ],
    payload: UpdatePatient,
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await updatePatientController(patient_id, payload, current_user)


@patientsRouter.delete("/{patientId}", status_code=200)
async def deletePatientRoute(
    patient_id: Annotated[
        str,
        Path(
            ...,
            alias="patientId",
            pattern=r"^P\d{3}$",
            description="ID of Patient in the DB",
            examples=["P001"],
        ),
    ],
    current_user: AccessTokenPayload = Depends(verifyAccessToken),
):
    return await deletePatientController(patient_id, current_user)
