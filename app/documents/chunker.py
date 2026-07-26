from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def create_chunks(
        self,
        documents: list[dict]
    ) -> list[dict]:

        chunks = []

        for document in documents:

            page_number = document["page"]

            content = document["content"]

            page_chunks = self.splitter.split_text(
                content
            )

            for chunk_index, chunk in enumerate(
                page_chunks
            ):

                chunk_id = (
                    f"page_{page_number}"
                    f"_chunk_{chunk_index}"
                )

                chunks.append({

                    "chunk_id": chunk_id,

                    "content": chunk,

                    "metadata": {

                        "page": page_number,

                        "chunk_index": chunk_index,

                        "source": "sbi_health_policy.pdf"

                    }

                })

        return chunks