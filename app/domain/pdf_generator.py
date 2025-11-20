import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


# Регистрируем TTF-шрифт с поддержкой кириллицы
FONT_NAME = "DejaVuSans"
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "DejaVuSans.ttf")


def _register_font():
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


def render_text_to_pdf(text: str) -> bytes:
    """
    Рендерит текст (в т.ч. русский) в PDF, используя TTF-шрифт с поддержкой кириллицы.
    """
    _register_font()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont(FONT_NAME, 11)

    x = 50
    y = height - 50

    # простейшая разбивка на строки и "переносы"
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            y -= 16
            if y < 50:
                c.showPage()
                c.setFont(FONT_NAME, 11)
                y = height - 50
            continue

        # делаем грубый перенос строк по ширине страницы
        max_width = width - 100  # поля слева/справа
        words = line.split()
        current = ""

        for w in words:
            candidate = (current + " " + w).strip()
            if pdfmetrics.stringWidth(candidate, FONT_NAME, 11) <= max_width:
                current = candidate
            else:
                # печатаем текущую строку
                c.drawString(x, y, current)
                y -= 14
                if y < 50:
                    c.showPage()
                    c.setFont(FONT_NAME, 11)
                    y = height - 50
                current = w

        if current:
            c.drawString(x, y, current)
            y -= 14
            if y < 50:
                c.showPage()
                c.setFont(FONT_NAME, 11)
                y = height - 50

        # небольшое дополнительное расстояние после абзаца
        y -= 4

    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
