import os
import numpy as np
from datetime import datetime
import time
import datetime
from dateutil.relativedelta import relativedelta
from exceptions import NotAbleToConnectToSourceApi
from exceptions import ResponseFromCurrencyApiNotSuccessfull
from exceptions import NoAPIKeyPresent
from ah_requests import AhRequest
from logger import Logger
import json


CURRENCY_API_KEY = os.getenv('CURRENCY_API_KEY', None)
if not CURRENCY_API_KEY:
    raise NoAPIKeyPresent("Can't find 'CURRENCY_API_KEY' in the env variables", status_code=500) 
    

LOG = Logger()


def strToDate(strDate):
    date_format = "%Y-%m-%d"
    d = datetime.datetime.strptime(time.strftime(strDate), date_format).date()
    return d

def today(d=None):
    today = datetime.date.today()
    if d:
        datum = today + datetime.timedelta(days=d)
        return datum.strftime('%Y-%m-%d')
    else:
        return today.strftime('%Y-%m-%d')

def queryCurrencyApi(pair, date):
    url = "http://www.apilayer.net/api/historical?access_key={}&source={}&currencies={}&date={}".format(CURRENCY_API_KEY, pair[:3], pair[3:],date)
    #LOG.console(url)
    ah_request = AhRequest()
    res = ah_request.get(url=url)
    res = res.json()
    return float(res['quotes'][pair])
    
def rates(payload):
    ah_request = AhRequest()
    result = []
    for transaction in payload['transactions']:
        obj = dict()
        pair = transaction['currency_from']+transaction['currency_to']
        transaction_start_date = transaction['start']
        transaction_end_date = transaction['end']
        if transaction_end_date < today():
            end_date = transaction_end_date
        else:
            end_date = today()
        start_date = strToDate(end_date) - relativedelta(years=1)
        url = "http://www.apilayer.net/api/timeframe?start_date={0}&end_date={1}&access_key={4}&source={2}&currencies={3}".format(start_date, end_date, pair[:3], pair[3:], CURRENCY_API_KEY)
        res = ah_request.get(url=url)
        res = res.json()
        rates = []
        dates = list(res['quotes'])
        values = list(res['quotes'].values())
        for x in range(len(dates)):
            rates.append({'date':dates[x],'value':values[x][pair]})

        obj.update(rates=rates, pair=pair)
        obj.update(start_rate=queryCurrencyApi(pair=pair, date=transaction_start_date))
        obj.update(end_rate=queryCurrencyApi(pair=pair, date=end_date))

        result.append(obj)
    return result
