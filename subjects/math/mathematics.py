from __future__ import annotations
import random
import math
import sqlite3
import os


from models.subject import Subject
from models.topic import Topic


def _load_steps_from_db(topic_name: str | None = None) -> list[dict[str, str]]:
    """Load learning steps from the project SQLite database."""
    project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    candidate_db_paths = [
        os.path.join(project_root, "learning.db"),
        os.path.join(project_root, "Database", "learning.db"),
    ]

    # Prefer DB files that exist; still keep candidates for clearer debug output.
    db_paths = [path for path in candidate_db_paths if os.path.exists(path)] or candidate_db_paths

    table_candidates = ("learning_steps", "operations")

    def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
            (table_name,),
        ).fetchone()
        return row is not None

    for db_path in db_paths:
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                table_name = next((t for t in table_candidates if _table_exists(conn, t)), None)
                if not table_name:
                    continue

                base_query = (
                    "SELECT content_type, topic, item_type, title, explanation, expression, answer "
                    f"FROM {table_name}"
                )

                rows = []
                if topic_name:
                    rows = conn.execute(
                        base_query + " WHERE lower(topic) = lower(?) ORDER BY rowid",
                        (topic_name,),
                    ).fetchall()

                # Some datasets store sub-topics (addition, division, ...). If a strict
                # topic filter is empty, return the table's ordered rows instead.
                if not rows:
                    rows = conn.execute(base_query + " ORDER BY rowid").fetchall()

                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[DEBUG] DB error ({db_path}): {e}")

    print(f"[DEBUG] DB error: no supported table found in {db_paths}")
    return []


