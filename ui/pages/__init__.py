from __future__ import annotations

from nicegui import ui
from starlette.requests import Request

from ui.pages.common import add_global_css, build_topbar
from ui.pages.home import build_home_page
from ui.pages.learn import build_learn_page
from ui.pages.paint import build_paint_page
from ui.pages.quiz import build_quiz_page
from ui.pages.quiz_results import build_quiz_results_page
from ui.pages.topic import build_topic_mode_page
from ui.pages.subject import build_subject_page
from ui.pages.filter import build_quiz_filter_page


@ui.page('/')
def home():
    add_global_css()
    build_topbar()
    build_home_page()


def register_subject(subject):
    slug = subject.url_slug

    @ui.page(f'/{slug}')
    def subject_page(_s=subject):
        add_global_css()
        build_topbar()
        build_subject_page(_s)

    for topic in subject.topics:
        _register_topic(subject, topic)


def _register_topic(subject, topic):
    slug = subject.url_slug
    topic_slug = topic.name.lower()

    @ui.page(f'/{slug}/{topic_slug}')
    def topic_mode_page(_s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_topic_mode_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/filter')
    def topic_filter_page(_s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_quiz_filter_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/quiz')
    def topic_quiz_page(request: Request, _s=subject, _t=topic):
        add_global_css()
        build_topbar()
        filters = dict(request.query_params)
        build_quiz_page(_s, _t, filters)

    @ui.page(f'/{slug}/{topic_slug}/results')
    def topic_results_page(score: int = 0, attempts: int = 0, _s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_quiz_results_page(_s, _t, score, attempts)

    if topic.has_learning:
        @ui.page(f'/{slug}/{topic_slug}/learn')
        def topic_learn_page(_s=subject, _t=topic):
            add_global_css()
            build_topbar()
            build_learn_page(_s, _t)

    if topic.has_painting:
        @ui.page(f'/{slug}/{topic_slug}/paint')
        def topic_paint_page(_s=subject, _t=topic):
            add_global_css()
            build_topbar()
            build_paint_page(_s, _t)


__all__ = ['register_subject']
