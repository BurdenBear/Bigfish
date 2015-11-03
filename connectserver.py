# -*- coding: utf-8 -*-

from WindSocket import wind_server
from datetime import datetime
import time

if __name__ == '__main__':
    request = {}
    request['symbol'] = '000002.SZ'
    request['start_time'] = datetime(2015,9,30,9,00,00)
    request['end_time'] = datetime.fromtimestamp(int(time.time()))
    request['bar_type'] = 'd'
    try:
        print(wind_server.wind_client_fetch_historic_data(request))
    except Exception as e:
        pass
