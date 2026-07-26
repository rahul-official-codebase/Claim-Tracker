from typing import Any
from documents.pdf_processor import PDFProcessor
from documents.chunker import DocumentChunker
from embeddings.embedding_service import EmbeddingService
from vectorstore.qdrant_service import QdrantService


class RAGPipeline:

    def __init__(self):

        # 1. PDF Processing
        self.pdf_processor = PDFProcessor()

        # 2. Chunking
        self.chunker = DocumentChunker(
            chunk_size=1000,
            chunk_overlap=200
        )

        # 3. Embeddings
        self.embedding_service = (
            EmbeddingService()
        )

        # 4. Vector Database
        self.qdrant = QdrantService()


    def ingest_document(
        self,
        pdf_path: str
    ):
        """
        Process PDF and store its chunks
        and embeddings in Qdrant.
        """

        # --------------------------------
        # Step 1: Extract PDF
        # --------------------------------

        documents = (
            self.pdf_processor
            .process(pdf_path)
        )

        print(
            f"Extracted {len(documents)} pages"
        )


        # --------------------------------
        # Step 2: Create chunks
        # --------------------------------

        chunks = (
            self.chunker
            .create_chunks(documents)
        )

        print(
            f"Created {len(chunks)} chunks"
        )


        # --------------------------------
        # Step 3: Generate embeddings
        # --------------------------------

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service
            .generate_embeddings(texts)
        )


        # --------------------------------
        # Step 4: Attach embeddings
        # --------------------------------

        for chunk, embedding in zip[tuple[dict, list[float]]](
            chunks,
            embeddings
        ):

            chunk["embedding"] = embedding


        # --------------------------------
        # Step 5: Create Qdrant collection
        # --------------------------------

        self.qdrant.create_collection(
            vector_size=len(embeddings[0])
        )


        # --------------------------------
        # Step 6: Store in Qdrant
        # --------------------------------

        self.qdrant.upload_chunks(
            chunks
        )

        print(
            "Document successfully indexed"
        )


        return {
            "pages": len(documents),
            "chunks": len(chunks)
        }


    def query(
        self,
        question: str,
        limit: int = 5
    ):
        """
        Search relevant policy chunks
        for a user question.
        """

        # --------------------------------
        # Step 1: Embed user question
        # --------------------------------

        query_embedding = (
            self.embedding_service
            .generate_embedding(question)
        )


        # --------------------------------
        # Step 2: Search Qdrant
        # --------------------------------

        results = self.qdrant.search(
            query_vector=query_embedding,
            limit=limit
        )


        # --------------------------------
        # Step 3: Format results
        # --------------------------------

        relevant_chunks = []

        for result in results:

            relevant_chunks.append({

                "score": result.score,

                "content": (
                    result.payload["content"]
                ),

                "metadata": (
                    result.payload["metadata"]
                )

            })


        return relevant_chunks