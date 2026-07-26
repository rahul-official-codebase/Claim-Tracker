from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)


class QdrantService:

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333
    ):

        self.client = QdrantClient(
            host=host,
            port=port
        )

        self.collection_name = (
            "insurance_policies"
        )


    # ==================================================
    # Create Collection
    # ==================================================

    def create_collection(
        self,
        vector_size: int
    ):

        collections = (
            self.client
            .get_collections()
            .collections
        )

        collection_exists = any(
            collection.name
            == self.collection_name
            for collection in collections
        )

        if not collection_exists:

            self.client.create_collection(

                collection_name=(
                    self.collection_name
                ),

                vectors_config=VectorParams(

                    size=vector_size,

                    distance=Distance.COSINE
                )
            )


    # ==================================================
    # Upload Embedded Chunks
    # ==================================================

    def upload_chunks(
        self,
        chunks: list[dict]
    ):

        points = []

        for index, chunk in enumerate(chunks):

            point = PointStruct(

                id=index,

                vector=chunk["embedding"],

                payload={

                    "chunk_id":
                        chunk["chunk_id"],

                    "content":
                        chunk["content"],

                    "metadata":
                        chunk["metadata"]
                }
            )

            points.append(point)


        self.client.upsert(

            collection_name=(
                self.collection_name
            ),

            points=points
        )


    # ==================================================
    # Search Similar Policy Chunks
    # ==================================================

    def search(
        self,
        query_vector: list[float],
        limit: int = 5
    ):

        results = self.client.query_points(

            collection_name=(
                self.collection_name
            ),

            query=query_vector,

            limit=limit,

            with_payload=True
        )

        return results.points