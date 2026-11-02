from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(file_content: bytes) -> str:
    """
    Extract text from a PDF stored in memory.
    """

    pdf_file = BytesIO(file_content)
    reader = PdfReader(pdf_file)

    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not supported.")

    extracted_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if page_text.strip():
            extracted_text.append(
                f"--- Page {page_number} ---\n{page_text}"
            )

    return "\n\n".join(extracted_text)
