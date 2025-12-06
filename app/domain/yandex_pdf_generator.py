import io
import os

from app.domain.models import FullSurveyPayload

from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Регистрируем TTF-шрифт с поддержкой кириллицы
FONT_NAME = "DejaVuSans"
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "DejaVuSans.ttf")


def _register_font():
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))


def yandex_render_text_to_pdf(analysis_text: str, survey_data: FullSurveyPayload) -> bytes:
    """
    Рендерит текст (в т.ч. русский) в PDF, используя TTF-шрифт с поддержкой кириллицы.
    """
    _register_font()

    buffer = io.BytesIO()

    """Создание PDF-отчета с результатами анализа"""

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Стили
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50'),
        fontName=FONT_NAME
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor('#3498db'),
        fontName=FONT_NAME
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leading=14,
        fontName=FONT_NAME
    )

    story = []

    # Заголовок
    story.append(Paragraph("ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ И РЕКОМЕНДАЦИИ", title_style))
    story.append(Paragraph(f"Дата отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 20))

    # Сводка данных
    story.append(Paragraph("СВОДКА ДАННЫХ ТЕСТИРОВАНИЯ", heading_style))

    # Таблица с основными показателями
    data = [["Показатель", "Значение", "Уровень"]]

    if survey_data.concentration:
        data.append(["Концентрация", f"{survey_data.concentration.total} баллов", ""])

    if survey_data.anxiety:
        data.append(["Тревожность", f"{survey_data.anxiety.total}", survey_data.anxiety.level or ""])

    if survey_data.stress:
        data.append(["Стресс", f"{survey_data.stress.total}", survey_data.stress.level or ""])

    if survey_data.sleep:
        data.append(["Качество сна", f"{survey_data.sleep.total}", survey_data.sleep.level or ""])

    if survey_data.sensory:
        sensory = survey_data.sensory
        if sensory.tactileLevel:
            data.append(["Тактильная чувствительность", f"{sensory.tactileAvg:.1f}", sensory.tactileLevel])

    table = Table(data, colWidths=[2.5 * inch, 1.5 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    story.append(table)
    story.append(Spacer(1, 25))

    # Анализ от ИИ
    story.append(Paragraph("ДЕТАЛЬНЫЙ АНАЛИЗ И РЕКОМЕНДАЦИИ", heading_style))

    # Разбиваем текст анализа на параграфы
    sections = analysis_text.split('\n\n')
    for section in sections:
        if section.strip():
            # Определяем, является ли секция заголовком
            lines = section.strip().split('\n')
            if len(lines) > 0:
                first_line = lines[0].strip()
                if first_line and not first_line.startswith(' ') and ':' not in first_line:
                    story.append(Paragraph(first_line, heading_style))
                    for line in lines[1:]:
                        if line.strip():
                            story.append(Paragraph(f"• {line.strip()}", normal_style))
                else:
                    story.append(Paragraph(section.strip(), normal_style))
            story.append(Spacer(1, 6))

    # Практические рекомендации
    story.append(Spacer(1, 15))
    story.append(Paragraph("ПРАКТИЧЕСКИЕ ШАГИ", heading_style))
    story.append(Paragraph("""
    1. Регулярно отслеживайте свое состояние в дневнике
    2. Внедряйте рекомендации постепенно, начиная с самых простых
    3. Обращайтесь к специалистам при необходимости
    4. Будьте терпеливы к себе - изменения требуют времени
    """, normal_style))

    # Подпись
    story.append(Spacer(1, 30))
    story.append(Paragraph("С уважением,", normal_style))
    story.append(Paragraph("Система анализа ментального здоровья", normal_style))
    story.append(Paragraph(f"Сгенерировано с использованием YandexGPT",
                            ParagraphStyle('Footer', parent=normal_style, fontSize=9, textColor=colors.gray)))

    doc.build(story)
    
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
