from pathlib import Path
from uuid import uuid4

from fastapi import (
    UploadFile,
    HTTPException
)

from app.claims.schemas import ClaimCreate

from app.documents.pdf_processor import (
    PDFProcessor
)

from app.vectorstore.qdrant_service import (
    QdrantService
)

from app.embeddings.embedding_service import (
    EmbeddingService
)

from app.claims.claim_evaluator import (
    ClaimEvaluator
)


class ClaimService:

    def __init__(self):

        # ==================================================
        # CLAIM UPLOAD DIRECTORY
        # ==================================================

        self.upload_dir = Path(
            "uploads/claims"
        )

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )


        # ==================================================
        # PDF PROCESSOR
        # ==================================================

        self.pdf_processor = (
            PDFProcessor()
        )


        # ==================================================
        # QDRANT VECTOR STORE
        # ==================================================

        self.vector_store = (
            QdrantService()
        )


        # ==================================================
        # EMBEDDING SERVICE
        # ==================================================

        self.embedding_service = (
            EmbeddingService()
        )


        # ==================================================
        # CLAIM EVALUATOR
        # ==================================================

        self.claim_evaluator = (
            ClaimEvaluator(
                model_name="gemma3:4b"
            )
        )


    # ======================================================
    # CREATE CLAIM
    # ======================================================

    async def create_claim(

        self,

        claim_data: ClaimCreate,

        documents: list[UploadFile]

    ):


        # ==================================================
        # 1. GENERATE CLAIM ID
        # ==================================================

        claim_id = (

            f"CLM-"

            f"{uuid4().hex[:8].upper()}"

        )


        # ==================================================
        # 2. CREATE CLAIM DIRECTORY
        # ==================================================

        claim_directory = (

            self.upload_dir

            / claim_id

        )


        claim_directory.mkdir(

            parents=True,

            exist_ok=True

        )


        # ==================================================
        # 3. VALIDATE DOCUMENTS
        # ==================================================

        if not documents:

            raise HTTPException(

                status_code=400,

                detail=(

                    "At least one claim "

                    "document is required."

                )

            )


        allowed_extensions = {

            ".pdf"

        }


        saved_documents = []


        # ==================================================
        # 4. SAVE DOCUMENTS
        # ==================================================

        for document in documents:


            # ----------------------------------------------
            # Validate filename
            # ----------------------------------------------

            if not document.filename:

                continue


            # ----------------------------------------------
            # Get extension
            # ----------------------------------------------

            file_extension = (

                Path(

                    document.filename

                )

                .suffix

                .lower()

            )


            # ----------------------------------------------
            # Validate extension
            # ----------------------------------------------

            if (

                file_extension

                not in allowed_extensions

            ):

                raise HTTPException(

                    status_code=400,

                    detail=(

                        f"Unsupported file type: "

                        f"{document.filename}. "

                        "Only PDF files are allowed."

                    )

                )


            # ----------------------------------------------
            # Generate safe filename
            # ----------------------------------------------

            safe_filename = (

                f"{uuid4().hex}_"

                f"{Path(document.filename).name}"

            )


            # ----------------------------------------------
            # File path
            # ----------------------------------------------

            file_path = (

                claim_directory

                / safe_filename

            )


            # ----------------------------------------------
            # Read file
            # ----------------------------------------------

            content = (

                await document.read()

            )


            # ----------------------------------------------
            # Save file
            # ----------------------------------------------

            try:

                with open(

                    file_path,

                    "wb"

                ) as file:

                    file.write(

                        content

                    )


            except Exception as e:

                raise HTTPException(

                    status_code=500,

                    detail=(

                        "Failed to save "

                        f"document {document.filename}: "

                        f"{str(e)}"

                    )

                )


            # ----------------------------------------------
            # Store document information
            # ----------------------------------------------

            saved_documents.append(

                {

                    "original_filename":

                        document.filename,

                    "stored_filename":

                        safe_filename,

                    "file_path":

                        str(file_path)

                }

            )


        # ==================================================
        # 5. VALIDATE SAVED DOCUMENTS
        # ==================================================

        if not saved_documents:

            raise HTTPException(

                status_code=400,

                detail=(

                    "No valid PDF documents "

                    "were uploaded."

                )

            )


        # ==================================================
        # 6. EXTRACT TEXT
        # ==================================================

        extracted_documents = []


        for document in saved_documents:


            file_path = (

                document["file_path"]

            )


            try:

                pages = (

                    self.pdf_processor

                    .process(

                        file_path

                    )

                )


                extracted_documents.append(

                    {

                        "filename":

                            document[

                                "original_filename"

                            ],

                        "pages":

                            pages

                    }

                )


            except Exception as e:

                raise HTTPException(

                    status_code=500,

                    detail=(

                        "Failed to process "

                        f"{document['original_filename']}: "

                        f"{str(e)}"

                    )

                )


        # ==================================================
        # 7. COMBINE CLAIM TEXT
        # ==================================================

        claim_text = ""


        for document in extracted_documents:


            claim_text += (

                "\n\n"

                "DOCUMENT: "

                f"{document['filename']}"

                "\n"

            )


            for page in document["pages"]:


                claim_text += (

                    "\nPAGE: "

                    f"{page['page']}"

                    "\n"

                )


                claim_text += (

                    page.get(

                        "content",

                        ""

                    )

                )


        # ==================================================
        # 8. BUILD POLICY SEARCH QUERY
        # ==================================================

        policy_query = (

            self._build_policy_query(

                claim_data=claim_data,

                claim_text=claim_text

            )

        )


        # ==================================================
        # 9. GENERATE QUERY EMBEDDING
        # ==================================================

        try:

            query_vector = (

                self.embedding_service

                .generate_embedding(

                    policy_query

                )

            )


        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=(

                    "Failed to generate "

                    "policy query embedding: "

                    f"{str(e)}"

                )

            )


        # ==================================================
        # 10. SEARCH QDRANT
        # ==================================================

        try:

            policy_results = (

                self.vector_store

                .search(

                    query_vector=query_vector,

                    limit=5

                )

            )


        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=(

                    "Failed to search "

                    "policy vector store: "

                    f"{str(e)}"

                )

            )


        # ==================================================
        # 11. PREPARE POLICY REFERENCES
        # ==================================================

        policy_references = []


        for result in policy_results:


            # ----------------------------------------------
            # Get payload
            # ----------------------------------------------

            if hasattr(

                result,

                "payload"

            ):

                payload = (

                    result.payload

                    or {}

                )

            else:

                payload = (

                    result.get(

                        "payload",

                        {}

                    )

                )


            # ----------------------------------------------
            # Get score
            # ----------------------------------------------

            if hasattr(

                result,

                "score"

            ):

                score = (

                    result.score

                )

            else:

                score = (

                    result.get(

                        "score"

                    )

                )


            # ----------------------------------------------
            # Get metadata
            # ----------------------------------------------

            metadata = (

                payload.get(

                    "metadata",

                    {}

                )

            )


            # ----------------------------------------------
            # Store reference
            # ----------------------------------------------

            policy_references.append(

                {

                    "score":

                        score,

                    "page":

                        payload.get(

                            "page",

                            metadata.get(

                                "page"

                            )

                        ),

                    "content":

                        payload.get(

                            "content",

                            ""

                        ),

                    "metadata":

                        metadata

                }

            )


        # ==================================================
        # 12. NO POLICY EVIDENCE
        # ==================================================

        if not policy_references:

            return {

                "claim_id":

                    claim_id,

                "decision":

                    "MANUAL_REVIEW",

                "confidence":

                    0.0,

                "reason":

                    (

                        "No relevant policy evidence "

                        "was found for this claim. "

                        "Manual review is required."

                    )

            }


        # ==================================================
        # 13. LLM CLAIM EVALUATION
        # ==================================================

        try:
            # print("========== CLAIM DATA ==========")
            # print(claim_data)

            # print("========== POLICY REFERENCES ==========")
            # for reference in policy_references:
            #     print(reference)

            # print("========== CLAIM TEXT ==========")
            # print(claim_text)


            evaluation = (

                self.claim_evaluator

                .evaluate(

                    claim_id=claim_id,

                    claim_data=claim_data,

                    claim_text=claim_text,

                    policy_references=(

                        policy_references

                    )

                )

            )


        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=(

                    "Failed to evaluate "

                    "claim using LLM: "

                    f"{str(e)}"

                )

            )


        # ==================================================
        # 14. FINAL RESPONSE
        # ==================================================

        return {

            "claim_id":

                claim_id,

            "decision":

                evaluation.decision,

            "confidence":

                evaluation.confidence,

            "reason":

                evaluation.reason

        }


    # ======================================================
    # BUILD POLICY SEARCH QUERY
    # ======================================================

    def _build_policy_query(

        self,

        claim_data: ClaimCreate,

        claim_text: str

    ) -> str:


        query = f"""

Insurance claim eligibility evaluation.

Policy Number:
{claim_data.policy_number}

Patient:
{claim_data.patient_name}

Hospital:
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

Disease:
{claim_data.disease_name}

Claim Document Information:
{claim_text}

Find policy clauses related to:

- Coverage
- Treatment eligibility
- Waiting periods
- Pre-existing diseases
- Exclusions
- Hospitalization requirements
- Claim limits
- Sub-limits
- Required documents
- Claim submission requirements
"""

        return query.strip()