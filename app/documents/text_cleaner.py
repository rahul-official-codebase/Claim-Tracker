import re


class TextCleaner:

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted PDF text.
        """

        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove excessive spaces/tabs
        text = re.sub(r"[ \t]+", " ", text)

        # Remove spaces before/after newlines
        text = re.sub(r" *\n *", "\n", text)

        # Replace 3+ consecutive newlines with 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def clean_table(table: list[list]) -> list[list]:
        """
        Clean extracted table cells.
        """

        cleaned_table = []

        for row in table:

            if not row:
                continue

            cleaned_row = []

            for cell in row:

                if cell is None:
                    cleaned_row.append("")
                    continue

                # Convert cell to string
                cell = str(cell)

                # Normalize whitespace
                cell = re.sub(r"\s+", " ", cell)

                cleaned_row.append(cell.strip())

            cleaned_table.append(cleaned_row)

        return cleaned_table

    @staticmethod
    def table_to_text(
        table: list[list],
        table_index: int
    ) -> str:
        """
        Convert a cleaned table into readable text.
        """

        if not table:
            return ""

        lines = [
            f"Table {table_index}:"
        ]

        for row in table:

            row_text = " | ".join(row)

            if row_text.strip():
                lines.append(row_text)

        return "\n".join(lines)