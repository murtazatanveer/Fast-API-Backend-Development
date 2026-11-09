from sqlalchemy import select

from Configuration.supabaseClient import getSessionFactory
from Models.patientModel import Patient
from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import PatientResponse


async def getPatients(current_user: AccessTokenPayload) -> list[dict]:
    session_factory = getSessionFactory()
    async with session_factory() as db:
        result = await db.execute(
            select(Patient)
            .where(Patient.created_by == current_user.user_id)
            .order_by(Patient.id.asc())
        )
        patients = result.scalars().all()

        return [
            PatientResponse.model_validate(patient).model_dump(
                by_alias=True, mode="json"
            )
            for patient in patients
        ]
