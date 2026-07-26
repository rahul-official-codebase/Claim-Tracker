from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ClaimCreate(BaseModel):
    policy_number: str = Field(
        ...,
        min_length=1
    )

    patient_name: str = Field(
        ...,
        min_length=1
    )

    hospital_name: str = Field(
        ...,
        min_length=1
    )

    treatment: str = Field(
        ...,
        min_length=1
    )

    admission_date: date

    discharge_date: date

    claim_amount: Decimal = Field(
        ...,
        gt=0
    )

    pre_existing_disease: bool = False

    disease_name: str | None = None