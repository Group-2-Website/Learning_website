from __future__ import annotations

from nicegui import ui
from subjects import SUBJECTS
from ui.builders import (add_global_css, build_topbar, build_home_page,
                         build_subject_topics_page, build_topic_mode_page,
                         build_quiz_page, build_learn_page)


@ui.page('/')
def home():
    add_global_css()
    build_topbar()
    build_home_page()


def _register_subject(subject):
    slug = subject.url_slug

    @ui.page(f'/{slug}')
    def subject_page(_s=subject):
        add_global_css()
        build_topbar()
        build_subject_topics_page(_s)

    for topic in subject.topics:
        _register_topic(subject, topic)


def _register_topic(subject, topic):
    slug       = subject.url_slug
    topic_slug = topic.name.lower()

    @ui.page(f'/{slug}/{topic_slug}')
    def topic_mode_page(_s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_topic_mode_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/quiz')
    def topic_quiz_page(_s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_quiz_page(_s, _t)

    if topic.has_learning:
        @ui.page(f'/{slug}/{topic_slug}/learn')
        def topic_learn_page(_s=subject, _t=topic):
            add_global_css()
            build_topbar()
            build_learn_page(_s, _t)
