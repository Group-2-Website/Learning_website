from __future__ import annotations
from fractions import Fraction
import random
import math
import re

from sqlalchemy import func, inspect
from Database.Learning import Session, Operation as DBOperation, Fraction as DBFraction
from models.subject import Subject
from models.topic import Topic

_TABLE_MODEL_MAP = {
    "operations": DBOperation,
    "fractions": DBFraction,
}
_TABLE_CANDIDATES = ("operations", "fractions")


def _load_steps_from_db(
    topic_name: str | None = None,
    table: str | None = None,
) -> list[dict[str, str]]:
    """Load learning steps from the database via SQLAlchemy.
     If topic_name is given, filter steps by topic. If table is given, query that specific table;
     otherwise auto-detect which table to use based on existing tables and topic name. """
    session = Session()
    try:
        # Resolve which model/table to query
        model = None
        if table and table in _TABLE_MODEL_MAP:
            model = _TABLE_MODEL_MAP[table]
        else:
            engine = session.get_bind()
            inspector = inspect(engine)
            existing = set(inspector.get_table_names())
            for candidate in _TABLE_CANDIDATES:
                if candidate in existing and candidate in _TABLE_MODEL_MAP:
                    model = _TABLE_MODEL_MAP[candidate]
                    break

        if model is None:
            return []

        query = session.query(model)
        if topic_name:
            query = query.filter(func.lower(model.topic) == topic_name.lower())
        rows = query.order_by(model.id).all()

        # Fallback: if topic filter yielded nothing, return all rows
        if not rows and topic_name:
            rows = session.query(model).order_by(model.id).all()

        columns = ["content_type", "topic", "item_type", "title", "explanation", "expression", "answer", "image"]
        return [{col: getattr(row, col, "") or "" for col in columns} for row in rows]
    except Exception as e:
        print(f"[DEBUG] DB error: {e}")
        return []
    finally:
        session.close()


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


def _normalize_operator_symbol(op: str) -> str:
    return {"*": "×", "/": "÷", "-": "−"}.get(op, op)


def _parse_binary_expression(expression: str) -> tuple[str, str, str] | None:
    """Parse expressions like '2/3 + 1/3', '3 + (-1)', '6 / 2'."""
    token = r"[-+]?\(?\d+(?:/\d+)?\)?"
    match = re.match(rf"^\s*({token})\s*([+\-*/×÷−])\s*({token})\s*$", expression or "")
    if not match:
        return None
    left, op, right = match.groups()
    return left.strip(), _normalize_operator_symbol(op), right.strip()


def _token_to_fraction(token: str) -> Fraction | None:
    cleaned = (token or "").replace("(", "").replace(")", "").strip()
    if not cleaned:
        return None
    try:
        return Fraction(cleaned)
    except (ValueError, ZeroDivisionError):
        return None


