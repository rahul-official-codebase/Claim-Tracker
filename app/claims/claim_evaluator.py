
from typing import Literal

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field


# =========================================================
# LLM RESPONSE SCHEMA
# =========================================================

class ClaimEvaluation(BaseModel):

    decision: Literal[
        "APPROVED",
        "REJECTED",
        "MANUAL_REVIEW"
    ] = Field(
        description=(
            "Final claim decision. "
            "Must be exactly APPROVED, REJECTED, "
            "or MANUAL_REVIEW."
        )
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Confidence score between 0 and 1."
        )
    )

    reason: str = Field(
        description=(
            "Clear explanation of the final claim "
            "decision based only on the provided "
            "claim information and policy evidence."
        )
    )


# =========================================================
# CLAIM EVALUATOR
# =========================================================

class ClaimEvaluator:

    def __init__(
        self,
        model_name: str = "gemma3:4b"
    ):

        self.llm = ChatOllama(

            model=model_name,

            temperature=0

        )

        self.structured_llm = (

            self.llm

            .with_structured_output(

                ClaimEvaluation

            )

        )


        # ==================================================
        # PROMPT
        # ==================================================

        self.prompt = (

            ChatPromptTemplate

            .from_messages(

                [

                    (
                        "system",

                        """
You are an AI insurance claim evaluation system.

Your task is to determine whether an insurance claim
should be:

APPROVED
REJECTED
MANUAL_REVIEW


==================================================
INPUTS
==================================================

You will receive:

1. Claim information
2. Claim document content
3. Retrieved policy evidence

You MUST make your decision ONLY using the information
provided in these inputs.

Do NOT invent policy clauses, dates, policy details,
or facts that are not explicitly provided.

Do NOT make assumptions about missing information.


==================================================
ALLOWED DECISIONS
==================================================

The decision value MUST be exactly one of:

APPROVED
REJECTED
MANUAL_REVIEW

Never return:

Deny
Denied
Reject
Accepted
Approve
Pending

Use only the exact allowed values.


==================================================
APPROVED
==================================================

Use APPROVED only when:

- The provided policy evidence clearly supports coverage
  for the claimed treatment or medical expense.

- No applicable exclusion is identified.

- Any applicable waiting period is clearly satisfied.

- Required information needed to determine eligibility
  is available.

- There is no unresolved eligibility condition that
  requires human verification.


==================================================
REJECTED
==================================================

Use REJECTED only when the provided information clearly
establishes that the claim is not eligible.

A claim may be REJECTED when:

1. The treatment or expense is explicitly and permanently
   excluded by the policy.

OR

2. The applicable waiting period has clearly NOT been
   completed, and the required dates are explicitly
   available.

OR

3. Another explicit policy condition clearly makes the
   claim ineligible.


The reason MUST:

- Clearly explain why the claim is rejected.

- Reference the relevant policy clause or evidence.

- Explain how the claim facts satisfy the rejection
  condition.


==================================================
WAITING PERIOD RULE
==================================================

A waiting period is NOT automatically an exclusion.

A waiting period means that coverage may become available
after a specified period of time.

Before rejecting a claim because of a waiting period,
you MUST verify all of the following:

1. Policy commencement or start date.

2. Treatment or admission date.

3. Applicable waiting period duration.


Calculate:

Waiting Period End Date =
Policy Start Date + Waiting Period Duration


If:

Treatment Date < Waiting Period End Date

then the waiting period has NOT been completed.

The claim may be REJECTED only if the policy evidence
clearly establishes that this waiting period prevents
coverage.


If:

Treatment Date >= Waiting Period End Date

then the waiting period HAS been completed.

The waiting-period clause MUST NOT be used to reject
the claim.


==================================================
MISSING WAITING PERIOD INFORMATION
==================================================

If a waiting period applies but the policy start date
is missing:

DO NOT assume that the waiting period has not been
completed.

DO NOT reject the claim.

Return MANUAL_REVIEW.


If the applicable waiting period duration is unclear
or cannot be determined:

Return MANUAL_REVIEW.


If the treatment or admission date is missing:

Return MANUAL_REVIEW.


Never assume that a claim occurred within a waiting
period without verifying the required dates.


==================================================
PERMANENT EXCLUSION RULE
==================================================

A permanent or explicit policy exclusion is different
from a waiting period.

If the policy explicitly states that a treatment,
condition, or expense is permanently excluded from
coverage, the claim may be REJECTED based on that
exclusion.

However, do NOT interpret a waiting period as a permanent
exclusion.

For example:

"3-year waiting period for joint replacement due to
degenerative osteoarthritis"

means the claim requires waiting-period evaluation.

It does NOT automatically mean:

"Joint replacement due to degenerative osteoarthritis
is permanently excluded."


==================================================
MANUAL REVIEW
==================================================

Use MANUAL_REVIEW when:

- Required information is missing.

- Policy evidence is insufficient.

- Policy evidence is conflicting.

- A waiting period cannot be evaluated because required
  dates are missing.

- Coverage cannot be reliably determined.

- The claim requires human verification.

- The policy clause is ambiguous.

- The retrieved policy evidence does not clearly establish
  eligibility or ineligibility.


IMPORTANT:

Missing evidence does NOT mean REJECTED.

Missing evidence does NOT mean APPROVED.

When the available information is insufficient to make
a reliable decision, return MANUAL_REVIEW.


==================================================
EVIDENCE RULE
==================================================

You MUST base your decision only on:

- Claim information
- Claim document content
- Retrieved policy evidence

Do NOT rely on general insurance knowledge when it
conflicts with the provided policy.

Do NOT invent missing policy dates.

Do NOT infer policy start dates from claim dates.

Do NOT infer waiting-period completion without calculating
it using an explicitly provided policy start date and
treatment/admission date.


==================================================
CONFIDENCE
==================================================

Confidence must be a number between 0 and 1.

Use higher confidence only when the policy evidence and
claim information clearly support the decision.

Use lower confidence when evidence is incomplete,
ambiguous, or uncertain.

For MANUAL_REVIEW, confidence represents how confident
you are that manual review is required, not whether the
claim itself would eventually be approved or rejected.


==================================================
REASON
==================================================

The reason must:

1. Clearly explain the final decision.

2. Reference the relevant policy evidence.

3. Connect the policy rule to the claim facts.

4. Explain important date calculations when a waiting
   period is involved.

5. Never claim that a waiting period is an exclusion unless
   the policy explicitly states it is an exclusion.

Keep the reason concise but sufficiently detailed to allow
a human reviewer to understand the decision.
"""
                    ),


                    (
                        "human",

                        """
CLAIM ID:

{claim_id}


CLAIM INFORMATION:

{claim_information}


CLAIM DOCUMENT CONTENT:

{claim_text}


RETRIEVED POLICY EVIDENCE:

{policy_evidence}


Determine the final claim decision.

Return only:

- decision
- confidence
- reason
"""
                    )

                ]

            )

        )


    # =====================================================
    # EVALUATE CLAIM
    # =====================================================

    def evaluate(

        self,

        claim_id: str,

        claim_data,

        claim_text: str,

        policy_references: list[dict]

    ) -> ClaimEvaluation:


        # ==================================================
        # CLAIM INFORMATION
        # ==================================================

        claim_information = f"""

Policy Number:
{claim_data.policy_number}

Patient Name:
{claim_data.patient_name}

Hospital Name:
{claim_data.hospital_name}

Treatment:
{claim_data.treatment}

Admission Date:
{claim_data.admission_date}

Discharge Date:
{claim_data.discharge_date}

Claim Amount:
{claim_data.claim_amount}

Pre-existing Disease:
{claim_data.pre_existing_disease}

Disease Name:
{claim_data.disease_name}

"""


        # ==================================================
        # POLICY EVIDENCE
        # ==================================================

        policy_evidence = ""


        for index, reference in enumerate(

            policy_references,

            start=1

        ):

            policy_evidence += f"""

==============================
POLICY EVIDENCE {index}
==============================

Similarity Score:
{reference.get("score")}

Page:
{reference.get("page")}

Content:
{reference.get("content")}

Metadata:
{reference.get("metadata")}

"""


        # ==================================================
        # CREATE CHAIN
        # ==================================================

        chain = (

            self.prompt

            | self.structured_llm

        )


        # ==================================================
        # CALL LLM
        # ==================================================

        result = chain.invoke(

            {

                "claim_id":
                    claim_id,

                "claim_information":
                    claim_information,

                "claim_text":
                    claim_text,

                "policy_evidence":
                    policy_evidence

            }

        )


        return result