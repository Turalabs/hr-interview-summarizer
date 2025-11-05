from markdown_pdf import MarkdownPdf, Section
from io import BytesIO

def generate_markdown_pdf_bytes(title: str, body_md: str) -> bytes:
    if not body_md:
        body_md = "_(No content provided)_"

    pdf = MarkdownPdf()

    pdf.add_section(
        Section(
            f"# {title or 'Document'}\n\n{body_md.strip()}",
        )
    )

    buffer = BytesIO()
    pdf.save(buffer)
    buffer.seek(0)

    return buffer.read()
