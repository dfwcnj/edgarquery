#! env python

import os
import sys
import argparse
import csv
import json
import re
import urllib.request
import webbrowser

try:
    from edgarquery import ebquery
except ImportError as e:
    import ebquery

class TickerD():

    def __init__(self):
        self.turl     = 'https://www.sec.gov/files/company_tickers.json'
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')

        self.tickd = {}

        self.uq = ebquery._EBURLQuery()


    def tickers(self):
        resp = self.uq.query(self.turl, self.hdr)
        rstr = resp.read().decode('utf-8')
        jd = json.loads(rstr)
        for k in jd.keys():
            # CIK as key
            ck = jd[k]['cik_str']
            self.tickd[ck] = jd[k]
            # ticker as key
            tkr = jd[k]['ticker']
            self.tickd[tkr] = jd[k]

    def getrecforcik(self, cik):
        if not self.tickd.keys():
            self.tickers()
        if cik not in self.tickd.keys():
            return None
        return self.tickd[cik]

    def getcikforticker(self, ticker):
        if not self.tickd.keys():
            self.tickers()
        ticker = ticker.upper()
        if ticker not in self.tickd.keys():
            return None
        cik = self.tickd[ticker]['cik_str']
        return '%d' % (cik)

    def gettickerforcik(self, cik):
        if not self.tickd.keys():
            self.tickers()
        if cik not in self.tickd.keys():
            return None
        ticker = self.tickd[cik]['ticker']
        return ticker