class Fractions(Topic):
    name = "Fractions"
    has_learning = True
    has_painting  = True

    def page_background_image(self) -> str:
        return "/images/circle.jpeg"

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
            "number of questions": [(str(n), f"{n} questions") for n in [5, 10, 15, 20]],
        }

    def default_quiz_filters(self) -> dict[str, str]:
        return {"operation": "all", "difficulty": "mixed", "number of questions": "10"}

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective_filters = self.sanitize_quiz_filters(filters or {})

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

    def learning_steps(self) -> list[tuple[str, str, str, str, str]]:
        rows = _load_steps_from_db("fractions", table="fractions")
        self._step_rows = rows
        if rows:
            self._step_images = [r.get("image") or "" for r in rows]
            return [
                (
                    r.get("title") or "",
                    r.get("image") or "",
                    r.get("explanation") or "",
                    r.get("expression") or "",
                    r.get("answer") or "",
                )
                for r in rows
            ]
        self._step_images = []
        return []

    def step_visual_html(self, step_index: int) -> str:
        """Return a DB-driven visual for each learning card."""
        base = super().step_visual_html(step_index)
        rows = getattr(self, "_step_rows", None)
        if rows is None:
            rows = _load_steps_from_db("fractions", table="fractions")
            self._step_rows = rows
        if step_index < 0 or step_index >= len(rows):
            return base

        row = rows[step_index]
        expression = (row.get("expression") or "").strip()
        parsed = _parse_binary_expression(expression)
        if not parsed:
            return base

        left_t, op, right_t = parsed
        left_f = _token_to_fraction(left_t)
        right_f = _token_to_fraction(right_t)
        if left_f is None or right_f is None:
            return base

        colors = ["#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1"]
        left_color = colors[step_index % len(colors)]
        right_color = colors[(step_index + 1) % len(colors)]

        left_svg = self._circles_for_fraction(left_f.numerator, left_f.denominator, left_color, size=78)
        right_svg = self._circles_for_fraction(right_f.numerator, right_f.denominator, right_color, size=78)

        answer_f = _token_to_fraction((row.get("answer") or "").strip())
        if answer_f is not None and answer_f.denominator == 1:
            # Keep whole-number outcomes as plain numbers, not forced fraction pies.
            answer_visual = (
                '<div style="min-width:46px;height:46px;border-radius:999px;background:#96c97d;'
                'display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#60435F;">'
                f'{answer_f.numerator}'
                '</div>'
            )
        elif answer_f is not None:
            answer_visual = self._circles_for_fraction(answer_f.numerator, answer_f.denominator, colors[(step_index + 2) % len(colors)], size=78)
        else:
            answer_visual = ""

        equation = (
            '<div style="display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap;">'
            f'<div style="display:flex;align-items:center;">{left_svg}</div>'
            f'<span style="font-size:22px;font-weight:800;color:#a83432;">{op}</span>'
            f'<div style="display:flex;align-items:center;">{right_svg}</div>'
        )
        if answer_visual:
            equation += (
                '<span style="font-size:22px;font-weight:800;color:#60435F;">=</span>'
                f'<div style="display:flex;align-items:center;">{answer_visual}</div>'
            )
        equation += '</div>'
        return base + equation

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        """Accept any numerically equivalent form: 2/4, 1/2, 0.5, 4/8 etc."""

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
        hint_colors = ["#7EC88A", "#FFAD05", "#6BBFFF"]
        pages = []
        for idx, (num, den) in enumerate(targets, start=1):
            hint_svg = _fraction_svg(num, den, size=180, color=hint_colors[(idx - 1) % len(hint_colors)])
            pages.append(
                f'<div class="paint-page" data-page="{idx}" '
                f'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
                f'<div style="font-size:20px;font-weight:800;color:#60435F;">'
                f'Paint {num}/{den}'
                f'</div>'
                f'<div data-target-num="{num}" data-target-den="{den}">{_blank_paint_circle_svg(den)}</div>'
                f'<div class="paint-hint" style="display:none;">{hint_svg}</div>'
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
        return "/images/operation.jpg"

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
            "number of questions": [(str(n), f"{n} questions") for n in [5, 10, 15, 20]],

            "row": [(str(i), f"Row {i}") for i in range(1, 13)],
        }

    def default_quiz_filters(self) -> dict[str, str]:
        return {"operation": "all", "difficulty": "mixed", "number of questions": "10"}

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective_filters = self.sanitize_quiz_filters(filters or {})

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


    def learning_steps(self) -> list[tuple[str, str,str,str, str]]:
        steps = _load_steps_from_db(table="operations")
        if steps:
            self._step_images = [row.get("image") or "" for row in steps]
            return [
                (
                    row.get("title") or "",
                    row.get("image") or "",
                    row.get("explanation") or "",
                    row.get("expression") or "",
                    row.get("answer") or ""
                )
                for row in steps
            ]
        self._step_images = []
        return [
            ("", "","" ,"", "")
        ]

    def step_visual_html(self, step_index: int) -> str:
        base = super().step_visual_html(step_index)

        def group(rows, cols):
            return "".join([
                f'<div style="display:flex;gap:6px;font-size:25px;">{"🍎" * cols}</div>'
                for _ in range(rows)
            ])

        def people(p, a):
            return "".join([
                f'<div style="text-align:center;font-size:25px;">●<br>{"🍎" * a}</div>'
                for _ in range(p)
            ])
        if step_index == 15:
            return base + f'''
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
                {group(2, 3)}
            </div>
            '''
        if step_index == 16:
            return base + f'''
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;">
                {group(2, 4)}
            </div>
            '''
        if step_index == 18:
            return base + f'''
            <div style="display:flex;justify-content:center;gap:40px;">
                {people(2, 3)}
            </div>
            '''
        if step_index == 19:
            return base + f'''
            <div style="display:flex;justify-content:center;gap:30px;">
                {people(4, 2)}
            </div>
            '''

        return base


    def paint_visual_html(self) -> str:
        targets = ["", "/images/Operation_painting2.png", ""]
        hints = ["", "/images/math-sol.png", ""]
        pages = []
        for idx, image_path in enumerate(targets, start=1):
            hint_html = ""
            if hints[idx - 1]:
                hint_html = (
                    f'<div class="paint-hint" style="display:none;">'
                    f'<img src="{hints[idx - 1]}" alt="hint {idx}" style="max-width:400px;height:auto;" />'
                    f'</div>'
                )
            pages.append(
                f'<div class="paint-page" data-page="{idx}" '
                f'style="display:flex;flex-direction:column;align-items:center;gap:10px;margin:10px 0;">'
                f'<div style="font-size:20px;font-weight:800;color:#60435F;">'
                f'</div>'
                f'<img src="{image_path}" alt="operation {idx}" style="max-width:220px;height:auto;" />'
                f'{hint_html}'
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
        return "/images/operation.jpg"
