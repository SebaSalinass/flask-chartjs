from typing import Optional, Callable, Dict, Any

from flask import Flask, Blueprint, render_template, render_template_string
from markupsafe import Markup
from .chart import Chart, DataSet


__all__ = ('ChartJS', 'Chart', 'DataSet')


class ChartJS:

    app: Optional[Flask]
    config: Optional[dict]
    _blueprint: Blueprint
    _nonce_callback: Optional[Callable[[], str]] = None

    def __init__(self, app: Optional[Flask] = None) -> None:
        self._blueprint = Blueprint('chartjs', __name__, template_folder='templates', static_folder='static')

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.app = app
        self.app.register_blueprint(self._blueprint)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['chartjs'] = self

        @app.context_processor
        def inject_context_variables() -> dict:
            return dict(load_chartjs=self._render_load_chartjs, render_chart=self._render_chart)

    def _render_load_chartjs(self) -> Markup:
        return Markup(render_template('load_chartjs.jinja'))

    def _render_chart(self, chart: Chart, options: Dict[str, Any], html_only: bool = False,
                      js_only: bool = False, use_htmx: bool = False) -> Markup:
        html_str, js_str = '', ''
        if not js_only:
            html_str = render_template('html.jinja', chart=chart)
        
        if not html_only:
            js_str = render_template('js.jinja', chart=chart, use_htmx=use_htmx)

        return Markup('\n'.join([html_str, js_str]))

