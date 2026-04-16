from nicegui import ui, app
from subjects import SUBJECTS
from ui.pages import register_subject

# Register the TTS audio endpoint (lives in subjects/language/tts.py)

for _subject in SUBJECTS:
    register_subject(_subject)

app.add_static_files('/images', 'images')
ui.run(title="E-learning for kids", port=8081, reload=True, favicon="hamster.ico")
