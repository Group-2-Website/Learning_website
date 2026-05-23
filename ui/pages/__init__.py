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
from ui.pages.filter import build_quiz_filter_page, build_learn_filter_page
from ui.pages.history import build_quiz_history_page


def _setup_page() -> None:
    """Call on every page: inject global CSS then render the top navigation bar."""
    add_global_css()
    build_topbar()


@ui.page('/')
def home():
    _setup_page()
    build_home_page()


def register_subject(subject):
    slug = subject.url_slug

    @ui.page(f'/{slug}')
    def subject_page(_s=subject):
        _setup_page()
        build_subject_page(_s)

    for topic in subject.topics:
        _register_topic(subject, topic)


def _register_topic(subject, topic):
    slug = subject.url_slug
    topic_slug = topic.name.lower()

    @ui.page(f'/{slug}/{topic_slug}')
    def topic_mode_page(_s=subject, _t=topic):
        _setup_page()
        build_topic_mode_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/filter')
    def topic_filter_page(_s=subject, _t=topic):
        _setup_page()
        build_quiz_filter_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/quiz')
    def topic_quiz_page(request: Request, _s=subject, _t=topic):
        _setup_page()
        filters = dict(request.query_params)
        build_quiz_page(_s, _t, filters)

    @ui.page(f'/{slug}/{topic_slug}/results')
    def topic_results_page(score: int = 0, attempts: int = 0, _s=subject, _t=topic):
        _setup_page()
        build_quiz_results_page(_s, _t, score, attempts)

    @ui.page(f'/{slug}/{topic_slug}/history')
    def topic_history_page(_s=subject, _t=topic):
        _setup_page()
        build_quiz_history_page(_s, _t)

    if topic.has_learning:
        if topic.learn_filter_definitions():
            @ui.page(f'/{slug}/{topic_slug}/learn-filter')
            def topic_learn_filter_page(_s=subject, _t=topic):
                _setup_page()
                build_learn_filter_page(_s, _t)

        @ui.page(f'/{slug}/{topic_slug}/learn')
        def topic_learn_page(request: Request, _s=subject, _t=topic):
            _setup_page()
            filters = dict(request.query_params)
            if filters:
                _t.apply_learn_filters(filters)
            build_learn_page(_s, _t)

    if topic.has_painting:
        @ui.page(f'/{slug}/{topic_slug}/paint')
        def topic_paint_page(_s=subject, _t=topic):
            _setup_page()
            build_paint_page(_s, _t)

        @ui.page(f'/{slug}/{topic_slug}/paint/{{page_index}}')
        def topic_paint_detail_page(page_index: int, _s=subject, _t=topic):
            _setup_page()
            build_paint_page(_s, _t, page_index)


__all__ = ['register_subject']
