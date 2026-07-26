from datetime import date
from decimal import Decimal

from fastapi import APIRouter, File, Form, UploadFile

from app.claims.schemas import ClaimCreate
from app.claims.claim_service import ClaimService


router = APIRouter(
    prefix="/claims",
    tags=["Claims"]
)

claim_service = ClaimService()


@router.post("/")
async def create_claim(
    policy_number: str = Form(...),
    patient_name: str = Form(...),
    hospital_name: str = Form(...),
    treatment: str = Form(...),
    admission_date: date = Form(...),
    discharge_date: date = Form(...),
    claim_amount: Decimal = Form(...),
    pre_existing_disease: bool = Form(False),
    disease_name: str | None = Form(None),

    hospital_bill: UploadFile = File(...),
    medical_report: UploadFile = File(...),
    discharge_summary: UploadFile = File(...)
):

    claim_data = ClaimCreate(
        policy_number=policy_number,
        patient_name=patient_name,
        hospital_name=hospital_name,
        treatment=treatment,
        admission_date=admission_date,
        discharge_date=discharge_date,
        claim_amount=claim_amount,
        pre_existing_disease=pre_existing_disease,
        disease_name=disease_name
    )

    documents = [
        hospital_bill,
        medical_report,
        discharge_summary
    ]

    result = await claim_service.create_claim(
        claim_data=claim_data,
        documents=documents
    )
    
    return result