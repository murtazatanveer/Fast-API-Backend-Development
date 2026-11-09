import logging

from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import Patient as PatientSchema
from Schemas.patientsSchema import UpdatePatient
from Services.createPatientService import createPatient
from Services.deletePatientService import deletePatient
from Services.getPatientByIdService import getPatientById
from Services.getPatientsService import getPatients
from Services.sortPatientsService import sortPatients
from Services.updatePatientService import updatePatient
from Utils.errors import ServiceError
from Utils.responceHelper import errorResponse, successResponse

logger = logging.getLogger(__name__)


async def createPatientController(
    payload: PatientSchema, current_user: AccessTokenPayload
):
    try:
        await createPatient(payload, current_user)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Create patient failed")
        return errorResponse(500, "Server is not responding. Please try again later", displayUi=True)

    return successResponse(
        201,
        "Patient Created Successfully",
        displayUi=True,
    )


async def getPatientsController(current_user: AccessTokenPayload):
    try:
        patients = await getPatients(current_user)
    except Exception:
        logger.exception("Get patients failed")
        return errorResponse(
            500,
            "Server is not responding. Please try again later",
            displayUi=False,
        )

    return successResponse(
        200,
        "Patients fetched successfully",
        displayUi=False,
        data=patients,
    )


async def sortPatientsController(
    sort_by: str, order: str, current_user: AccessTokenPayload
):
    try:
        patients = await sortPatients(sort_by, order, current_user)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Sort patients failed")
        return errorResponse(
            500,
            "Server is not responding. Please try again later",
            displayUi=False,
        )

    return successResponse(
        200,
        f"Patients sorted by {sort_by} in {order} order",
        displayUi=False,
        data=patients,
    )


async def getPatientByIdController(
    patient_id: str, current_user: AccessTokenPayload
):
    try:
        patient = await getPatientById(patient_id, current_user)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Get patient by ID failed")
        return errorResponse(
            500,
            "Server is not responding. Please try again later",
            displayUi=False,
        )

    return successResponse(
        200,
        "Patient Found",
        displayUi=True,
        data=patient,
    )


async def updatePatientController(
    patient_id: str,
    payload: UpdatePatient,
    current_user: AccessTokenPayload,
):
    try:
        result = await updatePatient(patient_id, payload, current_user)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Update patient failed")
        return errorResponse(
            500,
            "Server is not responding. Please try again later",
            displayUi=False,
        )

    return successResponse(
        200,
        "Patient updated successfully",
        displayUi=True,
        data={
            "docId": result["patient_id"],
            "updatedFields": result["updated_fields"],
        },
    )


async def deletePatientController(
    patient_id: str, current_user: AccessTokenPayload
):
    try:
        result = await deletePatient(patient_id, current_user)
    except ServiceError as exc:
        return errorResponse(exc.status_code, exc.message, displayUi=exc.display_ui)
    except Exception:
        logger.exception("Delete patient failed")
        return errorResponse(
            500,
            "Server is not responding. Please try again later",
            displayUi=False,
        )

    return successResponse(
        200,
        "Patient Deleted Successfully",
        displayUi=True,
        data={"docId": result["patient_id"]},
    )
