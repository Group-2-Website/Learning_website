from __future__ import annotations

import random

from sqlalchemy import func

from Database.Learning import Biology as DBBiology
from Database.Learning import Geography as DBGeography
from Database.Learning import Session
from models.subject import Subject
from models.topic import Topic


def _placeholder_paint_pages(topic_name: str) -> str:
    pages = []
    for idx in range(1, 4):
        pages.append(
            f'<div class="paint-page" data-page="{idx}" '
            'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
            '<div style="font-size:20px;font-weight:800;color:#60435F;text-align:center;">'
            f'{topic_name} Painting {idx}'
            '</div>'
            '<div data-target-num="" data-target-den="" '
            'style="width:220px;height:220px;border:4px dashed #60435F;border-radius:24px;'
            'display:flex;align-items:center;justify-content:center;background:#ffffff;color:#60435F;'
            'font-weight:700;text-align:center;padding:16px;">'
            'Painting content will be added later.'
            '</div>'
            '<div class="paint-hint" style="display:none;">'
            '<div style="font-weight:700;color:#60435F;text-align:center;">'
            'Painting is not added yet.'
            '</div>'
            '</div>'
            '</div>'
        )

    return (
        '<div class="science-paint-pages" '
        'style="display:flex;gap:24px;justify-content:center;flex-wrap:wrap;">'
        + "".join(pages)
        + "</div>"
    )


class ScienceTopic(Topic):
    has_learning = False
    has_painting = True

    def generate_question(
        self, filters: dict[str, str] | None = None
    ) -> tuple[str, str] | tuple[str, str, list[str]]:
        return "Quiz content will be added later.", "coming soon"

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        if not user.strip():
            return False, "Please enter an answer."
        return False, "Quiz content is not added yet."

    def page_background_image(self) -> str:
        return "/images/science.png"

    def paint_visual_html(self) -> str:
        return _placeholder_paint_pages(self.name)

    def paint_page_subtitle(self) -> str:
        return f"Painting for {self.name} will be added later."


class DatabaseScienceTopic(ScienceTopic):
    category_filter_name = "category"
    source_model = None
    source_options: list[tuple[str, str]] = []

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        return {self.category_filter_name: self.source_options}

    def default_quiz_filters(self) -> dict[str, str]:
        if not self.source_options:
            return {}
        return {self.category_filter_name: self.source_options[0][0]}

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective_filters = self.sanitize_quiz_filters(filters or {})
        selected_source = effective_filters.get(self.category_filter_name)
        if self.source_model is None or not selected_source:
            return "Quiz content will be added later.", "coming soon"

        session = Session()
        try:
            rows = (
                session.query(self.source_model)
                .filter(func.lower(self.source_model.source_csv) == selected_source.lower())
                .all()
            )
        finally:
            session.close()

        if not rows:
            return "Quiz content will be added later.", "coming soon"

        selected_row = random.choice(rows)
        options = [
            selected_row.option_a,
            selected_row.option_b,
            selected_row.option_c,
        ]
        random.shuffle(options)
        return selected_row.question, selected_row.correct_answer, options

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        if not user.strip():
            return False, "Please choose an answer."
        return user.strip().lower() == correct.strip().lower(), ""


class Geography(DatabaseScienceTopic):
    name = "Geography"
    source_model = DBGeography
    source_options = [
        ("countries", "Countries"),
        ("continants", "Continents"),
        ("water in the earth", "Water In The Earth"),
    ]


class Biology(DatabaseScienceTopic):
    name = "Biology"
    source_model = DBBiology
    source_options = [
        ("human_body", "Human Body"),
        ("plant", "Plant"),
        ("animals", "Animals"),
    ]


class Science(Subject):
    name = "Science"
    url_slug = "science"
    icon = "/images/Biology_Geography.png"
    topics: list[Topic] = [Geography(), Biology()]

    def page_background_image(self) -> str:
        return "/images/science.png"
