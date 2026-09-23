# firestore_client.py
from google.cloud import firestore
from config import settings

_db: firestore.AsyncClient | None = None


def get_db() -> firestore.AsyncClient:
    """Return a singleton async Firestore client."""
    global _db
    if _db is None:
        _db = firestore.AsyncClient(
            project=settings.gcp_project_id,
            database=settings.firestore_database,
        )
    return _db


async def close_db() -> None:
    """Close the Firestore client on app shutdown."""
    global _db
    if _db is not None:
        _db.close()          # ← NOT awaited
        _db = None