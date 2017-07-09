import urllib

def check(symbol):
    """
    function validates the symbol, if it's not a valid symbol then it returns
    an error
    symbol -> symbol to validate
    """

    # getting the data
    symbol = symbol.upper()
    url = "http://www.google.com/finance/getprices?q={0}".format(symbol)
    url += "&i=300&p=500d&f=d,o,h,l,c,v"
    csv = urllib.request.urlopen(url).readlines()

    if len(csv) < 8:
        return "error"
    else:
        return "ok"

