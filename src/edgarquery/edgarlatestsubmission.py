#! /usr/bin/env python

#
# EDGARLatestSubmission
#

import os
import sys
import argparse
import datetime
from functools import partial
import html
from html.parser import HTMLParser
import json
import re
import subprocess
import urllib.request
import webbrowser

try:
    from edgarquery import ebquery
    from edgarquery import edgarsubmissionspivot
    from edgarquery import tickerd
except ImportError as e:
    import ebquery
    import edgarsubmissionspivot
    import tickerd

class EDGARLatestSubmission():

    def __init__(self):
        """ EDGARLatestSubmission

        retrieve the latest SEC submission data for a company
        """
        self.sprefix = 'https://www.sec.gov/Archives/edgar/full-index'
        self.rprefix = 'https://www.sec.gov/Archives'
        self.fprefix = '%s/edgar/data/' % self.rprefix

        self.jsurl   = 'https://data.sec.gov/submissions/CIK%s.json'
        self.bprefix = 'https://www.sec.gov/edgar/browse/?CIK=$s'
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')
        self.now     = datetime.datetime.now()
        self.link    = True
        self.chunksize =4294967296
        self.uq = ebquery._EBURLQuery()
        self.td = tickerd.TickerD()
        self.sp = edgarsubmissionspivot.EDGARSubmissionsPivot()

    def getcikforticker(self, ticker):
        return self.td.getcikforticker(ticker)


    def searchlinks(self, url):
        resp = self.uq.query(url, self.hdr)
        if resp == None:
            return None
        ua = url.split('/')
        cik = ua[-1]
        rstr    = resp.read().decode('utf-8')
        class MyHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.urla = []
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    self.urla.append('%s%s' % ('https://www.sec.gov',
                                                attrs[0][1]))
            def handle_endtag(self, tag):
                pass
            def handle_data(self, data):
                pass
        parser = MyHTMLParser()
        parser.feed(rstr)
        urla = parser.urla
        return urla

    def getandparsejson(self, url):
        resp = self.uq.query(url, self.hdr)
        if resp == None:
            return None
        rstr    = resp.read().decode('utf-8')
        js = json.loads(rstr)
        hdr = [k for k in js['filings']['recent'].keys()]
        lr = len(js['filings']['recent'][hdr[0]])
        rows=[]
        for i in range(lr):
            row = []
            for k in hdr:
                row.append(js['filings']['recent'][k][i])
            rows.append(row)
        return hdr, rows

    def searchjsonsubmissions(self, cik, sub):
        # url = self.jsurl  % (cik.zfill(10) )
        # keys, rows = self.getandparsejson(url)
        keys, rows = self.sp.pivotsubmissions(cik)
        assert keys[5] == 'form', 'what??'
        for r in rows:
            if sub in r[5]:
                acc = r[0].replace('-', '')
                surl = 'https://www.sec.gov/Archives/edgar/data/%s/%s/%s' % (cik, acc, r[12])
                return surl
        return None

    def search13F(self, cik):
        url = '%s/%s' % (self.fprefix, cik)
        urla0 = self.searchlinks(url)
        if urla0 == None:
            print('search13F searchlinks failed for %s' % url, file=sys.stderr)
            return None
        urla0 = [u for u in urla0 if cik in u]
        if len(urla0) == 0:
            print('search13F CIK %s not in  %s' % (cik, url), file=sys.stderr)
            return None
        for i in range(len(urla0)):
            urla1 = self.searchlinks(urla0[i])
            if urla1 == None:
                print('search13F searchlinks failed for %s' % urla0[0], file=sys.stderr)
                return None
            urla1 = [u for u in urla1 if '-index.html' in u]
            if len(urla1) == 0:
                print('search13F -index.html not in  %s' % (url0[0]), file=sys.stderr)
                return None
            urla2 = self.searchlinks(urla1[0])
            if urla2 == None:
                print('search13F searchlinks failed for %s' % urla1[0], file=sys.stderr)
                return None
            furla = [u for u in urla2 if 'xslForm13F_X02' in u] 
            if len(furla) == 0:
                # print('search13F xslForm13F_X02 not  in  %s' % (urla1[0]), file=sys.stderr)
                continue
            return furla[-1]

    def searchSubmission(self, cik, sub, link, directory, show):
        """ searchSubmission

        search in the form.idx files for a page that contains a link
        to the X-k for a cik
        cik - central index key, required
        sub - submission form type
        link - if true, just return a url link to the submission html page
               if false, store the html page
        directory - directory to store the data
        show - display the output in your browser
        """
        url = None
        if '13F' in sub:
            url = self.search13F(cik)
        else:
            url = self.searchjsonsubmissions(cik, sub)
        if url == None:
            print('no submission for %s %s' % (cik, sub), file=sys.stderr)
            return
        if link:
            print(url)
        if show:
            webbrowser.open(url)
        if directory:
            tkresp = self.uq.query(url, self.hdr)
            ofn = os.path.join(directory, 'CIK%s%s.htm' %\
                (cik.zfill(10), sub ) )
            self.uq.storequery(tkresp, ofn)
        return

# if __name__ == '__main__':
def main():
    LT = EDGARLatestSubmission()

    argp = argparse.ArgumentParser(
              description='find the most recent submission for a ticker or cik for some common submissƣons.') 
    argp.add_argument("--cik", help="10-digit Central Index Key")
    argp.add_argument("--ticker", help="company ticker symbol")
    argp.add_argument("--submission", default='10-K',
        choices=['4', '144', '10-Q', '8-K', '13F-HR', '3', 'SD', 'PX14A6G', 'DEFA14A', 'ARS', 'DEF 14A', 'SC 13G/A', '10-K', 'S-3ASR', '424B5', 'FWP', 'PRE 14A', 'UPLOAD', 'CORRESP', 'SC 13G', '424B2', 'IRANNOTICE', 'S-8', '3/A', '5', 'EFFECT', 'POS AM', '424B3', 'S-4', 'S-8 POS'],
        help="X-K submission type")

    argp.add_argument("--link", action='store_true', default=False,
          help="return the url for the latest X-K")
    argp.add_argument("--directory", default='/tmp',
         help="directory to store the output")
    argp.add_argument("--show", action='store_true', default=False,
         help="show the X-K stored in directory to your browser")

    args = argp.parse_args()

    if not args.cik and not args.ticker:
        argp.print_help()
        sys.exit()

    cik = None
    if args.cik:
        cik = args.cik
    if args.ticker:
        cik = LT.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys.exit()

    LT.searchSubmission(cik, args.submission, link=args.link, directory=args.directory, show=args.show)

if __name__ == '__main__':
    main()
