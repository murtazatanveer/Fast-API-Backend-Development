# verify_firestore.py  (TEMPORARY — delete after it passes)
from config import settings

from google.cloud import firestore

print("→ Connecting...")
print(f"   project  : {settings.gcp_project_id}")
print(f"   database : {settings.firestore_database}")

db = firestore.Client()
print(f"   client.project = {db.project}")

try:
    list(db.collection("connectivity_test").limit(1).stream())
    print("✅ Firestore connection OK")
except Exception as e:
    print(f"❌ {type(e).__name__}: {e}")
    raise