def _pie_slice_paths(
    denominator: int,
    size: int,
    radius_padding: int,
    fill_for_slice,
    *,
    stroke: str,
    stroke_width: str,
    large_arc_flag: int,
    extra_attrs_for_slice = None,
) -> str:
    """Build SVG path elements for a denominator-sliced pie."""
    cx = cy = size // 2
    r = cx - radius_padding
    slices = []

    for i in range(denominator):
        start_angle = math.radians(90 + 360 * i / denominator)
        end_angle = math.radians(90 + 360 * (i + 1) / denominator)
        x1 = cx + r * math.cos(start_angle)
        y1 = cy - r * math.sin(start_angle)
        x2 = cx + r * math.cos(end_angle)
        y2 = cy - r * math.sin(end_angle)

        extra_attrs = ""
        if extra_attrs_for_slice is not None:
            attrs = extra_attrs_for_slice(i)
            if attrs:
                extra_attrs = f" {attrs}"

        slices.append(
            f'<path{extra_attrs} d="M{cx},{cy} L{x1:.2f},{y1:.2f} A{r},{r} 0 {large_arc_flag},0 {x2:.2f},{y2:.2f} Z" '
            f'fill="{fill_for_slice(i)}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    return "".join(slices)


def _fraction_svg(numerator: int, denominator: int, size: int = 120, color: str = "#FF8C69") -> str:
    """Return an inline SVG of a pie chart representing numerator/denominator."""
    cx = size // 2
    large = 1 if (1 / denominator) > 0.5 else 0

    paths = _pie_slice_paths(
        denominator,
        size,
        radius_padding=6,
        fill_for_slice=lambda slice_index: color if slice_index < numerator else "#f3f3f3",
        stroke="#60435F",
        stroke_width="1.5",
        large_arc_flag=large,
    )

    label = f"{numerator}/{denominator}"
    return (
        f'<svg width="{size}" height="{size + 20}" xmlns="http://www.w3.org/2000/svg">'
        f'{paths}'
        f'<text x="{cx}" y="{size + 15}" text-anchor="middle" '
        f'font-size="13" font-weight="bold" fill="#60435F" font-family="sans-serif">{label}</text>'
        f'</svg>'
    )


class Fractions(Topic):
    name = "Fractions"
    has_learning = True
    has_painting  = True

    def page_background_image(self) -> str:
        return "/images/Background.png"

    _DENOMINATORS = [2, 3, 4, 5, 6, 8, 10]

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        return {
            "operation": [
                ("all", "All operations"),
                ("add_sub", "Addition + Subtraction"),
                ("mul_div", "Multiplication + Division"),
                ("add", "Addition only"),
                ("sub", "Subtraction only"),
                ("mul", "Multiplication only"),
                ("div", "Division only"),
            ],
            "difficulty": [
                ("mixed", "Mixed"),
                ("easy", "Easy"),
                ("medium", "Medium"),
                ("hard", "Hard"),
            ],
        }

    def default_quiz_filters(self) -> dict[str, str]:
        return {"operation": "all", "difficulty": "mixed"}

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        definitions = self.quiz_filter_definitions()
        defaults = self.default_quiz_filters()
        cleaned: dict[str, str] = {}
        for filter_name, options in definitions.items():
            valid_values = {value for value, _ in options}
            fallback = defaults.get(filter_name, options[0][0])
            value = selected.get(filter_name, fallback)
            cleaned[filter_name] = value if value in valid_values else fallback
        return cleaned

    def set_operation_filter(self, mode: str) -> None:
        # Backward-compatible helper used by older UI code.
        filters = self.default_quiz_filters()
        filters["operation"] = mode
        self._legacy_filters = self.sanitize_quiz_filters(filters)

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective_filters = self.sanitize_quiz_filters(filters or getattr(self, "_legacy_filters", {}))

        operation_groups = {
            "all": ["+", "-", "×", "÷"],
            "add_sub": ["+", "-"],
            "mul_div": ["×", "÷"],
            "add": ["+"],
            "sub": ["-"],
            "mul": ["×"],
            "div": ["÷"],
        }
        denominators_by_difficulty = {
            "mixed": self._DENOMINATORS,
            "easy": [2, 3, 4, 5],
            "medium": [4, 5, 6, 8],
            "hard": [6, 8, 10],
        }

        op = random.choice(operation_groups[effective_filters["operation"]])
        denom = random.choice(denominators_by_difficulty[effective_filters["difficulty"]])

        if op in ("+", "-"):
            a = random.randint(1, denom - 1)
            b = random.randint(1, denom - 1)
            if op == "-":
                a, b = max(a, b), min(a, b)
                if a == b:
                    a = min(a + 1, denom - 1)
            num_result = a + b if op == "+" else a - b
            common = math.gcd(abs(num_result), denom)
            r_num = num_result // common
            r_den = denom // common
            question = f"{a}/{denom} {op} {b}/{denom} = ?"
            answer = str(r_num) if r_den == 1 else f"{r_num}/{r_den}"

        else:  # × or ÷
            a_num = random.randint(1, denom - 1)
            a_den = denom
            b_num = random.randint(1, denom - 1)
            b_den = random.choice([d for d in self._DENOMINATORS if d != denom] or [denom])
            if op == "×":
                r_num = a_num * b_num
                r_den = a_den * b_den
            else:  # ÷  →  a/b_den  (multiply by reciprocal)
                r_num = a_num * b_den
                r_den = a_den * b_num
            common = math.gcd(abs(r_num), r_den)
            r_num //= common
            r_den //= common
            question = f"{a_num}/{a_den} {op} {b_num}/{b_den} = ?"
            answer = str(r_num) if r_den == 1 else f"{r_num}/{r_den}"

        return question, answer

    # visual

    @staticmethod
    def _circles_for_fraction(num: int, den: int, color: str, size: int = 110) -> str:
        """Return one or more SVG circles representing num/den (result can be > 1)."""
        svgs = []
        remaining = num
        while remaining > 0:
            slice_num = min(remaining, den)
            svgs.append(_fraction_svg(slice_num, den, size=size, color=color))
            remaining -= slice_num
        return "".join(svgs)

    def question_visual_html(self, question: str) -> str:
        """Return HTML showing SVG pie charts for each fraction in the question."""
        import re
        fracs = re.findall(r'(\d+)/(\d+)', question)
        if not fracs:
            return ""

        colors  = ["#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1"]
        op_sym  = "+" if "+" in question else "−" if "−" in question or "-" in question else \
                  "×" if "×" in question else "÷"

        parts = []
        for idx, (num, den) in enumerate(fracs):
            circle_html = self._circles_for_fraction(
                int(num), int(den), colors[idx % len(colors)], size=110
            )
            parts.append(
                f'<div style="display:flex;align-items:center;gap:4px;">{circle_html}</div>'
            )

        sep = f'<span style="font-size:28px;font-weight:800;color:#a83432;align-self:center;padding:0 6px;">{op_sym}</span>'
        joined = sep.join(parts)
        return (
            f'<div style="display:flex;align-items:center;gap:8px;justify-content:center;'
            f'flex-wrap:wrap;margin:8px 0;">{joined}</div>'
        )

    # learning steps

    def learning_steps(self) -> list[tuple[str, str, str, str]]:
        return [
            # 3 intro cards
            ("What is a fraction?", "A fraction shows part of a whole. The bottom number (denominator) is how many equal pieces.", "The top number (numerator) is how many pieces you have.", ""),
            ("Same denominator rule", "To add or subtract fractions, the denominators must be the same.", "Keep the denominator, and add or subtract only the numerators!", ""),
            ("Multiply & Divide rule", "To multiply fractions, multiply top × top and bottom × bottom.", "To divide, flip the second fraction and then multiply.", ""),

            # 10 addition / subtraction examples
            ("Adding and subtracting fractions", "It is easy when they have the same denominator.", "", ""),
            ("➕ Example 1", "1/4 + 1/4 = 2/4 = 1/2 — same denominator, just add the tops.", "1/4 + 1/4", "1/2"),
            ("➕ Example 2", "2/6 + 1/6 = 3/6 = 1/2 — three sixths is the same as one half!", "2/6 + 1/6", "1/2"),
            ("➕ Example 3", "3/8 + 3/8 = 6/8 = 3/4 — always simplify by dividing by the common factor.", "3/8 + 3/8", "3/4"),
            ("➕ Example 4", "1/3 + 1/3 = 2/3 — two thirds of a whole.", "1/3 + 1/3", "2/3"),
            ("➕ Example 5", "4/10 + 3/10 = 7/10 — the denominator stays 10.", "4/10 + 3/10", "7/10"),
            ("➖ Example 6", "3/4 − 1/4 = 2/4 = 1/2 — subtract the tops, keep the bottom.", "3/4 - 1/4", "1/2"),
            ("➖ Example 7", "5/6 − 2/6 = 3/6 = 1/2 — three sixths simplifies to one half.", "5/6 - 2/6", "1/2"),
            ("➖ Example 8", "7/8 − 3/8 = 4/8 = 1/2 — divide both by 4 to simplify.", "7/8 - 3/8", "1/2"),
            ("➖ Example 9", "4/5 − 1/5 = 3/5 — three fifths remaining.", "4/5 - 1/5", "3/5"),
            ("➖ Example 10", "9/10 − 4/10 = 5/10 = 1/2 — five tenths is the same as one half.", "9/10 - 4/10", "1/2"),

            # multiplication / division examples
            ("✖️ Multiplying fractions", "Find a fraction of a fraction: multiply top × top and bottom × bottom.", "", ""),
            ("✖️ Example 1", "1/2 × 1/2 = 1/4 — multiply tops: 1×1=1; bottoms: 2×2=4.", "1/2 * 1/2", "1/4"),
            ("✖️ Example 2", "2/3 × 3/4 = 6/12 = 1/2 — simplify by dividing top and bottom by 6.", "2/3 * 3/4", "1/2"),
            ("✖️ Example 3", "3/4 × 2/3 = 6/12 = 1/2 — same as above, order does not matter!", "3/4 * 2/3", "1/2"),
            ("✖️ Example 4", "1/3 × 1/3 = 1/9 — a third of a third is a ninth.", "1/3 * 1/3", "1/9"),
            ("✖️ Example 5", "2/5 × 5/6 = 10/30 = 1/3 — simplify 10 and 30 by dividing by 10.", "2/5 * 5/6", "1/3"),
            ("➗ Dividing fractions", "Ask how many of the second fraction fit into the first one, then flip and multiply.", "", ""),
            ("➗ Example 6", "1/2 ÷ 1/4 = 1/2 × 4/1 = 4/2 = 2 — flip the second fraction then multiply.", "1/2 / 1/4", "2"),
            ("➗ Example 7", "3/4 ÷ 3/8 = 3/4 × 8/3 = 24/12 = 2 — the answer is 2 whole circles!", "3/4 / 3/8", "2"),
            ("➗ Example 8", "2/3 ÷ 1/3 = 2/3 × 3/1 = 6/3 = 2 — how many thirds fit in two thirds? Two!", "2/3 / 1/3", "2"),
            ("➗ Example 9", "5/6 ÷ 5/12 = 5/6 × 12/5 = 60/30 = 2 — flip and multiply.", "5/6 / 5/12", "2"),
            ("➗ Example 10", "1/4 ÷ 1/8 = 1/4 × 8/1 = 8/4 = 2 — two eighths fit in every quarter.", "1/4 / 1/8", "2"),
        ]

    def step_visual_html(self, step_index: int) -> str:
        """Return a visual for each learning card."""
        colors = ["#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1"]
        color = colors[step_index % len(colors)]

        def render_pair(a_n: int, a_d: int, b_n: int, b_d: int, op: str) -> str:
            svg_a = _fraction_svg(a_n, a_d, size=80, color=color)
            svg_b = _fraction_svg(b_n, b_d, size=80, color="#FFAD05" if color != "#FFAD05" else "#7EC88A")
            sep = f'<span style="font-size:22px;font-weight:800;color:#a83432;">{op}</span>'
            return f'<div style="display:flex;align-items:center;gap:4px;">{svg_a}{sep}{svg_b}</div>'

        # intro cards 0-2: plain circles showing halves/thirds/quarters
        if step_index < 3:
            denom = step_index + 2
            return _fraction_svg(1, denom, size=90, color=color)

        # section header card
        if step_index == 3:
            return render_pair(1, 4, 1, 4, "+")

        # +/- examples: indices 4-13 (examples 1-10)
        add_examples = [
            (1, 4, 1, 4, "+"), (2, 6, 1, 6, "+"), (3, 8, 3, 8, "+"), (1, 3, 1, 3, "+"), (4, 10, 3, 10, "+"),
            (3, 4, 1, 4, "−"), (5, 6, 2, 6, "−"), (7, 8, 3, 8, "−"), (4, 5, 1, 5, "−"), (9, 10, 4, 10, "−"),
        ]
        if 4 <= step_index <= 13:
            return render_pair(*add_examples[step_index - 4])

        # multiplication section header card
        if step_index == 14:
            return render_pair(1, 2, 1, 2, "×")

        # × examples: indices 15-19 (examples 1-5)
        mul_examples = [
            (1, 2, 1, 2, "×"), (2, 3, 3, 4, "×"), (3, 4, 2, 3, "×"), (1, 3, 1, 3, "×"), (2, 5, 5, 6, "×"),
        ]
        if 15 <= step_index <= 19:
            return render_pair(*mul_examples[step_index - 15])

        # division section header card
        if step_index == 20:
            return render_pair(1, 2, 1, 4, "÷")

        # ÷ examples: indices 21-25 (examples 6-10)
        div_examples = [
            (1, 2, 1, 4, "÷"), (3, 4, 3, 8, "÷"), (2, 3, 1, 3, "÷"), (5, 6, 5, 12, "÷"), (1, 4, 1, 8, "÷"),
        ]
        if 21 <= step_index <= 25:
            return render_pair(*div_examples[step_index - 21])

        return ""

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        """Accept any numerically equivalent form: 2/4, 1/2, 0.5, 4/8 etc."""
        from fractions import Fraction

        def _parse(text: str):
            text = text.strip().replace(" ", "")
            if not text:
                return None
            try:
                if "/" in text:
                    parts = text.split("/")
                    if len(parts) != 2:
                        return None
                    n, d = int(parts[0]), int(parts[1])
                    return None if d == 0 else Fraction(n, d)
                return Fraction(float(text)).limit_denominator(1000)
            except (ValueError, ZeroDivisionError):
                return None

        if not user.strip():
            return False, "Please enter an answer."
        u = _parse(user)
        if u is None:
            return False, "Enter a number or fraction (e.g. 3/4 or 0.5)"
        c = _parse(correct)
        return u == c, ""

    def paint_visual_html(self) -> str:
        """Render fraction-specific paint cards with one circle per card."""

        def _blank_paint_circle_svg(denominator: int, size: int = 180) -> str:
            paths = _pie_slice_paths(
                denominator,
                size,
                radius_padding=8,
                fill_for_slice=lambda _slice_index: "#ffffff",
                stroke="#60435F",
                stroke_width="2",
                large_arc_flag=0,
                extra_attrs_for_slice=lambda slice_index: f'class="paint-slice" data-slice="{slice_index}"',
            )

            return (
                f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
                f'xmlns="http://www.w3.org/2000/svg">{paths}</svg>'
            )

        targets = [(1, 2), (2, 3), (2, 7)]
        pages = []
        for idx, (num, den) in enumerate(targets, start=1):
            pages.append(
                f'<div class="paint-page" data-page="{idx}" '
                f'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
                f'<div style="font-size:20px;font-weight:800;color:#60435F;">'
                f'Paint {num}/{den}'
                f'</div>'
                f'<div data-target-num="{num}" data-target-den="{den}">{_blank_paint_circle_svg(den)}</div>'
                f'</div>'
            )
        return (
            '<div class="fractions-paint-pages" '
            'style="display:flex;gap:24px;justify-content:center;flex-wrap:wrap;">'
            + "".join(pages)
            + "</div>"
        )


class Operation(Topic):
    name = "Operations"
    has_painting = True
    def page_background_image(self) -> str:
        return "/images/Math_back.png"

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        return {
            "operation": [
                ("all", "All operations"),
                ("add_sub", "Addition + Subtraction"),
                ("mul_div", "Multiplication + Division"),
                ("add", "Addition only"),
                ("sub", "Subtraction only"),
                ("mul", "Multiplication only"),
                ("div", "Division only"),
            ],
            "difficulty": [
                ("mixed", "Mixed"),
                ("easy", "Easy"),
                ("medium", "Medium"),
                ("hard", "Hard"),
            ],
        }

    def default_quiz_filters(self) -> dict[str, str]:
        return {"operation": "all", "difficulty": "mixed"}

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        definitions = self.quiz_filter_definitions()
        defaults = self.default_quiz_filters()
        cleaned: dict[str, str] = {}
        for filter_name, options in definitions.items():
            valid_values = {value for value, _ in options}
            fallback = defaults.get(filter_name, options[0][0])
            value = selected.get(filter_name, fallback)
            cleaned[filter_name] = value if value in valid_values else fallback
        return cleaned

    def set_operation_filter(self, mode: str) -> None:
        # Backward-compatible helper used by older UI code.
        filters = self.default_quiz_filters()
        filters["operation"] = mode
        self._legacy_filters = self.sanitize_quiz_filters(filters)

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective_filters = self.sanitize_quiz_filters(filters or getattr(self, "_legacy_filters", {}))

        operation_groups = {
            "all": ["+", "-", "×", "÷"],
            "add_sub": ["+", "-"],
            "mul_div": ["×", "÷"],
            "add": ["+"],
            "sub": ["-"],
            "mul": ["×"],
            "div": ["÷"],
        }
        digit_by_difficulty = {
            "mixed": (1,1000),
            "easy": range(1,12),
            "medium": range(12,100),
            "hard": range(100,1000),
        }

        op = random.choice(operation_groups[effective_filters["operation"]])
        digit = random.choice(digit_by_difficulty[effective_filters["difficulty"]])

        if op in ("+", "-"):
            a = random.randint(1, digit)
            b = random.randint(1, digit)
            if op == "-":
                a, b = max(a, b), min(a, b)
            question = f"{a} {op} {b} = ?"
            num_result = a + b if op == "+" else a - b
        elif op == "×":
            a = random.randint(1, digit)
            b = random.randint(1, digit)
            question = f"{a} {op} {b} = ?"
            num_result = a * b
        else:
            num_result = random.randint(1, digit)
            b = random.randint(1, max(1, digit))
            a = b * num_result
            question = f"{a} {op} {b} = ?"
        return question, str(num_result)

    def learning_steps(self) -> list[tuple[str, str, str, str]]:
        """Load steps from learning.db for topic `Operations`, returning title, explanation, expression, and answer."""
        steps = _load_steps_from_db("operation")
        if steps:
            return [
                (
                    row.get("title") or "",
                    row.get("explanation") or "",
                    row.get("expression") or "",
                    row.get("answer") or ""
                )
                for row in steps
            ]
        return [
            ("", "", "", "")
        ]

    def paint_visual_html(self) -> str:
         targets = ["/images/Operation_painting1.png", "/images/Operation_painting1.png", "/images/Operation_painting2.png"]
         pages = []
         for idx, image_path in enumerate(targets, start=1):
             pages.append(
             f'<div class="paint-page" data-page="{idx}" '
             f'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
             f'<div style="font-size:20px;font-weight:800;color:#60435F;">'
             f'</div>'
             f'<img src="{image_path}" alt="operation {idx}" style="max-width:220px;height:auto;" />'
             f'</div>'
             )
         return (
         '<div class="operations-paint-pages" '
         'style="display:flex;gap:24px;justify-content:center;flex-wrap:wrap;">'
         + "".join(pages)
         + "</div>"
         )


class Math(Subject):
    name = "Math"
    url_slug = "math"
    icon = "/images/icons/notebook.svg"
    topics: list[Topic] = [
        Fractions(),
        Operation(),
    ]

    def page_background_image(self) -> str:
        return "/images/Math_back.png"
