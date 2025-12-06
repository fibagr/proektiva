from app.domain.models import FullSurveyPayload


def yandex_build_prompt(survey_data: FullSurveyPayload) -> str:
    """Подготовка промпта на основе данных тестирования"""

    prompt_template = """Ты - опытный психолог и специалист по ментальному здоровью. 
На основе предоставленных данных тестирования составь развернутый анализ и персонализированные рекомендации.

ДАННЫЕ ТЕСТИРОВАНИЯ:

{data_summary}

ПРОАНАЛИЗИРУЙ и ПРЕДОСТАВЬ в структурированном виде:
1. ОБЩАЯ ОЦЕНКА СОСТОЯНИЯ
   - Основные сильные стороны
   - Ключевые области для улучшения

2. ПОДРОБНЫЙ АНАЛИЗ ПО КАТЕГОРИЯМ
   - Концентрация внимания: анализ показателей и рекомендации
   - Тревожность: оценка уровня и стратегии регуляции
   - Стресс: анализ уровня стресса и методы управления
   - Сон: качество сна и рекомендации по улучшению
   - Сенсорная обработка: особенности восприятия и адаптации

3. ПЕРСОНАЛИЗИРОВАННЫЕ РЕКОМЕНДАЦИИ
   - Ежедневные практики
   - Долгосрочные стратегии
   - Экстренные методы при ухудшении состояния

4. ПЛАН УЛУЧШЕНИЯ
   - Недельный план с конкретными шагами
   - Мониторинг прогресса

Используй профессиональный, но доступный язык. Учитывай все предоставленные данные.
Предоставь практические, выполнимые рекомендации."""

    # Собираем сводку данных
    data_summary = []

    if survey_data.concentration:
        data_summary.append(f"КОНЦЕНТРАЦИЯ ВНИМАНИЯ:")
        data_summary.append(f"  - Общий балл: {survey_data.concentration.total}")
        data_summary.append(f"  - Средний показатель: {survey_data.concentration.average}")
        if survey_data.concentration.conclusion:
            data_summary.append(f"  - Заключение: {survey_data.concentration.conclusion}")

    if survey_data.anxiety:
        data_summary.append(f"\nТРЕВОЖНОСТЬ:")
        data_summary.append(f"  - Уровень: {survey_data.anxiety.level}")
        data_summary.append(f"  - Общий балл: {survey_data.anxiety.total}")
        data_summary.append(f"  - Средний показатель: {survey_data.anxiety.average}")

    if survey_data.stress:
        data_summary.append(f"\nСТРЕСС:")
        data_summary.append(f"  - Уровень: {survey_data.stress.level}")
        data_summary.append(f"  - Общий балл: {survey_data.stress.total}")
        data_summary.append(f"  - Средний показатель: {survey_data.stress.average}")

    if survey_data.sleep:
        data_summary.append(f"\nСОН:")
        data_summary.append(f"  - Уровень качества: {survey_data.sleep.level}")
        data_summary.append(f"  - Общий балл: {survey_data.sleep.total}")
        data_summary.append(f"  - Средний показатель: {survey_data.sleep.average}")

    if survey_data.sensory:
        data_summary.append(f"\nСЕНСОРНАЯ ОБРАБОТКА:")
        sensory = survey_data.sensory
        if sensory.tactileLevel:
            data_summary.append(f"  - Тактильная чувствительность: {sensory.tactileLevel}")
        if sensory.proprioLevel:
            data_summary.append(f"  - Проприоцепция: {sensory.proprioLevel}")
        if sensory.vestibularLevel:
            data_summary.append(f"  - Вестибулярная система: {sensory.vestibularLevel}")
        if sensory.auditoryLevel:
            data_summary.append(f"  - Слуховая обработка: {sensory.auditoryLevel}")
        if sensory.visualLevel:
            data_summary.append(f"  - Визуальная обработка: {sensory.visualLevel}")
        if sensory.interoLevel:
            data_summary.append(f"  - Интероцепция: {sensory.interoLevel}")

    data_summary_str = "\n".join(data_summary)

    return prompt_template.format(data_summary=data_summary_str)
