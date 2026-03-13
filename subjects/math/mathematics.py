from __future__ import annotations
import random
import math
from models.subject import Subject
from models.topic import Topic


def _fraction_svg(numerator: int, denominator: int, size: int = 120, color: str = "#FF8C69") -> str:
    """Return an inline SVG of a pie chart representing numerator/denominator."""
    cx = cy = size // 2
    r = cx - 6
    slices = []

    for i in range(denominator):
        start_angle = math.radians(90 + 360 * i / denominator)
        end_angle   = math.radians(90 + 360 * (i + 1) / denominator)
        x1 = cx + r * math.cos(start_angle)
        y1 = cy - r * math.sin(start_angle)
        x2 = cx + r * math.cos(end_angle)
        y2 = cy - r * math.sin(end_angle)
        fill = color if i < numerator else "#f3f3f3"
        large = 1 if (1 / denominator) > 0.5 else 0
        slices.append(
            f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} A{r},{r} 0 {large},0 {x2:.2f},{y2:.2f} Z" '
            f'fill="{fill}" stroke="#60435F" stroke-width="1.5"/>'
        )

    label = f"{numerator}/{denominator}"
    paths = "".join(slices)
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

    def learn_page_subtitle(self) -> str:
        return "Each circle shows a whole split into equal parts — that's a fraction!"

    def page_background_image(self) -> str:
        return "/images/Background.png"

    _DENOMINATORS = [2, 3, 4, 5, 6, 8, 10]

    #  question generation

    def generate_question(self) -> tuple[str, str]:
        denom = random.choice(self._DENOMINATORS)
        op    = random.choice(["+", "-", "×", "÷"])

        if op in ("+", "-"):
            a = random.randint(1, denom - 1)
            b = random.randint(1, denom - 1)
            if op == "-":
                a, b = max(a, b), min(a, b)
                if a == b:
                    a = min(a + 1, denom - 1)
            num_result = a + b if op == "+" else a - b
            common = math.gcd(abs(num_result), denom)
            r_num  = num_result // common
            r_den  = denom   // common
            question = f"{a}/{denom} {op} {b}/{denom} = ?"
            answer   = str(r_num) if r_den == 1 else f"{r_num}/{r_den}"

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
            answer   = str(r_num) if r_den == 1 else f"{r_num}/{r_den}"

        return question, answer

    # ── visual ───────────────────────────────────────────────────────────────

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

    # ── learning steps ───────────────────────────────────────────────────────

    def learning_steps(self) -> list[tuple[str, str]]:
        return [
            # ── 3 intro cards ──────────────────────────────────────────────
            ("What is a fraction?",
             "A fraction shows part of a whole. The bottom number (denominator) is how many equal pieces. "
             "The top number (numerator) is how many pieces you have."),
            ("Same denominator rule",
             "To add or subtract fractions, the denominators must be the same. "
             "Keep the denominator, and add or subtract only the numerators!"),
            ("Multiply & Divide rule",
             "To multiply fractions, multiply top × top and bottom × bottom. "
             "To divide, flip the second fraction and then multiply."),

            # ── 10 addition / subtraction examples ────────────────────────
            ("➕ Example 1",  "1/4 + 1/4 = 2/4 = 1/2 — same denominator, just add the tops."),
            ("➕ Example 2",  "2/6 + 1/6 = 3/6 = 1/2 — three sixths is the same as one half!"),
            ("➕ Example 3",  "3/8 + 3/8 = 6/8 = 3/4 — always simplify by dividing by the common factor."),
            ("➕ Example 4",  "1/3 + 1/3 = 2/3 — two thirds of a whole."),
            ("➕ Example 5",  "4/10 + 3/10 = 7/10 — the denominator stays 10."),
            ("➖ Example 6",  "3/4 − 1/4 = 2/4 = 1/2 — subtract the tops, keep the bottom."),
            ("➖ Example 7",  "5/6 − 2/6 = 3/6 = 1/2 — three sixths simplifies to one half."),
            ("➖ Example 8",  "7/8 − 3/8 = 4/8 = 1/2 — divide both by 4 to simplify."),
            ("➖ Example 9",  "4/5 − 1/5 = 3/5 — three fifths remaining."),
            ("➖ Example 10", "9/10 − 4/10 = 5/10 = 1/2 — five tenths is the same as one half."),

            # ── 10 multiplication / division examples ─────────────────────
            ("✖️ Example 1",  "1/2 × 1/2 = 1/4 — multiply tops: 1×1=1; bottoms: 2×2=4."),
            ("✖️ Example 2",  "2/3 × 3/4 = 6/12 = 1/2 — simplify by dividing top and bottom by 6."),
            ("✖️ Example 3",  "3/4 × 2/3 = 6/12 = 1/2 — same as above, order does not matter!"),
            ("✖️ Example 4",  "1/3 × 1/3 = 1/9 — a third of a third is a ninth."),
            ("✖️ Example 5",  "2/5 × 5/6 = 10/30 = 1/3 — simplify 10 and 30 by dividing by 10."),
            ("➗ Example 6",  "1/2 ÷ 1/4 = 1/2 × 4/1 = 4/2 = 2 — flip the second fraction then multiply."),
            ("➗ Example 7",  "3/4 ÷ 3/8 = 3/4 × 8/3 = 24/12 = 2 — the answer is 2 whole circles!"),
            ("➗ Example 8",  "2/3 ÷ 1/3 = 2/3 × 3/1 = 6/3 = 2 — how many thirds fit in two thirds? Two!"),
            ("➗ Example 9",  "5/6 ÷ 5/12 = 5/6 × 12/5 = 60/30 = 2 — flip and multiply."),
            ("➗ Example 10", "1/4 ÷ 1/8 = 1/4 × 8/1 = 8/4 = 2 — two eighths fit in every quarter."),
        ]

    def step_visual_html(self, step_index: int) -> str:
        """Return a visual for each learning card."""
        colors = ["#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1",
                  "#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1",
                  "#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1",
                  "#7EC88A", "#FFAD05", "#6BBFFF", "#FF8C69", "#D67AB1",
                  "#7EC88A", "#FFAD05", "#6BBFFF"]
        color = colors[step_index % len(colors)]

        # intro cards 0-2: plain circles showing halves/thirds/quarters
        if step_index < 3:
            denom = step_index + 2
            return _fraction_svg(1, denom, size=90, color=color)

        # +/- examples: index 3-12  (examples 1-10)
        if step_index < 13:
            ex = step_index - 3   # 0..9
            add_examples = [
                (1,4,1,4), (2,6,1,6), (3,8,3,8), (1,3,1,3), (4,10,3,10),
                (3,4,1,4), (5,6,2,6), (7,8,3,8), (4,5,1,5), (9,10,4,10),
            ]
            a_n, a_d, b_n, b_d = add_examples[ex]
            op = "+" if ex < 5 else "−"
            svg_a = _fraction_svg(a_n, a_d, size=80, color=color)
            svg_b = _fraction_svg(b_n, b_d, size=80, color="#FFAD05" if color != "#FFAD05" else "#7EC88A")
            sep = f'<span style="font-size:22px;font-weight:800;color:#a83432;">{op}</span>'
            return f'<div style="display:flex;align-items:center;gap:4px;">{svg_a}{sep}{svg_b}</div>'

        # ×/÷ examples: index 13-22 (examples 1-10)
        mul_examples = [
            (1,2,1,2,'×'), (2,3,3,4,'×'), (3,4,2,3,'×'), (1,3,1,3,'×'), (2,5,5,6,'×'),
            (1,2,1,4,'÷'), (3,4,3,8,'÷'), (2,3,1,3,'÷'), (5,6,5,12,'÷'), (1,4,1,8,'÷'),
        ]
        ex = step_index - 13
        if ex < 0 or ex >= len(mul_examples):
            return ""
        a_n, a_d, b_n, b_d, op = mul_examples[ex]
        svg_a = _fraction_svg(a_n, a_d, size=80, color=color)
        svg_b = _fraction_svg(b_n, b_d, size=80, color="#FFAD05" if color != "#FFAD05" else "#7EC88A")
        sep = f'<span style="font-size:22px;font-weight:800;color:#a83432;">{op}</span>'
        return f'<div style="display:flex;align-items:center;gap:4px;">{svg_a}{sep}{svg_b}</div>'

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


class Math(Subject):
    name = "Math"
    url_slug = "math"
    topics: list[Topic] = [
        Fractions(),
    ]





