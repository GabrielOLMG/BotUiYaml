from fastapi import APIRouter
router = APIRouter()

# =========================
# Endpoint 1: health check
# =========================
@router.get("/")
def root():
    return {"status": "debug server running"}