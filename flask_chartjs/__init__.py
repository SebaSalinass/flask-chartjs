from typing import Optional, Callable, Dict, Any

from flask import Flask, Blueprint, Markup, render_template
from .chart import Chart, DataSet


__all__ = ('ChartJSManager', 'Chart', 'DataSet')


class ChartJSManager:

    app: Optional[Flask]
    local_path: Optional[str] = None
    config: Optional[dict] = None
    _nonce_callback: Optional[Callable[[], str]] = None

    def __init__(self, app: Optional[Flask] = None) -> None:

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.app = app
        self.local_path = app.config.get('CHARTJS_LOCAL_PATH')
        blueprint = Blueprint('chartjs', __name__, template_folder='templates',
                              static_folder='static', static_url_path='/chartjs' + app.static_url_path)
        self.app.register_blueprint(blueprint)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['chartjs'] = self

        @app.context_processor
        def inject_context_variables() -> dict:
            return dict(chartjs=self)

    def load(self) -> Markup:
        return Markup(render_template('load_chartjs.jinja', local_path=self.local_path))

    def render(self, chart: Chart, options: Dict[str, Any] = None, plugins: Dict[str, Any] = None,
               datasets: Dict[str, Any] = None, html_only: bool = False, js_only: bool = False) -> Markup:
        
        chart_data = chart.as_dict()

        if datasets:
            for key, val in datasets.items():
                chart_data['data']['datasets'][key].update(val)
        
        if options:
            chart_data.update(options=options)
        if plugins:
            chart_data.update(plugins=plugins)

        html_str, js_str = '', ''
        if not js_only:
            html_str = render_template('html.jinja', chart=chart)

        if not html_only:
            js_str = render_template('js.jinja', chart=chart, chart_data=chart_data)
            
        return Markup('\n'.join([html_str, js_str]))
