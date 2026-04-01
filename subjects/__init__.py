from subjects.language.Language_selection import Language
from subjects.math.mathematics import Math
from subjects.science.science import Science
from models.subject import Subject

# ── Register every subject here.
# ── main.py imports this list and auto-generates all routes.
SUBJECTS: list[Subject] = [
    Math(), Language(), Science()

]

