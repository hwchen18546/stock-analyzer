import urllib
import csv
import datetime
import numpy as np
import matplotlib.finance as finance
import matplotlib.mlab as mlab

class YAHOO:
    def get_realtime_data(self, ticker, raw):
        url_string = "http://finance.yahoo.com/d/quotes.csv?s=%s&f=d1ohgl1vl1" %(ticker)
        data = urllib.urlopen(url_string).readlines()
        for now in csv.reader(data):
            now[0] = datetime.datetime.strptime(now[0], "%m/%d/%Y").date()
        if now[0] == raw[-1].date:
            return raw

        raw[:-1] = raw[1:]
        raw[-1].date, raw[-1].open = now[0], now[1]
        raw[-1].high, raw[-1].low = now[2], now[3]
        raw[-1].close, raw[-1].volume = now[4], now[5]
        raw[-1].adj_close = now[6]
        return raw 
    def get_history_data(self, ticker, start, end):
        try:
            fh = finance.fetch_historical_yahoo(ticker, start, end)
            # a numpy record array with fields: date, open, high, low, close, volume, adj_close)
            raw = mlab.csv2rec(fh)
            fh.close()
            raw.sort()
            # get today data
            if end == datetime.date.today():
                raw = self.get_realtime_data(ticker, raw)
        except:
            return 0
        return raw 

    def get_ticker_name(self, ticker):
        url_string = "http://finance.yahoo.com/d/quotes.csv?s=%s&f=n" %(ticker)
        data = urllib.urlopen(url_string).readlines()
        for name in csv.reader(data):
            return name[0]
