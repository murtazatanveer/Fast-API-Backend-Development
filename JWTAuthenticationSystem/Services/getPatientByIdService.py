from sqlalchemy import select

from Configuration.supabaseClient import getSessionFactory
from Models.patientModel import Patient
from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import PatientResponse
from Utils.errors import ServiceError


async def getPatientById(
    patient_id: str, current_user: AccessTokenPayload
) -> dict:
    session_factory = getSessionFactory()
    async with session_factory() as db:
        result = await db.execute(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.created_by == current_user.user_id,
            )
        )
        patient = result.scalar_one_or_none()

        if patient is None:
            raise ServiceError(
                404, "Patient ID does not exist", display_ui=True
            )

        return PatientResponse.model_validate(patient).model_dump(
            by_alias=True, mode="json"
        )
