import fitz
import pdfplumber

from app.documents.text_cleaner import TextCleaner


class PDFProcessor:

    def __init__(self):

        self.cleaner = TextCleaner()

    def process(self, pdf_path: str) -> list[dict]:

        documents = []

        # Open PDF using PyMuPDF
        pymupdf_doc = fitz.open(pdf_path)

        # Open PDF using pdfplumber
        pdfplumber_doc = pdfplumber.open(pdf_path)

        try:

            for page_number in range(len(pymupdf_doc)):

                # =====================================
                # 1. Extract normal text
                # =====================================

                pymupdf_page = pymupdf_doc[page_number]

                raw_text = pymupdf_page.get_text("text")

                # Clean extracted text
                text = self.cleaner.clean_text(raw_text)


                # =====================================
                # 2. Extract tables
                # =====================================

                pdfplumber_page = pdfplumber_doc.pages[page_number]

                raw_tables = pdfplumber_page.extract_tables()


                # =====================================
                # 3. Clean tables
                # =====================================

                cleaned_tables = []

                for table in raw_tables:

                    cleaned_table = self.cleaner.clean_table(
                        table
                    )

                    if cleaned_table:
                        cleaned_tables.append(
                            cleaned_table
                        )


                # =====================================
                # 4. Convert tables to text
                # =====================================

                table_text_parts = []

                for table_index, table in enumerate(
                    cleaned_tables,
                    start=1
                ):

                    table_text = self.cleaner.table_to_text(
                        table,
                        table_index
                    )

                    if table_text:
                        table_text_parts.append(
                            table_text
                        )


                table_text = "\n\n".join(
                    table_text_parts
                )


                # =====================================
                # 5. Combine text + tables
                # =====================================

                combined_content = self.build_content(
                    page_number=page_number + 1,
                    text=text,
                    table_text=table_text
                )


                # =====================================
                # 6. Store document
                # =====================================

                documents.append({

                    "page": page_number + 1,

                    "text": text,

                    "tables": cleaned_tables,

                    "content": combined_content

                })

        finally:

            # Always close files
            pymupdf_doc.close()

            pdfplumber_doc.close()


        return documents


    @staticmethod
    def build_content(
        page_number: int,
        text: str,
        table_text: str
    ) -> str:
        """
        Build final content for RAG processing.
        """

        sections = [
            f"Page: {page_number}"
        ]

        if text:

            sections.append(
                f"TEXT:\n{text}"
            )

        if table_text:

            sections.append(
                f"TABLES:\n{table_text}"
            )

        return "\n\n".join(sections)