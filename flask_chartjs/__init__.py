from typing import Optional, Callable

from flask import Markup, render_template_string, Flask


class ChartJS:

    app: Optional[Flask]
    congfig: Optional[dict]
    _nonce_callback: Optional[Callable[..., str]] = None

    def __init__(self, app: Optional[Flask] = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.app = app

        @app.context_processor
        def inject_variables() -> dict:
            return dict(load_chartjs=self.__load_chartjs)

    @property
    def nonce_callback(self) -> Callable[..., str]:
        return self._nonce_callback

    def nonce_loader(self, callback: Callable[..., str]) -> Callable[..., str]:
        """This sets the callback for loading the current nonce str, needed in case of CSP.

        Args:
            callback (Callable[..., str]): _description_

        Returns:
            Callable[..., str]: _description_
        """
        self._nonce_callback = callback
        return self._nonce_callback

    def __load_chartjs(self) -> Markup:
        nonce_str = ''
        if self._nonce_callback is not None:
            nonce_str = f'nonce={self._nonce_callback()} '

        template_string = f'''<script {nonce_str}src="https://cdn.jsdelivr.net/npm/chart.js"></script>'''
        return Markup(render_template_string(template_string))
