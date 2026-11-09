from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from Configuration.supabaseClient import getSessionFactory
from Models.patientModel import Patient
from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import Patient as PatientSchema
from Utils.errors import ServiceError


async def createPatient(
    payload: PatientSchema, current_user: AccessTokenPayload
) -> dict:
    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
            existing_patient = await db.execute(
                select(Patient).where(Patient.id == payload.id)
            )
            if existing_patient.scalar_one_or_none() is not None:
                raise ServiceError(
                    409, "Patient ID already exists", display_ui=True
                )

            patient = Patient(
                id=payload.id,
                name=payload.name,
                city=payload.city,
                age=payload.age,
                gender=payload.gender,
                height=payload.height,
                weight=payload.weight,
                bmi=payload.bmi,
                verdict=payload.verdict,
                created_by=current_user.user_id,
            )
            db.add(patient)

            await db.commit()

        except ServiceError:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            raise ServiceError(409, "Patient ID already exists", display_ui=True)
        except Exception:
            await db.rollback()
            raise
