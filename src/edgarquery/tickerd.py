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
        self.mfturl     = 'https://www.sec.gov/files/company_tickers_mf.json'
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')

        self.tickd = {}
        self.mftickd = {}

        self.uq = ebquery._EBURLQuery()


    def tickers(self):
        resp = self.uq.query(self.turl, self.hdr)
        rstr = resp.read().decode('utf-8')
        jd = json.loads(rstr)
        keys =['cik_str', 'ticker', 'title']
        for k in jd.keys():
            # CIK as key
            cik = '%d' % jd[k]['cik_str']
            self.tickd[cik] = {}
            self.tickd[cik][keys[0]] = cik
            self.tickd[cik][keys[1]] = jd[k][keys[1]]
            self.tickd[cik][keys[2]] = jd[k][keys[2]]
            # ticker as key
            tkr = jd[k]['ticker']
            self.tickd[tkr] = {}
            self.tickd[tkr][keys[0]] = cik
            self.tickd[tkr][keys[1]] = jd[k][keys[1]]
            self.tickd[tkr][keys[2]] = jd[k][keys[2]]

    def mftickers(self):
        resp = self.uq.query(self.mfturl, self.hdr)
        rstr = resp.read().decode('utf-8')
        jd = json.loads(rstr)

        keys = ['cik', 'seriesId', 'classId', 'symbol']
        for row in jd['data']:
            cik = '%d' % row[0]
            self.mftickd[cik]={}
            self.mftickd[cik][keys[0]] = cik
            self.mftickd[cik][keys[1]] = row[1]
            self.mftickd[cik][keys[2]] = row[2]
            self.mftickd[cik][keys[3]] = row[3]
            sym = row[3]
            self.mftickd[sym]={}
            self.mftickd[sym][keys[0]] = cik
            self.mftickd[sym][keys[1]] = row[1]
            self.mftickd[sym][keys[2]] = row[2]
            self.mftickd[sym][keys[3]] = row[3]

    def getrecforticker(self, ticker):
        if not self.tickd.keys():
            self.tickers()
            self.mftickers()
        if ticker in self.tickd.keys():
            return self.tickd[ticker]
        if ticker in self.mftickd.keys():
            return self.mftickd[ticker]
        return None

    def getrecforcik(self, cik):
        if not self.tickd.keys():
            self.tickers()
            self.mftickers()
        if cik in self.tickd.keys():
            return self.tickd[cik]
        if cik in self.mftickd.keys():
            return self.mftickd[cik]
        return None

    def getcikforticker(self, ticker):
        if not self.tickd.keys():
            self.tickers()
            self.mftickers()
        ticker = ticker.upper()
        if ticker in self.tickd.keys():
            return self.tickd[ticker]['cik_str']
        if ticker in self.mftickd.keys():
            return self.mftickd[ticker]['cik']
        return None

    def gettickerforcik(self, cik):
        if not self.tickd.keys():
            self.tickers()
            self.mftickers()
        if cik in self.tickd.keys():
            return self.tickd[cik]['ticker']
        if cik in self.mftickd.keys():
            return self.tickd[cik]['symbol']
        return None


