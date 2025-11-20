import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def render_text_to_pdf(text: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x = 50
    y = height - 50

    for line in text.split("\n"):
        if not line.strip():
            y -= 16
            continue

        c.drawString(x, y, line[:120])
        y -= 14

        if y < 50:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
