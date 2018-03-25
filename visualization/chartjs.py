import json
import uuid
import collections
import types

import jinja2

from db import get_cursor, select_param_with_time, select_single_param
from utils import get_random_color, get_random_chars

env = jinja2.Environment(
    loader=jinja2.PackageLoader('visualization', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

__ChartType = collections.namedtuple('ChartType', [
    'Line',
    # 'Bar',
    # 'Doughnut'
])
chart_type = __ChartType(
    Line='line',
    # Bar='bar',
    # Doughnut='doughnut'
)

_params_map = {
    'Spindel': '1094',
    'Feed': '3022',
    'M30': '3901',
    'Tool life': '5701',
    'Time': None
}

all_params = _params_map.keys()


def _select_single_param(param_name):
    return lambda machine_id: [
        r for r in select_single_param(
            from_date=0, to_date=100000000000,
            param_code=_params_map[param_name],
            machine_id=machine_id)
    ]


def _select_params_with_time(param_name):
    return lambda machine_id: zip(
        *[r for r in select_param_with_time(
            from_date=0, to_date=100000000000,
            param_code=_params_map[param_name],
            machine_id=machine_id)]
    )


_param_provider_map = {
    'by_time': {
        'Spindel': _select_params_with_time('Spindel'),
        'Feed': _select_params_with_time('Feed'),
        'M30': _select_params_with_time('M30'),
        'Tool life': _select_params_with_time('Tool life'),
    },
    'single': {
        'Spindel': _select_single_param('Spindel'),
        'Feed': _select_single_param('Feed'),
        'M30': _select_single_param('M30'),
        'Tool life': _select_single_param('Tool life'),
    }
}


class ChartRenderer:
    @staticmethod
    def template():
        raise NotImplementedError()

    def context(self):
        raise NotImplementedError()

    def render(self):
        raise NotImplementedError()


class TimeLineChartRenderer(ChartRenderer):
    def __init__(self, xy_data, machine_id, title, label, line_color=None,
                 point_color=None, fill=False,
                 width=None, height=None):
        """
        :param xy_data: Function or LambdaFunction object that
            returns tuple of two elements.
            Firs element -- iterable that contains X axis data.
            Second element -- iterable that contains Y axis data.
            Elements must be the same length
        :param machine_id: ID of the CNC machine
        :param title: Chart title
        :param label: Label of the Y axis
        :param line_color: Color of the line
        :param point_color: Color of the points on the line
        :param fill: if True than area under the line will be filled
            or not if taken False.
        :param width: width of the html canvas where chart is situated
        :param height: width of the html canvas where chart is situated
        """
        assert callable(xy_data)
        assert (isinstance(xy_data, types.FunctionType)
                or isinstance(xy_data, types.LambdaType))
        self.xy_data = xy_data
        self.machine_id = machine_id
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

        data = list(self.xy_data(self.machine_id))

        if data:
            x_data, y_data = data
        else:
            x_data, y_data = None, None

        if x_data and y_data:
            x_data, y_data = list(x_data), list(y_data)
        else:
            x_data, y_data = [], []

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

    def dumps(self):
        return json.dumps({
            'id': self.id.__str__(),
            'title': self.title,
            'label': self.label,
            'line_color': self.line_color,
            'point_color': self.point_color,
            'axis_id': self.axis_id,
            'fill': self.fill,
            'width': self.width,
            'height': self.height,
            'machine_id': self.machine_id,
        })


class DataSource:
    def __init__(self, chart_type: str, **params):
        self.chart_type = chart_type
        self.params = params

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def get_data_provider_rule(self):
        x_param = self.params.get('x_param')
        y_param = self.params.get('y_param')

        if self.chart_type == chart_type.Line:
            if 'Time' in [x_param, y_param]:
                return json.dumps({
                    'criteria': 'by_time',
                    'param': x_param if x_param != 'Time' else y_param
                })
        else:
            return json.dumps([
                {'criteria': 'single', 'param': x_param},
                {'criteria': 'single', 'param': y_param}
            ])


class Chart:
    renderer_class = TimeLineChartRenderer

    def __init__(self, chart_type: str, data_source: DataSource = None,
                 machine_id=None, title=None, label=None, **kw):
        self.chart_type = chart_type
        self.data_source = data_source
        self.machine_id = machine_id
        self.title = title
        self.label = label
        self.chart_params = kw

    def save(self):
        conn, curr = get_cursor()
        chart_renderer = self.renderer_class(
            xy_data=lambda : ([], []),
            machine_id=self.machine_id,
            title=self.title, label=self.label)
        chart_context = chart_renderer.dumps()
        data_provider_rule = self.data_source.get_data_provider_rule()
        curr.execute("""
        insert into chart(machine_id, chart_type, chart_params, data_provider) 
        values(?, ?, ?, ?)
        """, [self.machine_id, self.chart_type,
              chart_context, data_provider_rule])
        conn.commit()

    def retrieve(self, chart_id):
        raise NotImplementedError()

    @classmethod
    def retrieve_all(cls):
        conn, c = get_cursor()
        _sql = """
            SELECT 
                id,
                chart_type,
                chart_params,
                data_provider
            FROM chart 
            """
        for i, row in enumerate(c.execute(_sql)):
            chart_params = json.loads(row[-2])
            rule = json.loads(row[-1])
            if isinstance(rule, list) and len(rule) == 2:
                data_provider = lambda : (
                    _param_provider_map['single'][rule[0]['param']],
                    _param_provider_map['single'][rule[1]['param']]
                )
            elif isinstance(rule, dict):
                data_provider = _param_provider_map['by_time'][rule['param']]
            else:
                raise Exception('Unsupported structure')
            ch = cls.renderer_class(
                xy_data=data_provider,
                machine_id=chart_params['machine_id'],
                title=chart_params['title'],
                label=chart_params['label'],
                line_color=chart_params['line_color'],
                point_color=chart_params['point_color'],
                fill=chart_params['fill'],
                width=chart_params['width'],
                height=chart_params['height']
            )

            yield ch.render()
