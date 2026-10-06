from fastapi import APIRouter
from backend.app.db.database import engine

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health():
    database_status = "UP"
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except Exception:
        database_status = "DOWN"
    return {
        "status": "UP" if database_status == "UP" else "DEGRADED",
        "database": database_status,
    }
