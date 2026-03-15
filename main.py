from __future__ import annotations
from nicegui import ui, app
from subjects import SUBJECTS
from ui.pages import register_subject


for _subject in SUBJECTS:
    register_subject(_subject)

app.add_static_files('/images', 'images')
ui.run(title="E-learning for kids", port=8081, reload=True)