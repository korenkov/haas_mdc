import json
import random

from jinja2 import Template


class CrudMixin:
    @classmethod
    def insert(cls):
        raise NotImplemented()

    @classmethod
    def delete(cls):
        raise NotImplemented()

    @classmethod
    def update(cls):
        raise NotImplemented()

    @classmethod
    def select(cls):
        raise NotImplemented()


class Chart:
    def get_template(self):
        raise NotImplemented()

    def save(self):
        raise NotImplemented()

    def render(self):
        raise NotImplemented()


class LineChart(Chart):
    def __init__(self, chart_id, title):
        self.id = chart_id
        self.title = title
        self.x_data = [1, 2, 3, 4, 5, 6, 7]

    def render(self):
        tmp = self.template()
        context = self.context()
        return tmp.render(context=context)

    def context(self):
        return {
            'chartId': self.id,
            'chartName': self.title,
            'xAxisData': self.x_data,
            'yAxisDataArray': json.dumps([
                {
                    'label': 'Feed',
                    'lineColor': 'red',
                    'pointColor': 'red',
                    'axisId': 'y-axis-1',
                    'fill': False,
                    'data': [
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100
                    ]
                },
                {
                    'label': 'Spindel',
                    'lineColor': 'blue',
                    'pointColor': 'blue',
                    'axisId': 'y-axis-2',
                    'fill': False,
                    'data': [
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100,
                        random.randint(1, 99) * 100
                    ]
                }
            ])
        }

    @staticmethod
    def template():
        template_str = """
        <canvas id="{{ context.chartId }}" width="80" height="40"></canvas>
        <script>
            var ctx = document.getElementById({{ context.chartId }});

            var chartName = '{{ context.chartName }}';

            var xAxisData = {{ context.xAxisData }};

            var yAxisDataArray = {{ context.yAxisDataArray | safe }};

            var lineChartData = {
                labels: xAxisData,
                datasets: [
                    {
                        label: yAxisDataArray[0].label,
                        borderColor: yAxisDataArray[0].lineColor,
                        backgroundColor: yAxisDataArray[0].pointColor,
                        fill: yAxisDataArray[0].fill,
                        data: yAxisDataArray[0].data,
                        yAxisID: yAxisDataArray[0].axisId
                    },
                    {
                        label: yAxisDataArray[1].label,
                        borderColor: yAxisDataArray[1].lineColor,
                        backgroundColor: yAxisDataArray[1].pointColor,
                        fill: yAxisDataArray[1].fill,
                        data: yAxisDataArray[1].data,
                        yAxisID: yAxisDataArray[1].axisId
                    }
                ]
            };

            Chart.Line(ctx, {
                data: lineChartData,
                options: {
                    responsive: true,
                    hoverMode: 'index',
                    stacked: false,
                    title: {
                        display: true,
                        text: chartName
                    },
                    scales: {
                        yAxes: [
                            {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                id: yAxisDataArray[0].axisId
                            },
                            {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                id: yAxisDataArray[1].axisId
                            }
                        ]
                    }
                }
            });

        </script>
            """

        return Template(template_str)
