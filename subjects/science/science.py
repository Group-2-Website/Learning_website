from __future__ import annotations

import random

from Database.dao import ScienceQuizDAO
from models.subject import Subject
from models.topic import Topic, FilterOption, FilterDefinition
from models.quiz_card import QuizCard


def _build_science_paint_pages(
    targets: list[str],
    hints: list[str],
    titles: list[str],
) -> str:
    pages = []
    for idx, image_path in enumerate(targets, start=1):
        hint_html = ""
        if hints[idx - 1]:
            hint_html = (
                '<div class="paint-hint" style="display:none;">'
                f'<img src="{hints[idx - 1]}" alt="hint {idx}" style="max-width:400px;height:auto;" />'
                "</div>"
            )
        pages.append(
            f'<div class="paint-page" data-page="{idx}" '
            f'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
            '<div style="font-size:20px;font-weight:800;color:#60435F;text-align:center;">'
            f'Color the {titles[idx - 1]}!'
            "</div>"
            f'<div data-target-num="" data-target-den="">'
            f'<img src="{image_path}" alt="painting {idx}" style="max-width:220px;height:auto;" />'
            "</div>"
            f"{hint_html}"
            "</div>"
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
    quiz_mode: str = "multiple_choice"

    def page_background_image(self) -> str:
        return "/images/science.png"

    def paint_page_subtitle(self) -> str:
        return f"Color and explore {self.name}!"


class DatabaseScienceTopic(ScienceTopic):
    quiz_source: str = "database"
    category_filter_name = "category"
    db_subject: str = ""          # "biology" or "geography"
    source_options: list[FilterOption] = []

    paint_targets: list[str] = []
    paint_hints: list[str] = []
    paint_titles: list[str] = []

    def quiz_filter_definitions(self) -> list[FilterDefinition]:
        return [FilterDefinition(self.category_filter_name, self.source_options)]

    def _load_question_from_db(self, filters: dict[str, str] | None = None) -> QuizCard | None:
        effective_filters = self.sanitize_quiz_filters(filters or {})
        selected_source = effective_filters.get(self.category_filter_name)
        if not self.db_subject or not selected_source:
            return None

        rows = ScienceQuizDAO().list_questions(self.db_subject, selected_source)

        if not rows:
            return None

        row = random.choice(rows)
        options = [row.option_a, row.option_b, row.option_c]
        random.shuffle(options)
        return QuizCard(
            question=row.question,
            options=options,
            correct_answer=row.correct_answer,
            topic=self.name,
        )

    def paint_visual_html(self) -> str:
        return _build_science_paint_pages(
            targets=self.paint_targets,
            hints=self.paint_hints,
            titles=self.paint_titles,
        )


class Geography(DatabaseScienceTopic):
    name = "Geography"
    db_subject = "geography"
    source_options = [
        FilterOption("countries", "Countries"),
        FilterOption("continants", "Continents"),
        FilterOption("water in the earth", "Water In The Earth"),
    ]
    paint_targets = ["/images/swiss.png", "/images/continent.png", "/images/globe.png"]
    paint_hints  = ["/images/swiss_colored.png", "/images/continent_colored.png", "/images/globe_colored.png"]
    paint_titles = ["Map", "Continents", "Globe"]


class Biology(DatabaseScienceTopic):
    name = "Biology"
    db_subject = "biology"
    source_options = [
        FilterOption("human_body", "Human Body"),
        FilterOption("plant", "Plant"),
        FilterOption("animals", "Animals"),
    ]
    paint_targets = ["/images/human-body.png", "/images/happy_rabbit.png", "/images/flower.png"]
    paint_hints  = ["/images/human_body_colored.png", "/images/Animal-Colored.png", "/images/flower_colored.png"]
    paint_titles = ["Human Body", "This Happy Rabbit", " This Nice Flower"]


class Science(Subject):
    name = "Science"
    url_slug = "science"
    icon = "/images/icons/laboratory.svg"
    topics: list[Topic] = [Geography(), Biology()]

    def page_background_image(self) -> str:
        return "/images/science.png"