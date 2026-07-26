from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.documents.pdf_processor import PDFProcessor
from app.documents.chunker import DocumentChunker
from app.embeddings.embedding_service import EmbeddingService
from app.vectorstore.qdrant_service import QdrantService


class PolicyService:

    UPLOAD_DIR = Path("uploads/policies")

    def __init__(self):

        # Create upload directory
        self.UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        # Initialize components
        self.pdf_processor = PDFProcessor()

        self.chunker = DocumentChunker(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.embedding_service = (
            EmbeddingService()
        )

        self.qdrant = QdrantService()


    async def ingest_policy(
        self,
        file: UploadFile
    ):

        # =====================================
        # 1. Generate Policy ID
        # =====================================

        policy_id = str(uuid4())


        # =====================================
        # 2. Save PDF
        # =====================================

        policy_directory = (
            self.UPLOAD_DIR / policy_id
        )

        policy_directory.mkdir(
            parents=True,
            exist_ok=True
        )


        file_path = (
            policy_directory
            / file.filename
        )


        content = await file.read()


        with open(
            file_path,
            "wb"
        ) as pdf_file:

            pdf_file.write(content)


        # =====================================
        # 3. Extract PDF
        # =====================================

        documents = (
            self.pdf_processor
            .process(
                str(file_path)
            )
        )


        # =====================================
        # 4. Create chunks
        # =====================================

        chunks = (
            self.chunker
            .create_chunks(
                documents
            )
        )


        # =====================================
        # 5. Generate embeddings
        # =====================================

        texts = [
            chunk["content"]
            for chunk in chunks
        ]


        embeddings = (
            self.embedding_service
            .generate_embeddings(
                texts
            )
        )


        # =====================================
        # 6. Add embedding + policy metadata
        # =====================================

        for chunk, embedding in zip(
            chunks,
            embeddings
        ):

            chunk["embedding"] = embedding

            chunk["metadata"][
                "policy_id"
            ] = policy_id

            chunk["metadata"][
                "policy_name"
            ] = file.filename


        # =====================================
        # 7. Create Qdrant collection
        # =====================================

        self.qdrant.create_collection(
            vector_size=len(
                embeddings[0]
            )
        )


        # =====================================
        # 8. Store in Qdrant
        # =====================================

        self.qdrant.upload_chunks(
            chunks
        )


        # =====================================
        # 9. Return result
        # =====================================

        return {

            "policy_id":
                policy_id,

            "policy_name":
                file.filename,

            "pages":
                len(documents),

            "chunks":
                len(chunks),

            "status":
                "INDEXED"

        }