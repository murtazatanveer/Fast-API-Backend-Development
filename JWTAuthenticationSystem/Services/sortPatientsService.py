from sqlalchemy import select

from Configuration.supabaseClient import getSessionFactory
from Models.patientModel import Patient
from Schemas.authSchema import AccessTokenPayload
from Schemas.patientsSchema import PatientResponse
from Utils.errors import ServiceError

SORT_FIELDS = ["height", "weight", "bmi"]
ORDER_FIELDS = ["asc", "desc"]
SORT_COLUMNS = {
    "height": Patient.height,
    "weight": Patient.weight,
    "bmi": Patient.bmi,
}


async def sortPatients(
    sort_by: str, order: str, current_user: AccessTokenPayload
) -> list[dict]:
    if sort_by not in SORT_FIELDS:
        raise ServiceError(
            400,
            f"Invalid sortBy field. Select from {SORT_FIELDS}",
            display_ui=True,
        )

    if order not in ORDER_FIELDS:
        raise ServiceError(
            400,
            f"Invalid order field. Select from {ORDER_FIELDS}",
            display_ui=True,
        )

    sort_column = SORT_COLUMNS[sort_by]
    direction = sort_column.asc() if order == "asc" else sort_column.desc()

    session_factory = getSessionFactory()
    async with session_factory() as db:
        result = await db.execute(
            select(Patient)
            .where(Patient.created_by == current_user.user_id)
            .order_by(direction, Patient.id.asc())
        )
        patients = result.scalars().all()

        return [
            PatientResponse.model_validate(patient).model_dump(
                by_alias=True, mode="json"
            )
            for patient in patients
        ]
