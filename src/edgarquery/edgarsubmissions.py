#! /usr/bin/env python

#
# EDGARSubmissions
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

class EDGARSubmissions():

    def __init__(self):
        """ EDGARSubmissions

        retrieve submissions for a CIK for some year
        if the year is the current year, get submissions so far
        """
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid\
              HTTP User-Agent value such as an email address', file=sys.stderr)
            sys.exit(1)
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

    def getjsonsubmissions(self, cik, year):
            keys, rows = self.sp.pivotsubmissions(cik)
            assert keys[1] == 'filingDate', 'submissions not in proper format'
            ri = -1     # index of first row in submission year
            for i in range(len(rows)):
                if year in rows[i][1]:
                    ri = i
                    break
            sa = []
            if ri == -1:
                print('getjsonsubmissions no rows for %s' % (year))
                return sa
            keys.append('url')
            sa.append(keys)
            for i in range(ri, len(rows)):
                row = rows[i]
                if year not in row[1]:
                    return sa
                for j in range(len(row)):
                   if type(row[j]) == type(1):
                       row[j] = '%d' % row[j]
                acc = row[0].replace('-', '')
                surl = 'https://www.sec.gov/Archives/edgar/data/%s/%s/%s' % (cik, acc, row[12])
                row.append(surl)
                sa.append(row)
            return sa

    def show(self, sa, ticker, cik):
        sa[0].append('url')
        for i in range(1, len(sa)):
             acc = sa[i][0].replace('-', '')
             surl = 'https://www.sec.gov/Archives/edgar/data/%s/%s/%s' % (cik, acc, sa[i][12])
             sa[i].append('<a href="%s">url</a>' % surl)

        self.sh.aashow(sa, ticker)

def main():

    now = datetime.datetime.now()
    year = now.year

    argp = argparse.ArgumentParser(
              description='find the most recent submissions for ticker or cik')
    argp.add_argument("--cik", help="10-digit Central Index Key")
    argp.add_argument("--ticker", help="company ticker symbol")
    argp.add_argument("--year", default=year,
        choices=range(2014, year+1),
        type=int,
        help="year to search for submissions if not current year")

    argp.add_argument("--file", help="store the output in this file")
    argp.add_argument("--directory", default='/tmp',
        help="store the output in this directory")
    argp.add_argument("--show", action='store_true', default=False,
         help="show the 10-K stored in directory to your browser")

    args = argp.parse_args()

    if args.year:
        year = '%d' % args.year

    LS = EDGARSubmissions()

    cik = None
    if args.cik:
        cik = args.cik
    if args.ticker:
        cik = LS.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys.exit()

    sa = LS.getjsonsubmissions(cik, year)

    fp = sys.stdout
    if args.file:
        try:
            fn = os.path.join(args.directory, args.file)
            fp = open(fn, 'w')
        except Exception as e:
            print('%s: %s' % (args.file, e) )

    if args.show:
        LS.show(sa, args.ticker, cik)

    if not args.file and not args.show:
        LS.reportsubmissions(sa, fp)

if __name__ == '__main__':
    main()
