from subjects.math.mathematics import Math
from models.subject import Subject

# ── Register every subject here.
# ── main.py imports this list and auto-generates all routes.
SUBJECTS: list[Subject] = [
    Math(),

]

