from sqlalchemy import select

from Configuration.supabaseClient import getSessionFactory
from Models.patientModel import Patient
from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import Patient as PatientSchema
from Schemas.patientsSchema import UpdatePatient
from Utils.errors import ServiceError


async def updatePatient(
    patient_id: str, payload: UpdatePatient, current_user: AccessTokenPayload
) -> dict:
    updated_fields = payload.model_dump(exclude_none=True)

    if not updated_fields:
        raise ServiceError(400, "No fields to update", display_ui=True)

    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
            result = await db.execute(
                select(Patient)
                .where(
                    Patient.id == patient_id,
                    Patient.created_by == current_user.user_id,
                )
                .with_for_update()
            )
            patient = result.scalar_one_or_none()

            if patient is None:
                raise ServiceError(
                    404, "Patient ID does not exist", display_ui=True
                )

            merged_patient = {
                "id": patient.id,
                "name": patient.name,
                "city": patient.city,
                "age": patient.age,
                "gender": patient.gender,
                "height": patient.height,
                "weight": patient.weight,
            }
            merged_patient.update(updated_fields)

            recomputed_patient = PatientSchema(**merged_patient)

            for field_name, value in updated_fields.items():
                setattr(patient, field_name, value)
            patient.bmi = recomputed_patient.bmi
            patient.verdict = recomputed_patient.verdict

            await db.commit()

            return {
                "patient_id": patient.id,
                "updated_fields": list(updated_fields.keys()),
            }
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
