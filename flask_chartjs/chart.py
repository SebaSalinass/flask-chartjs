from typing import Literal, Optional, Union, Any, List, Dict
from dataclasses import dataclass, field

from flask import Markup, render_template_string
import json


@dataclass
class DataSet:

    label: Optional[str] = None
    clip: Optional[Union[int, dict]] = None
    type: Optional[str] = None
    order: Optional[int] = None
    stack: Optional[str] = None
    parsing: Optional[Union[bool, dict]] = None
    hidden: bool = False
    data: List[Any] = field(default_factory=list)
    options: dict = field(default_factory=dict)
    background_color: Optional[str] = None

    def add_row(self, value: Any) -> None:
        self.data.append(value)

    def as_dict(self) -> Dict[str, Any]:
        data = {
            'data': self.data
        }
        if self.label:
            data['label'] = self.label
        if self.hidden:
            data['hidden'] = True
        if self.options:
            data['options'] = self.options
        if self.type:
            data['type'] = self.type
        if self.background_color:
            data['backgroundColor'] = self.background_color

        return data


@dataclass
class ChartData:

    datasets: List[DataSet] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)

    def add_labels(self, *labels: str) -> None:
        for label in labels:
            if not isinstance(label, str):
                raise TypeError('label/s must be str type')
            self.labels.append(str(label))

    def add_dataset(self, dataset: DataSet) -> None:
        self.datasets.append(dataset)

    def as_dict(self) -> Dict[str, Any]:
        return {
            'labels': self.labels,
            'datasets': [dataset.as_dict() for dataset in self.datasets]
        }


@dataclass
class Chart:

    id: str
    type: Literal['area', 'bar', 'bubble', 'doughnut', 'line']
    fallback: Optional[str] = None
    data: ChartData = field(default_factory=ChartData)
    plugins: List = field(default_factory=list, init=False)
    options: Dict[str, Any] = field(default_factory=dict)

    __tick_callbacks: Dict[str, str] = field(default_factory=dict, init=False)

    def __call__(self, title: Optional[Dict] = None,
                 padding: Optional[Union[int, Dict]] = None,
                 axis_title: Optional[Dict] = None,
                 axis_tick_callback: Optional[Dict] = None) -> str:
        """Renders a markup safe version of this chart.

        Args:
            title (Optional[Dict], optional): In template option to set `Chart title`, accepts a dict with the same arguments as `set_title`. Defaults to None.
            padding (Optional[Dict], optional): In template option to set `Chart padding`, accepts a dict with the same arguments as `set_padding`. Defaults to None.
            axis_title (Optional[Dict], optional): In template option to set `Axis title`, accepts a dict with the same arguments as `set_axis_title`. Defaults to None.
            axis_tick_callback (Optional[Dict], optional): In template option to set `Axis tick callback`, accepts a dict with the same arguments as `set_title`. Defaults to None.

        Returns:
            str: An HTML safe string representing this chart.
        """
        if title:
            self.set_title(**title)
        if padding:
            self.set_padding(**padding)
        if axis_title:
            self.set_axis_title(**axis_title)
        if axis_tick_callback:
            for axis, callback in axis_tick_callback.items():
                self.set_axis_tick_callback(axis, callback)

        return Markup(render_template_string(self.chart_template_string(), chart=self))

    def set_title(self, text: str, padding: Optional[Union[int, Dict[Literal['left', 'top', 'right', 'bottom'], int]]] = None) -> None:
        """Sets the chart title.

        Args:
            title (str): Chart title.
            padding (Optional[Union[int, Dict[Literal[&#39;left&#39;, &#39;top&#39;, &#39;right&#39;, &#39;bottom&#39;], int]]], optional): Title padding. Defaults to None.
        """
        plugins = self.options.setdefault('plugins', dict(
            title=dict(
                display=True,
                text=text)))

        if padding:
            plugins['title']['padding'] = padding

    def set_axis_title(self, axis: Literal['x', 'y'], text: str, align: Literal['start', 'center', 'end'] = 'center',
                       weight: Optional[str] = None, size: int = 12) -> None:
        """Sets title for given axis. could customize alignment and font weight and size.

        Args:
            axis (Literal[&#39;x&#39;, &#39;y&#39;]): The axis
            title (str): The title
            align (Literal[&#39;start&#39;, &#39;center&#39;, &#39;end&#39;], optional): Alignment options. Defaults to 'center'.
            weight (Optional[str], optional): Font Weight. Defaults to None.
            size (int, optional): Font size. Defaults to 12.
        """
        scales = self.options.setdefault('scales', dict())
        scales[axis] = dict(title=dict(
            display=True,
            text=text.capitalize(),
            align=align,
            font=dict(
                weight=weight,
                size=size
            )
        )
        )

    def set_padding(self, padding: Union[int, Dict[Literal['left', 'top', 'right', 'bottom'], int]]) -> None:
        """Set chart canvas padding.

        Args:
            padding (Union[int, Dict[Literal[&#39;left&#39;, &#39;top&#39;, &#39;right&#39;, &#39;bottom&#39;], int]]): The padding amount or padding dict object.
        """
        layout = self.options.setdefault('layout', dict())
        layout['padding'] = padding

    def set_axis_tick_callback(self, axis: Literal['x', 'y'], js_callback: str) -> None:
        """Sets a tick callback for the given axys. Must be a Literal string JavasScript Function or name of a function returnning a string.

        Args:
            axis (Literal[&#39;x&#39;, &#39;y&#39;]): The axis.
            js_callback (str): The function for the callback.
        """
        TOKEN = f'{axis.upper()}_CALLBACK_TOKEN'
        self.__tick_callbacks[TOKEN] = js_callback

        scales = self.options.setdefault('scales', dict())
        axis_dict = scales.setdefault(axis, dict())
        ticks = axis_dict.setdefault('ticks', dict())
        ticks.setdefault('callback', TOKEN)

    def as_dict(self) -> Dict[str, Any]:

        data_dict = {
            'type': self.type,
            'data': self.data.as_dict(),
        }

        if self.plugins:
            data_dict['plugins'] = self.plugins
        if self.options:
            data_dict['options'] = self.options

        return data_dict

    def to_json(self) -> str:
        return_str = json.dumps(self.as_dict())

        for token, js_callback in self.__tick_callbacks.items():
            return_str = return_str.replace(f'"{token}"', Markup(js_callback))

        return return_str

    def chart_template_string(self) -> str:
        return '''
            {% set const_name = 'canvas_' + chart.id|replace('-', '_') %}
            <canvas id="{{ chart.id }}">
                <p>{{ chart.fallback or chart.type + ' ' + chart.id }}</p>
            </canvas>
            <script {% if csp_nonce %} nonce={{ csp_nonce() }} {% endif %}>
            {% if htmx %}
                var {{ const_name }} = htmx.find("#{{ chart.id }}")
            {% else %}
                var {{ const_name }} = document.querySelector("#{{ chart.id }}")
            {% endif %}
                new Chart({{ const_name }},
                    {{ chart.to_json() | safe }}
                    );
            </script>
            '''
