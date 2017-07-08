from ticker import app
from flask import render_template, request
from . import plotticker
import os
from googlefinance import getQuotes
import json
import urllib

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        symbol = request.form['symbol']
        symbol = symbol.upper()

        try:
            a = json.dumps(getQuotes(symbol))
        except urllib.error.HTTPError:
            return render_template('index.html', error='Invalid Symbol')

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

        filelist = [f for f in os.listdir("ticker/static/pics")
                    if f.endswith(".jpg")]
        for f in filelist:
            os.remove("ticker/static/pics/"+f)

        plotticker.data_plot(symbol, time, dmy)
        image = str(symbol.lower()) + str(time) + str(dmy.lower()) + '.jpg'

        return render_template('index.html', symbol=symbol.upper(), time=time_s
                               ,reset=1, image=image)


    return render_template('index.html')
