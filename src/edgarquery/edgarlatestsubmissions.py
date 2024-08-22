#! /usr/bin/env python

#
# EDGARLatestsubmissions
#

import os
import re
import html
from html.parser import HTMLParser
import sys
import argparse
import datetime
import subprocess
import urllib.request
from functools import partial

try:
    from edgarquery import aa2html
    from edgarquery import ebquery
    from edgarquery import edgarsubmissionspivot
    from edgarquery import tickerd
except ImportError as e:
    import aa2html
    import ebquery
    import edgarsubmissionspivot
    import tickerd

class EDGARLatestsubmissions():

    def __init__(self):
        """ EDGARLatestsubmissions

        retrieve the latest submissions for a CIK
        a CIK is a central index key used by the SEC to identify a company
        """
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')
        self.now     = datetime.datetime.now()
        self.uq = ebquery._EBURLQuery()
        self.td = tickerd.TickerD()
        self.sp = edgarsubmissionspivot.EDGARSubmissionsPivot()
        self.sh = aa2html._AA2HTML()

    def getcikforticker(self, ticker):
        return self.td.getcikforticker(ticker)

    def reportsubmissions(self, sa, fp):
        """ reportsubmissions(fp)

        report latest submissions for a cik
        fp - file pointer to write
        """
        for row in sa:
            r = ','.join(row)
            print('%s\n' % r, file=fp)

    def searchsubmissions(self, cik, directory):
        """ searchsubmissions(cik)

        search in the form.idx files for a time interval
        for a page that contains a link to the submissions for a cik
        return a dictionary containing the lastest submissions
        cik - central index key, required
        """
        suba = ['4', '144', '10-Q', '8-K', '13F-HR', '3', 'SD', 'PX14A6G', 'DEFA14A', 'ARS', 'DEF 14A', 'SC 13G/A', '10-K', 'S-3ASR', '424B5', 'FWP', 'PRE 14A', 'UPLOAD', 'CORRESP', 'SC 13G', '424B2', 'IRANNOTICE', 'S-8', '3/A', '5', 'EFFECT', 'POS AM', '424B3', 'S-4', 'S-8 POS']
        keys, rows = self.sp.pivotsubmissions(cik)
        sa = []
        sd = {}
        sa.append(keys)
        for row in rows:
            if len(sd.keys()) == len(suba):
                return sa
            if row[5] in suba and row[5] not in sd.keys():
                 for i in range(len(row)):
                     if type(row[i]) == type(1):
                         row[i] = '%d' % row[i]
                 #row.append(surl)
                 sa.append(row)
                 sd[row[5]]=1
        return sa

    def show(self, sa, ticker, cik):
        sa[0].append('url')
        for i in range(1, len(sa)):
             acc = sa[i][0].replace('-', '')
             surl = 'https://www.sec.gov/Archives/edgar/data/%s/%s/%s' % (cik, acc, sa[i][12])
             sa[i].append('<a href="%s">url</a>' % surl)

        self.sh.aashow(sa, ticker)

def main():
    LS = EDGARLatestsubmissions()

    argp = argparse.ArgumentParser(
             description='find the most recent submissions for a ticker or cik')
    argp.add_argument("--cik", help="10-digit Central Index Key")
    argp.add_argument("--ticker", help="company ticker symbol")

    argp.add_argument("--directory", default='/tmp',
        help="directory to store the output")
    argp.add_argument('--file', help="where to store the output")
    argp.add_argument("--show", action='store_true', default=False,
         help="show the 10-K stored in directory to your browser")

    args = argp.parse_args()

    cik = None
    if args.cik:
        cik = args.cik
    if args.ticker:
        cik = LS.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys,exit()

    sa = LS.searchsubmissions(cik, args.directory)

    fp = sys.stdout
    if args.file:
        try:
            fn = os.path.join(args.directory, args.file)
            fp = open(fn, 'w')
            LS.reportsubmissions(sa, fp)
        except Exception as e:
            print('%s: %s' % (args.file, e) )

    if args.show:
        LS.show(sa, args.ticker, cik)

    if not args.file and not args.show:
        LS.reportsubmissions(sa, fp)

if __name__ == '__main__':
    main()
