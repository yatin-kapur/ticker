from ticker import app
from flask import render_template, request, redirect
from . import plotticker

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        symbol = request.form['symbol']

        day_dict={'1D': 1, '5D': 5}
        mny_dict={'1M': 1, '3M': 3, '1Y': 12, '5Y': 60, '10Y': 120}

        time_s = ''
        time = 0

        actual = list(request.form.keys())[1]

        if request.form[actual] in ['1D', '5D']:
            time = day_dict[request.form[actual]]
            time_s = str(time) + ' Day(s)'
            dmy = 'D'
        else:
            time = mny_dict[request.form[actual]]
            dmy = 'M'
            if time > 11:
                time_s = str(int(time/12)) + ' Year(s)'
            else:
                time_s = str(time) + ' Month(s)'

        plotticker.data_plot(symbol, time, dmy)

        image = 'graph.jpg'

        return render_template('index.html', symbol=symbol.upper(), time=time_s
                               ,reset=1, image=image)

    return render_template('index.html')
