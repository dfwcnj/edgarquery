#! /usr/bin/env python

#
# EDGARLatestSubmission
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
import webbrowser
from functools import partial

try:
    from edgarquery import ebquery
    from edgarquery import tickerd
except ImportError as e:
    import ebquery
    import tickerd

class EDGARLatestSubmission():

    def __init__(self):
        """ EDGARLatestSubmission

        retrieve the latest SEC submission data for a company
        """
        self.sprefix = 'https://www.sec.gov/Archives/edgar/full-index'
        self.rprefix = 'https://www.sec.gov/Archives'
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

    def getcikforticker(self, ticker):
        return self.td.getcikforticker(ticker)

    def pgrep(self, pat=None, fn=None):
        """ pgrep

        simulate grap when command does not exist
        pat - regular expression pattern to match
        fn  - name of file to search
        """
        if not fn and not pat:
            print('pgrep pat and fn required')
            sys.exit(1)
        rc = re.compile(pat)
        with open(fn, 'r') as f:
            for line in f:
                if rc.search(line):
                    return line

    def dogrep(self, cik, sub, fn):
        """ dpgrep(cik, fn)

        desparately try to grep for something
        cik - SEC central index key
        sub - submission form type
        fn - name of file to search
        """
        if not fn and not cik:
            print('dogrep: fn and cik required')
            sys.exit(1)
        cmd=None
        pat = '%s.* %s ' % (sub, cik)
        if os.path.exists(os.path.join('/', 'bin', 'grep') ):
            cmd = os.path.join('bin', 'grep')
        elif os.path.exists(os.path.join('/', 'usr', 'bin', 'grep') ):
            cmd = os.path.join('/', 'usr', 'bin', 'grep')

        if cmd:
            try:
                sp = subprocess.Popen([cmd, pat, fn],
                       bufsize=-1, stdout=subprocess.PIPE)
                so, se = sp.communicate()
                if so:
                    out = so.decode('utf-8')
                    htm = '%s/%s-index.htm' % (self.rprefix,
                           out.split()[-1].split('.')[0] )
                    # print(htm)
                    return htm
                if se:
                    err = se.decode('utf-8')
                    print(err)
                    sys.exit(1)
                os.unlink(fn)
            except Exception as e:
                print('grep url: %s' % (e), file=sys.stderr)
                sys.exit(1)
        else:
            res = self.pgrep(pat, fn)
            return res

    def getxkfromhtml(self, cik, sub, url, link, directory):
        """ getxkfromhtml(url, link)

        this is a little brittle about depending too much on the web
        page link order
        parse the html table to find relative link to submission html file
        complete the url and either return it or
        store the submission html file
        cik = central index key
        sub submission type
        url - url containing the links to submission files
        link - if true, just return a url link to the submission html page
               if false, store the html page
        directory - directory to store the output
        """
        resp = self.uq.query(url, self.hdr)
        rstr    = resp.read().decode('utf-8')
        # resp = self.query(url)
        # rstr    = resp.read().decode('utf-8')
        # print(rstr)
        class MyHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tkurl = None
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    if 'ix?doc' in attrs[0][1]:
                        self.tkurl =  '%s%s' % ('https://www.sec.gov',
                             attrs[0][1].split('=')[1])
                        #print(self.tkurl)
                    elif 'Archives' in attrs[0][1] and \
                    (attrs[0][1].endswith('.htm') or \
                    attrs[0][1].endswith('.html') or \
                    attrs[0][1].endswith('.xml')) and not self.tkurl:
                        self.tkurl =  '%s%s' % ('https://www.sec.gov',
                                                attrs[0][1])
            def handle_endtag(self, tag):
                pass
            def handle_data(self, data):
                pass
        parser = MyHTMLParser()
        parser.feed(rstr)
        tkurl = parser.tkurl
        return tkurl

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
        ya = [y for y in range(self.now.year, 1993, -1)]
        for y in ya:
            qa = [q for q in range(4, 0, -1)]
            for q in qa:
                url = '%s/%d/QTR%d/form.idx' % (self.sprefix, y, q)

                ofn   = os.path.join(directory, 'form.idx')
                tktbl = None
                resp = self.uq.query(url, self.hdr)
                if resp == None:
                    continue
                self.uq.storequery(resp, ofn)
                print('\tSEARCHING: %s' % (url) )
                tktbl = self.dogrep(cik, sub, ofn)
                if tktbl:
                    tkurl = self.getxkfromhtml(cik, sub, tktbl, link, directory)
                    if link:
                        print(tkurl)
                    if show:
                        webbrowser.open(tkurl)
                    if directory:
                        tkresp = self.uq.query(tkurl, self.hdr)
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
        choices=['SC 13D', '13F-HR', 'DEF 14A', '8-K', '10-K', '10-Q'],
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
