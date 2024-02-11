#! /usr/bin/env python

#
# EDGARTickerstoCSV
#

import os
import sys
import json
import argparse
import urllib.request

class EDGARTickerstoCSV():

    def __init__(self, odir=None):
        """ EDGARTickerstoCSV

        retrieve the three ticker json files,
        parse them, and combine them into a single csv file
        """
        if odir: self.odir = odir
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.odir = os.path.abspath(self.odir)
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')
        self.turla = [
            'https://www.sec.gov/files/company_tickers.json',
            'https://www.sec.gov/files/company_tickers_exchange.json',
            'https://www.sec.gov/files/company_tickers_mf.json'
        ]

    def query(self, url=None):
        """query - retrieve a url

        url  - url to retrieve
        """
        try:
            req = urllib.request.Request(url, headers=self.hdr)
            resp = urllib.request.urlopen(req)
            return resp
        except urllib.error.URLError as e:
            print("Error %s(%s): %s" % ('query', url, e.reason),
            file=sys.stderr )
            sys.exit(1)

    def getjson(self, url):
        """getjson(url)

        retrieve a csv file and load it into a python json object
        url - url to a json object
        """
        resp = self.query(url)
        js   = json.loads(resp.read())
        return js

    def putcsv(self, js, ofp):
        """ putcsv(js, ofp)

        convert the json to csv and write to a csv file
        js - ticker json to convert
        ofp - file pointer to write to
        """
        keys = js.keys()

        if 'data' in js.keys():
            dta=js['data']
            for i in range(len(dta) ):
                print("'%s','%s','%s','%s'" % (dta[i][0], dta[i][1],
                                               dta[i][2], dta[i][3]), file=ofp )
        else:
            ha=[]
            for i in keys:
                if len(ha)==0:
                     for k in js[i].keys():
                         ha.append("'%s'," % k)
                     print(''.join(ha), file=ofp)
                ra = []
                for k in js[i].keys():
                    ra.append("'%s'," % (js[i][k]) )
                print(''.join(ra), file=ofp)
                #print("'%s','%s','%s'" % (js[k]['cik_str'], js[k]['ticker'],
                #                             js[k]['title']), file=ofp)

    def urljstocsv(self, odir):
        """ urljstocsv()

        retrieve the SEC FRED ticker urls and write their contents
        to csv files
        """
        if not odir: odir=self.odir
        for u in self.turla:
            if '_exchange' in u:
                hdr="'cik','title','ticker','exchange'"
                ofn = os.path.join(odir, 'tickers_exchange.csv')
            elif '_mf' in u:
                hdr="'cik','seriesId','classId','symbol'"
                ofn = os.path.join(odir, 'tickers_mf.csv')
            else:
                hdr="'cik','ticker','title'"
                ofn = os.path.join(odir, 'tickers.csv')
            with open(ofn, 'w') as ofp:
                print(hdr, file=ofp)
                #print(hdr, file=sys.stdout)
                js = self.getjson(u)
                self.putcsv(js, ofp)
                #self.putcsv(js, sys.stdout)


if __name__ == '__main__':
    def main():

        argp = argparse.ArgumentParser(description="collect EDGAR\
        companyticker json files and convert them to csv")

        argp.add_argument('--odir', default='/tmp/',
                       help="where to deposit the fileѕ")

        args = argp.parse_args()

        tc = EDGARTickerstoCSV()

        tc.urljstocsv(odir=args.odir)

main()
