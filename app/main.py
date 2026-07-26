from fastapi import FastAPI

from app.routers.claims import router as claims_router
from app.routers.policies import (
    router as policies_router
)


app = FastAPI(
    title="Insurance Claim Eligibility System"
)


app.include_router(
    claims_router
)

app.include_router(
    policies_router
)


@app.get("/")
async def root():

    return {
        "message":
            "Insurance Claim API is running"
    }



