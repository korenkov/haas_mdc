from flask import Flask, render_template

from chartjs import LineChart

app = Flask(__name__)


@app.route('/')
def index():
    charts = [
        LineChart(1, 'Title1').render(),
        LineChart(2, 'Title2').render(),
    ]
    return render_template('index.html', charts=charts)


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
