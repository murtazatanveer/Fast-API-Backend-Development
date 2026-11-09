from sqlalchemy import select

from Configuration.supabaseClient import getSessionFactory
from Models.patientModel import Patient
from Schemas.authSchema import AccessTokenPayload
from Utils.errors import ServiceError


async def deletePatient(
    patient_id: str, current_user: AccessTokenPayload
) -> dict:
    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
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

            await db.delete(patient)
            await db.commit()

            return {"patient_id": patient.id}
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
