import json
import uuid
from collections import namedtuple

import jinja2

from db import get_cursor
from utils import get_random_color, get_random_chars

env = jinja2.Environment(
    loader=jinja2.PackageLoader('visualization', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

__ChartType = namedtuple('ChartType', ['Line', 'Bar', 'Doughnut'])
chart_type = __ChartType(Line='line', Bar='bar', Doughnut='doughnut')
all_params = ['Spindel', 'Feed', 'M30', 'Time']


class ChartRenderer:
    @staticmethod
    def template():
        raise NotImplementedError()

    def context(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()


class TimeLineChartRenderer(ChartRenderer):
    def __init__(self, xy_data, title, label, line_color=None,
                 point_color=None, fill=False,
                 width=None, height=None):
        """
        :param xy_data: Callable object that returns tuple of two elements.
            Firs element -- iterable that contains X axis data.
            Second element -- iterable that contains Y axis data.
            Elements must be the same length
        :param title: Chart title
        :param label: Label of the Y axis
        :param line_color: Color of the line
        :param point_color: Color of the points on the line
        :param fill: if True than area under the line will be filled
            or not if taken False.
        :param width: width of the html canvas where chart is situated
        :param height: width of the html canvas where chart is situated
        """
        assert (callable(xy_data))
        self.xy_data = xy_data
        self.id = uuid.uuid4()
        self.title = title
        self.label = label
        self.line_color = line_color or get_random_color()
        self.point_color = point_color or get_random_color()
        self.axis_id = get_random_chars()
        self.fill = fill
        self.width = width or 60
        self.height = height or 30

    def render(self):
        tmp = self.template()
        context = self.context()
        return tmp.render(context=context)

    def context(self):
        x_data, y_data = self.xy_data()
        x_data, y_data = list(x_data), list(y_data)
        return {
            'width': self.width,
            'height': self.height,
            'chartId': self.id,
            'chartName': self.title,
            'xAxisData': x_data,
            'yAxisData': json.dumps(
                {
                    'label': self.label,
                    'lineColor': self.line_color,
                    'pointColor': self.point_color,
                    'axisId': self.axis_id,
                    'fill': self.fill,
                    'data': y_data
                }
            )
        }

    @staticmethod
    def template():
        template = env.get_template('_charts/timeline-chart.html')
        return template


class DataSource:
    def __init__(self, chart_type: str, **params):
        self.chart_type = chart_type
        self.params = params

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class Chart:
    def __init__(self, chart_type: str, data_source: DataSource = None):
        self.chart_type = chart_type
        self.data_source = data_source
        self.machine_id = None
        self.title = None
        self.chart_params = {}

    def get_chart_params(self):
        return json.dumps(self.chart_params)

    def save(self):
        conn, curr = get_cursor()
        curr.execute("""
        insert into chart(machine_id, title, chart_type, chart_params) 
        values(?, ?, ?, ?)
        """, [self.machine_id, self.title,
              self.chart_type, self.get_chart_params()])
        conn.commit()

    def retrieve(self, chart_id):
        raise NotImplementedError()

    def retrieve_all(self):
        raise NotImplementedError()
