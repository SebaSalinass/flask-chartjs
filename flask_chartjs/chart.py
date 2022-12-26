import json

from typing import Literal, Optional, Union, Any, Dict
from dataclasses import dataclass, field


PaddingType = Union[int, Dict[Literal['left', 'top', 'right', 'bottom'], int]]
AxisType = Literal['x', 'y']
ChartType = Literal['area', 'bar', 'bubble', 'doughnut',
                    'pie', 'line', 'polarArea', 'radar', 'scatter']
AlignmentType = Literal['center', 'left', 'right']


@dataclass
class DataSet:

    label: Optional[str] = None
    clip: Optional[Union[int, dict]] = None
    type: Optional[str] = None
    order: Optional[int] = None
    stack: Optional[str] = None
    parsing: Optional[Union[bool, dict]] = None
    hidden: bool = False
    data: list[Any] = field(default_factory=list)
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

    datasets: list[DataSet] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)

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
    type: ChartType
    data: ChartData = field(default_factory=ChartData)
    plugins: list = field(default_factory=list)
    options: dict = field(default_factory=dict)

    _ticks_callbacks: Dict[str, str] = field(default_factory=dict, init=False)
    _title: str = None

    def set_title(self, text: str, padding: PaddingType = None) -> None:
        """Gives te chart a title.

        :param text: The title to be set on the chart.
        :type text: str
        :param padding: The title padding an integer or {'left': 10} dict, defaults to None
        :type padding: Union[int, Dict[str, int]], optional
        """
        plugins = self.options.setdefault('plugins', dict())
        title = plugins.setdefault('title', dict(display=True, text=text))
        self._title = text

        if padding:
            title['padding'] = padding

    def set_axis_tick_callback(self, axis: AxisType, callback: str) -> None:
        TOKEN = f'{axis}_tick_callback'
        self._ticks_callbacks[TOKEN] = callback

        scales = self.options.setdefault('scales', dict())
        axis = scales.setdefault(axis, dict())
        axis['ticks'] = dict(callback=TOKEN)

    def set_axis_title(self, axis: AxisType,  text: str, align: AlignmentType = 'center',
                       weight: str = None, size: int = 12) -> None:

        scales = self.options.setdefault('scales', dict())
        axis = scales.setdefault(axis, dict())
        axis['title'] = dict(
            display=True,
            text=text,
            align=align,
            font=dict(weight=weight, size=size)
        )

    def set_padding(self, padding: PaddingType) -> None:
        layout = self.options.setdefault('layout', dict())
        layout['padding'] = padding

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
        return_str = json.dumps(self.as_dict(), indent=4)
        for token, value in self._ticks_callbacks:
            return_str.replace(f'\"{token}\"', value)

        return return_str
