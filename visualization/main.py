from flask import Flask, render_template, request, url_for, redirect

from db import select_param_with_time
from visualization import chartjs as chjs

app = Flask(__name__)


def xy_data(param_code, machine_id, from_date=0, to_date=100000000000):
    return lambda: zip(
        *[r for r in select_param_with_time(from_date, to_date, param_code, machine_id)]
    )


@app.route('/')
def index():
    m30_chart = chjs.TimeLineChartRenderer(
        xy_data(param_code='5701', machine_id='cnc_1'),
        'cnc_1', 'Tool life monitor counter'
    )
    feed_chart = chjs.TimeLineChartRenderer(
        xy_data(param_code='3022', machine_id='cnc_1'),
        'cnc_1', 'Feed'
    )
    spindel_chart = chjs.TimeLineChartRenderer(
        xy_data(param_code='1094', machine_id='cnc_2'),
        'cnc_2', 'Spindel'
    )
    charts = [
        m30_chart.render(),
        feed_chart.render(),
        spindel_chart.render(),
    ]
    return render_template('index.html', charts=charts)


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'GET':
        return render_template(
            'new_chart.html',
            chart_type=chjs.chart_type,
            all_params=chjs.all_params
        )

    elif request.method == 'POST':
        print(request.form)
        chart_type = request.form.get('chart_type')
        if chart_type == chjs.chart_type.Line:
            x_param = request.form.get('x')
            y_param = request.form.get('y')
            ds = chjs.DataSource(
                chart_type=chart_type, x_param=x_param, y_param=y_param)
            ch = chjs.Chart(chart_type=chart_type, data_source=ds)
            ch.save()
        elif chart_type in (chjs.chart_type.Bar, chjs.chart_type.Doughnut):
            params = request.form.get('params')
            ds = chjs.DataSource(chart_type=chart_type, params=params)
            ch = chjs.Chart(chart_type=chart_type, data_source=ds)
            ch.save()
        else:
            raise Exception('Unsupported chart type')

        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
