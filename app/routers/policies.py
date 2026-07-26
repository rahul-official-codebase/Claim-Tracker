from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException
)

from app.services.policy_service import (
    PolicyService
)


router = APIRouter(
    prefix="/policies",
    tags=["Policies"]
)

policy_service = PolicyService()


@router.post("/upload")
async def upload_policy(
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    result = await policy_service.ingest_policy(file)

    return result