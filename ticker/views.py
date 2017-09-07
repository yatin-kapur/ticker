from ticker import app
from flask import render_template, request
from . import plotticker, validate
import os
from threading import Thread
import time

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        symbol = request.form['symbol']
        symbol = symbol.upper()

        if validate.check(symbol) == "error":
            return render_template('index.html',
                                   error='Please Enter a Valid Symbol')

        day_dict={'1D': 1, '5D': 5}
        mny_dict={'1M': 1, '3M': 3, '1Y': 12, '5Y': 60, '10Y': 120}

        time_s = ''
        time_l = 0

        actual = list(request.form.keys())[1]

        if request.form[actual] in ['1D', '5D']:
            time_l = day_dict[request.form[actual]]
            time_s = str(time_l) + ' Day(s)'
            dmy = 'D'
        else:
            time_l = mny_dict[request.form[actual]]
            dmy = 'M'
            if time_l > 11:
                time_s = str(int(time_l/12)) + ' Year(s)'
            else:
                time_s = str(time_l) + ' Month(s)'

        image = plotticker.data_plot(symbol, time_l, dmy)
        delete_image = Thread(target=remove, args=(image,))
        delete_image.start()

        return render_template('index.html', symbol=symbol.upper(), time=time_s
                               ,reset=1, image=image)

    return render_template('index.html')

def remove(image):
    time.sleep(10)
    os.remove('ticker/static/pics/'+image)
