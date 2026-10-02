from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("", include_in_schema=False)
@router.get("/")
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
