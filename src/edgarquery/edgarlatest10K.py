#! /usr/bin/env python

#
# EDGARLatest10K
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

class EDGARLatest10K():

    def __init__(self):
        """ EDGARLatest10K

        retrieve the latest 10-K data
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

    def dogrep(self, cik=None, fn=None):
        """ dpgrep(cik, fn)

        desparately try to grep for something
        cik - SEC central index key
        fn - name of file to search
        """
        if not fn and not cik:
            print('dogrep: fn and cik required')
            sys.exit(1)
        cmd=None
        pat = '10-K.* %s ' % cik
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

    def get10kfromhtml(self, cik, url, link, directory):
        """ get10kfromhtml(url, link)

        parse the html table to find relative link to 10-K html file
        complete the url and either return it or
        store the 10-k html file
        url - url containing the links to 10-K files
        link - if true, just return a url link to the 10-K html page
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
            def handle_endtag(self, tag):
                pass
            def handle_data(self, data):
                pass
        parser = MyHTMLParser()
        parser.feed(rstr)
        tkurl = parser.tkurl
        return tkurl

    def gensearchurls(self):
        """ gensearchurls()

        10-k files are published once a year or so
        and can be published on a schedule controlled by the company
        return a set of links to form files where the 10-K link
        may reside
        """
        surla = []
        yr = self.now.year
        mo = self.now.month
        if mo <=3:
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
        elif mo <=6:
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr) )
        elif mo <=9:
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr) )
        else:
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr-1) )
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr) )
        surla.reverse()
        return surla

    def search10K(self, cik, link, directory, show):
        """ search10K

        search in the form.idx files for a page that contains a link
        to the 10-k for a cik
        cik - central index key, required
        link - if true, just return a url link to the 10-K html page
               if false, store the html page
        """
        surla = self.gensearchurls()
        ofn   = os.path.join(directory, 'form.idx')
        tktbl = None
        for url in surla:
            resp = self.uq.query(url, self.hdr)
            self.uq.storequery(resp, ofn)
            # resp = self.query(url)
            # self.storequery(resp, tf=ofn)
            print('\tSEARCHING: %s' % (url) )
            tktbl = self.dogrep(cik, ofn)
            if tktbl:
                tkurl = self.get10kfromhtml(cik, tktbl, link, directory)
                if link:
                    print(tkurl)
                if directory:
                    tkresp = self.uq.query(tkurl, self.hdr)
                    ofn = os.path.join(directory, 'CIK%s.10-K.htm' %\
                        (cik.zfill(10) ) )
                    self.uq.storequery(tkresp, ofn)
                    if show:
                        webbrowser.open('file://%s' % (ofn) )
                return


# if __name__ == '__main__':
def main():
    LT = EDGARLatest10K()

    argp = argparse.ArgumentParser(
              description='find the most recent 10-K for cik')
    argp.add_argument("--cik", help="10-digit Central Index Key")
    argp.add_argument("--ticker", help="company ticker symbol")
    argp.add_argument("--link", action='store_true', default=False,
          help="return the url for the latest 10-K")
    argp.add_argument("--directory", default='/tmp',
         help="directory to store the output")
    argp.add_argument("--show", action='store_true', default=False,
         help="show the 10-K stored in directory to your browser")

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

    LT.search10K(cik, link=args.link, directory=args.directory, show=args.show)

if __name__ == '__main__':
    main()
