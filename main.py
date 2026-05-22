from nicegui import ui, app
from subjects import SUBJECTS
from ui.pages import register_subject
from subjects.language import tts


def main():
    tts.init()

    for _subject in SUBJECTS:
        register_subject(_subject)

    app.add_static_files('/images', 'images')
    app.add_static_files('/static', 'static')

    ui.run(title="E-learning for kids", port=8082, reload=False, favicon='static/favicon.png')


if __name__ in {"__main__", "__mp_main__"}:
    main()
