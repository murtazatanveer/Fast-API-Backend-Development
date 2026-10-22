# firestore_client.py
from google.cloud import firestore
from Configuration.config import settings

_db: firestore.AsyncClient | None = None


def get_db() -> firestore.AsyncClient:
    global _db
    if _db is None:
        _db = firestore.AsyncClient(
            project=settings.gcp_project_id,
            database=settings.firestore_database,
        )
    return _db


def close_db() -> None:
    global _db
    if _db is not None:
        _db.close()          
        _db = None