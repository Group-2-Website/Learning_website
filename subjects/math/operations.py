from __future__ import annotations

import random

from .mathematics import MathTopic, OPERATION_GROUPS, load_steps_from_db, parse_binary_expression
from models.learning_card import LearningStep


def token_to_int(token: str) -> int | None:
    from fractions import Fraction
    cleaned = (token or "").replace("(", "").replace(")", "").strip()
    if not cleaned:
        return None
    try:
        frac = Fraction(cleaned)
    except (ValueError, ZeroDivisionError):
        return None
    if frac.denominator != 1:
        return None
    return int(frac.numerator)


class Operation(MathTopic):
    name = "Operations"
    has_painting = True

    def page_background_image(self) -> str:
        return "/images/operation.jpg"

    def quiz_filter_definitions(self) -> list:
        from models.topic import FilterOption, FilterDefinition
        result = super().quiz_filter_definitions()
        result.append(FilterDefinition("row", [FilterOption(str(i), f"Row {i}") for i in range(1, 13)], default="1"))
        return result

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective_filters = self.sanitize_quiz_filters(filters or {})

        digit_by_difficulty = {
            "mixed": (1, 1000),
            "easy": range(1, 12),
            "medium": range(12, 100),
            "hard": range(100, 1000),
        }

        op = random.choice(OPERATION_GROUPS[effective_filters["operation"]])
        digit = random.choice(digit_by_difficulty[effective_filters["difficulty"]])
        row = int(effective_filters.get("row", 1))

        if op == "×" and effective_filters["difficulty"] == "easy":
            a = row
            b = random.randint(1, 12)
            question = f"{a} × {b} = ?"
            num_result = a * b
        elif op in ("+", "-"):
            a = random.randint(1, digit)
            b = random.randint(1, digit)
            if op == "-":
                a, b = max(a, b), min(a, b)
            question = f"{a} {op} {b} = ?"
            num_result = a + b if op == "+" else a - b
        elif op == "×":
            a = random.randint(1, digit)
            b = random.randint(1, digit)
            question = f"{a} × {b} = ?"
            num_result = a * b
        else:
            num_result = random.randint(1, digit)
            b = random.randint(1, max(1, digit))
            a = b * num_result
            question = f"{a} ÷ {b} = ?"
        return question, str(num_result)

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        user = user.strip()

        if not user:
            return False, "Please enter an answer."
        if not user.lstrip("-").isdigit():
            return False, "Only integer numbers allowed!"

        return int(user) == int(correct), ""

    def learn_filter_definitions(self) -> list:
        from models.topic import FilterOption, FilterDefinition
        topic_options = [
            FilterOption("all", "Introduction (All Operations)"),
        ] + [FilterOption(f"row_{i}", f"Multiplication Row {i}") for i in range(1, 13)]
        return [
            FilterDefinition("topic", topic_options, default="all"),
        ]

    def apply_learn_filters(self, filters: dict[str, str]) -> None:
        topic_val = filters.get("topic", "all")
        if topic_val.startswith("row_"):
            try:
                self._learn_row = max(1, min(12, int(topic_val.split("_")[1])))
            except (ValueError, IndexError):
                self._learn_row = None
        else:
            self._learn_row = None

    def learn_page_subtitle(self) -> str:
        row = getattr(self, "_learn_row", None)
        if row is not None:
            return f"Let's learn about Row {row}"
        return "Explore and learn about Operations!"

    def learning_steps(self) -> list[LearningStep]:
        row = getattr(self, "_learn_row", None)
        if row is not None:
            # Generate multiplication table cards for the selected row
            steps = []
            for i in range(1, 13):
                result = row * i
                steps.append(LearningStep(
                    title="",
                    main_text=f"{row} × {i} = {result}",
                    secondary_text=self._render_multiplication_apples(
                        row, i
                    ) if row * i <= 144 else "",
                ))
            self._step_rows = steps
            self._step_images = ["" for _ in steps]
            return steps

        # Default: load introduction steps from DB
        steps = load_steps_from_db(subject_name="operations")
        self._step_rows = steps
        if steps:
            self._step_images = [step.image for step in steps]
            return steps
        self._step_images = []
        return [LearningStep()]

    @staticmethod
    def _clamp(value: int, minimum: int, maximum: int) -> int:
        return max(minimum, min(maximum, value))

    @staticmethod
    def _render_multiplication_apples(groups: int, apples_per_group: int) -> str:
        safe_groups = Operation._clamp(groups, 1, 12)
        safe_apples = Operation._clamp(apples_per_group, 0, 12)
        rows_html = "".join(
            f'<div style="display:flex;gap:6px;font-size:25px;">{"🍎" * safe_apples}</div>'
            for _ in range(safe_groups)
        )
        return (
            '<div style="display:flex;flex-direction:column;align-items:center;gap:6px;">'
            f"{rows_html}"
            "</div>"
        )

    @staticmethod
    def _render_division_apples(total: int, divisor: int, fallback_answer: int | None) -> str:
        safe_groups = Operation._clamp(divisor, 1, 10)
        apples_per_group = total // divisor if divisor > 0 else 0

        if divisor <= 0 or total % divisor != 0:
            if fallback_answer is None or fallback_answer < 0:
                return ""
            apples_per_group = fallback_answer

        safe_apples = Operation._clamp(apples_per_group, 0, 12)
        group_html = "".join(
            '<div style="text-align:center;font-size:25px;">'
            "●<br>"
            f'{"🍎" * safe_apples}'
            "</div>"
            for _ in range(safe_groups)
        )
        return (
            '<div style="display:flex;justify-content:center;gap:30px;flex-wrap:wrap;">'
            f"{group_html}"
            "</div>"
        )

    @staticmethod
    def _render_number_line(start: int, delta: int, explicit_result: int | None) -> str:
        end = start + delta if explicit_result is None else explicit_result

        min_n = min(start, end) - 1
        max_n = max(start, end) + 1
        values = list(range(min_n, max_n + 1))
        if len(values) < 3:
            values = [start - 1, start, start + 1]

        width = 420
        left_pad = 28
        right_pad = 28
        line_y = 62
        step = (width - left_pad - right_pad) / (len(values) - 1)

        positions = {value: left_pad + idx * step for idx, value in enumerate(values)}
        start_x = positions[start]
        end_x = positions[end]
        control_x = (start_x + end_x) / 2
        control_y = 12

        tick_lines = "".join(
            f'<line x1="{positions[value]:.2f}" y1="{line_y - 8}" x2="{positions[value]:.2f}" y2="{line_y + 8}" '
            'stroke="#60435F" stroke-width="2" />'
            for value in values
        )
        labels = "".join(
            f'<text x="{positions[value]:.2f}" y="{line_y + 24}" text-anchor="middle" '
            'font-size="13" font-weight="700" fill="#60435F" font-family="sans-serif">'
            f"{value}"
            "</text>"
            for value in values
        )

        operand_label = f"{delta:+d}"
        return (
            '<div style="display:flex;justify-content:center;margin:8px 0 2px 0;">'
            f'<svg width="{width}" height="108" viewBox="0 0 {width} 108" xmlns="http://www.w3.org/2000/svg">'
            "<defs>"
            '<marker id="numline-arrow" markerWidth="10" markerHeight="8" refX="8" refY="4" orient="auto" markerUnits="strokeWidth">'
            '<path d="M0,0 L10,4 L0,8 z" fill="#a83432" />'
            "</marker>"
            "</defs>"
            f'<line x1="{left_pad}" y1="{line_y}" x2="{width - right_pad}" y2="{line_y}" stroke="#60435F" stroke-width="3" />'
            f"{tick_lines}"
            f"{labels}"
            f'<path d="M {start_x:.2f} {line_y - 2} Q {control_x:.2f} {control_y} {end_x:.2f} {line_y - 2}" '
            'fill="none" stroke="#a83432" stroke-width="3" marker-end="url(#numline-arrow)" />'
            f'<text x="{control_x:.2f}" y="{control_y - 2}" text-anchor="middle" font-size="14" font-weight="800" fill="#a83432" font-family="sans-serif">'
            f"{operand_label}"
            "</text>"
            f'<circle cx="{start_x:.2f}" cy="{line_y}" r="5" fill="#60435F" />'
            f'<circle cx="{end_x:.2f}" cy="{line_y}" r="5" fill="#2f855a" />'
            "</svg>"
            "</div>"
        )

    def step_visual_html(self, step_index: int) -> str:
        base = super().step_visual_html(step_index)
        rows = getattr(self, "_step_rows", None)
        if rows is None:
            rows = load_steps_from_db(subject_name="operations")
            self._step_rows = rows

        if step_index < 0 or step_index >= len(rows):
            return base

        step = rows[step_index]
        expression = step.secondary_text.strip()
        parsed = parse_binary_expression(expression)
        if not parsed:
            return base

        left_t, op, right_t = parsed
        left_value = token_to_int(left_t)
        right_value = token_to_int(right_t)
        answer_value = token_to_int(step.hint_text.strip())

        if left_value is None or right_value is None:
            return base

        if op in ("×", "÷"):
            if op == "×":
                return base + self._render_multiplication_apples(left_value, right_value)

            division_html = self._render_division_apples(left_value, right_value, answer_value)
            return base + division_html if division_html else base

        if op not in ("+", "−"):
            return base

        delta = right_value if op == "+" else -right_value
        return base + self._render_number_line(left_value, delta, answer_value)

    def paint_visual_html(self) -> str:
        targets = ["/images/not_colored_1.png", "/images/Operation_painting2.png", "/images/not_colored_3.png"]
        hints = ["/images/colored_1.png", "/images/math-sol.png", "/images/colored_3.png"]
        titles = [
            "Solve each problem, then color the space with the matching color",
            "Have some fun with Math\n\n\n",
            "Solve each problem, then color the space with the matching color",
        ]
        
        # Color key content for each page
        color_key_content = [
            "6→Blue<br>4→Light Blue<br>10→Red<br>15→Pink<br>20→Orange<br>24→Light Orange<br>2→Yellow<br>5→White",
            "",
            "Dark Purple=40<br>Blue=96<br>Light Blue=88<br>Green=32<br>Light Green=72<br>"
            "Turquoise=64<br>Red=8<br>Pink=48<br>Light Pink=56<br>Orange=80,16<br>"
            "Peach=12,100<br>Yellow=24",
        ]
        
        def build_color_key(content: str) -> str:
            """Generate color key bubble HTML."""
            if not content:
                return ""
            return (
                '<div class="paint-color-key" style="background:linear-gradient(135deg,#ffc9b8,#ffb4a2);'
                'border:2.5px solid #ffb4a2;border-radius:20px;padding:18px 22px;'
                'box-shadow:inset 0 -3px 10px rgba(255,255,255,0.6),inset 2px 2px 12px rgba(255,255,255,0.7),'
                '0 6px 14px rgba(0,0,0,0.2),-2px -2px 0 #ffffff,2px 2px 0 #f28482,4px 4px 0 #e76f51;'
                'max-width:180px;">'
                '<div style="font-weight:800;font-size:15px;color:#60435F;margin-bottom:10px;text-align:center;">'
                'Color Key'
                '</div>'
                f'<div style="font-weight:700;font-size:12px;color:#60435F;line-height:1.5;text-align:left;">'
                f'{content}'
                '</div>'
                '</div>'
            )
        
        pages = []
        for idx, image_path in enumerate(targets, start=1):
            hint_html = ""
            if hints[idx - 1]:
                hint_html = (
                    '<div class="paint-hint" style="display:none;">'
                    f'<img src="{hints[idx - 1]}" alt="hint {idx}" style="max-width:400px;height:auto;" />'
                    "</div>"
                )
            
            color_key_html = ""
            if color_key_content[idx - 1]:
                color_key_html = (
                    '<div class="paint-color-key-wrapper" style="display:none;">'
                    f'{build_color_key(color_key_content[idx - 1])}'
                    "</div>"
                )
            
            pages.append(
                f'<div class="paint-page" data-page="{idx}" '
                f'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
                '<div style="font-size:20px;font-weight:800;color:#60435F;">'
                f'{titles[idx - 1]}'
                "</div>"
                f'<div data-target-num="" data-target-den="">'
                f'<img src="{image_path}" alt="operation {idx}" style="max-width:220px;height:auto;" />'
                '</div>'
                f"{color_key_html}"
                f"{hint_html}"
                "</div>"
            )
        return (
            '<div class="operations-paint-pages" '
            'style="display:flex;gap:24px;justify-content:center;flex-wrap:wrap;">'
            + "".join(pages)
            + "</div>"
        )
