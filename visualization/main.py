from flask import Flask, render_template, request, url_for, redirect

from visualization import chartjs as chjs

app = Flask(__name__)


@app.route('/')
def index():
    _all = chjs.Chart.retrieve_all()
    return render_template('index.html', charts=list(_all))


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
        machine_id = request.form.get('machine_id')
        label = request.form.get('label')
        title = request.form.get('title')
        if chart_type == chjs.chart_type.Line:
            x_param = request.form.get('x')
            y_param = request.form.get('y')
            ds = chjs.DataSource(
                chart_type=chart_type, x_param=x_param, y_param=y_param)
            ch = chjs.Chart(chart_type=chart_type, data_source=ds,
                            machine_id=machine_id, label=label, title=title)
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
