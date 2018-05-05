import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import urllib
import datetime
import time

matplotlib.use('Agg')


def fix_dates(csv, interval_s):
    """
    returns a list of dates in legible format and not unix time stamp
    csv -> first index of all items in csv list is date
    interval_s -> intervals to get data in (seconds)
    """
    unix_date = 0
    ret_date = []
    for byte in csv:
        temp_str = str(byte, 'utf-8')
        temp_date = temp_str.split(',')[0]

        # if date is unix then get unix
        if temp_date[0] == 'a':
            unix_date = int(temp_date[1:])
            date = unix_date
        # else add the time interval seconds to the stamp
        else:
            date = unix_date + (interval_s * int(temp_date))

        # adding the date to the list
        ret_date.append(date)

    ret_date = [datetime.datetime.fromtimestamp(x) for x in ret_date]

    return ret_date


def csv_ret(symbol, interval_s, days):
    """
    returns clean csv for the symbol and time specified
    """
    if interval_s < 60:
        interval_s = 60

    if days != 1:
        days = 5

    # getting the data
    symbol = symbol.upper()
    url = "http://finance.google.com/finance/getprices?q={0}".format(symbol)
    url += "&i={0}&p={1}d&f=d,o,h,l,c,v".format(interval_s, days)
    csv = urllib.request.urlopen(url).readlines()

    # removing title headers and adding it to dataframe
    csv = csv[7:]

    return csv


def find_data_days(symbol, interval_s, days):
    """
    finding data of the symbol for the days specified [1-10 days at most]
    symbol -> stock symbol
    interval_s -> intervals to get data in (seconds)
    days -> how many days past data to collect
    """

    csv = csv_ret(symbol, interval_s, days)

    # fixing dates
    dates = fix_dates(csv, interval_s)

    # list of unique dates
    u_dates = [dates[0].date()]
    for i in range(1, len(dates)):
        if dates[i].date() != dates[i-1].date():
            u_dates.append(dates[i].date())

    # adding data to data list without dates
    data = []
    for byte in csv:
        temp_str = str(byte, 'utf-8')
        temp_lst = temp_str.split(',')
        temp_lst[-1] = temp_lst[-1][:-1]
        temp_lst = temp_lst[1:]

        data.append(temp_lst)

    # making data frame with data
    data_df = pd.DataFrame(columns=['CLOSE', 'HIGH', 'LOW', 'OPEN', 'VOLUME'])
    for i in range(len(data)):
        data_df.loc[i] = data[i]

    # adding indices as dates
    data_df['TIME'] = dates
    data_df['DATE'] = [datetime.datetime.date(data_df.loc[x, 'TIME'])
                       for x in range(len(dates))]

    # making close values floats
    data_df.loc[:, 'CLOSE'] = np.float64(data_df.loc[:, 'CLOSE'])

    # plotting graph
    plt.style.use('dark_background')
    fig = plt.figure()
    if days == 1:
        ax = plt.axes()
        title = symbol + " One Day Summary"
        ax.plot_date(data_df.TIME, data_df.CLOSE,
                         color="#FFBF00", linewidth=1, fmt='-')
        ax.set_xlabel(dates[0].strftime("%b %d"))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation = 45)
        plt.ylabel('Price')
        plt.title(title)
    else:
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1, 5, sharey=True)

        # new dataframe for each date
        five_df = [pd.DataFrame, pd.DataFrame,
                   pd.DataFrame, pd.DataFrame, pd.DataFrame]
        for i in range(5):
            five_df[i] = data_df[data_df['DATE'] == u_dates[i]]
            # plotting on axis
        sent = 0
        for ax in [ax1, ax2, ax3, ax4, ax5]:
            ax.plot_date(five_df[sent].TIME, five_df[sent].CLOSE,
                         color="#FFBF00", linewidth=1, fmt='-')
            ax.set_xlabel(u_dates[sent].strftime("%b %d"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
            sent += 1
        ax1.set_ylabel('Price')
        title = symbol + " Five Day Summary"
        plt.suptitle(title)

    filename = str(symbol.lower()) + str(days) + 'd' + str(int(time.time())) \
        + '.png'

    fig.savefig('ticker/static/pics/'+filename, bbox_inches='tight', dpi=300)

    return filename


def date_url(date):
    """
    returns date appropriate for google finance link
    date -> date in datetime format
    """

    if str(date.strftime('%b')) in ['Apr', 'May', 'Jun', 'Jul']:
        return date.strftime('%B')
    else:
        return date.strftime('%b')


def find_data_mny(symbol, months):
    """
    finding data of the symbol for the months/years
    symbol -> stock symbol
    months -> months from this day
    """
    symbol = symbol.upper()

    # finding range of dates to get data between
    today = datetime.date.today()
    end = today
    start = today - datetime.timedelta(months * 365/12)

    # making end and start date to put in url
    start_s = date_url(start) + '%20' + str(int(end.strftime('%d'))) \
                + ',%20' + start.strftime('%Y')
    end_s = date_url(end) + '%20' + str(int(end.strftime('%d'))) \
                 + ',%20' + end.strftime('%Y')

    # finding data from google finance
    url = "http://finance.google.com/finance/historical?q={0}".format(symbol)
    url += "&startdate={0}&enddate={1}&output=csv".format(start_s, end_s)
    print(url)
    user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
    csv = urllib.request.urlopen(url).readlines()
    csv = csv[::-1]
    csv = csv[:-1]

    # list of data from csv
    data = []
    for byte in csv:
        temp_str = str(byte, 'utf-8')
        temp_lst = temp_str.split(',')

        data.append(temp_lst)

    # dataframe for the data
    data_df = pd.DataFrame(columns=['DATE', 'OPEN', 'HIGH',
                                    'LOW', 'CLOSE', 'VOLUME'])
    for i in range(len(data)):
        data_df.loc[i] = data[i]

    data_df.loc[:, 'CLOSE'] = np.float64(data_df.loc[:, 'CLOSE'])

    # getting dates to be dates
    for i in range(len(data_df)):
        data_df.loc[i, 'DATE'] = datetime.datetime.strptime(
            data_df.loc[i, 'DATE'],
            '%d-%b-%y').date()

    date_map = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four',
                5: 'Five', 6: 'Six', 7: 'Seven', 8: 'Eight',
                9: 'Nine'}

    period = ''
    # what to put in plot title
    if months < 10: # less than 10
        period = date_map[months] + " Month"
    elif months % 12 == 0: # if an actual year
        years = months / 12
        if years < 10:
            period = date_map[years] + " Year"
        else:
            period = str(int(years)) + " Year"
    else:
        period = str(months) + " Month"

    # plotting graph
    plt.style.use('dark_background')
    fig = plt.figure()
    ax = plt.axes()
    title = symbol + " " + period + " Summary"
    ax.plot_date(data_df.DATE, data_df.CLOSE,
                         color="#FFBF00", linewidth=1, fmt='-')
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d '%y"))
    plt.xticks(rotation = 45)
    plt.ylabel('Price')
    plt.title(title)

    filename = str(symbol.lower()) + str(months) + 'm' + str(int(time.time())) \
        + '.png'
    fig.savefig('ticker/static/pics/'+filename, bbox_inches='tight', dpi=300)

    return filename


def data_plot(symbol, tyme, dmy):
    """
    decides what type of plot to build
    """
    if dmy.upper() == 'M':
        return find_data_mny(str(symbol), int(tyme))
    elif dmy.upper() == 'Y':
        return find_data_mny(str(symbol), int(tyme) * 12)
    elif dmy.upper() == 'D':
        return find_data_days(str(symbol), 60, int(tyme))
