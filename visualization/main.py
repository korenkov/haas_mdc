from flask import Flask, render_template

from db import get_cursor
from visualization import chartjs

app = Flask(__name__)


def select_param_data(from_date, to_date, param_code, machine_id):
    conn, c = get_cursor(db='data.db')
    for row in c.execute("""
    SELECT 
        log_date,
        param_val
    FROM params_data 
    WHERE (log_date BETWEEN ? and ?) and param_code = ? and machine_id = ?
    """, [from_date, to_date, param_code, machine_id]):
        yield row


def xy_data(param_code, machine_id, from_date=0, to_date=100000000000):
    return lambda: zip(
        *[r for r in select_param_data(from_date, to_date, param_code, machine_id)]
    )


@app.route('/')
def index():
    m30_chart = chartjs.TimeLineChart(
        xy_data(param_code='5701', machine_id='cnc_1'),
        'cnc_1', 'Tool life monitor counter'
    )
    feed_chart = chartjs.TimeLineChart(
        xy_data(param_code='3022', machine_id='cnc_1'),
        'cnc_1', 'Feed'
    )
    spindel_chart = chartjs.TimeLineChart(
        xy_data(param_code='1094', machine_id='cnc_2'),
        'cnc_2', 'Spindel'
    )
    charts = [
        m30_chart.render(),
        feed_chart.render(),
        spindel_chart.render(),
    ]
    return render_template('index.html', charts=charts)


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
