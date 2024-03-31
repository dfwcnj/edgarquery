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
    from edgarquery import ebquery
    from edgarquery import tickerd
except ImportError as e:
    import ebquery
    import tickerd

class EDGARLatestsubmissions():

    def __init__(self):
        """ EDGARLatestsubmissions

        retrieve the latest submissions for a CIK
        a CIK is a central index key used by the SEC to identify a company
        """
        self.sprefix = 'https://www.sec.gov/Archives/edgar/full-index'
        self.rprefix = 'https://www.sec.gov/Archives'
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')
        self.now     = datetime.datetime.now()
        self.cik     = None
        self.submissions = {}
        self.uq = ebquery._EBURLQuery()
        self.chunksize =4294967296 # 4M
        self.td = tickerd.TickerD()

    def getcikforticker(self, ticker):
        return self.td.getcikforticker(ticker)

    def pgrep(self, pat=None, fn=None):
        """ pgrep(pat, fn)

        simulate grap when command does not exist
        pat - regular expression to match
        fn - filename to search
        """
        if not fn and not pat:
            print('pgrep pat and fn required')
            sys.exit(1)
        rc = re.compile(pat)
        with open(fn, 'r') as f:
            for line in f:
                if rc.search(line):
                    return line

    def dogrep(self, cik=None, sub=None, fn=None):
        """ dpgrep(cik, sub, fn)

        desparately try to grep for something
        construct a search command and search for the cik
        cik - central index key
        sub - forms part of a regular expression pattern
        fn - filename to search
        """
        if not fn and not sub and not cik:
            print('dogrep: fn, sub, and cik required')
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
                #os.unlink(fn)
            except Exception as e:
                print('grep url: %s' % (e), file=sys.stderr)
                sys.exit(1)
        else:
            res = self.pgrep(pat, fn)
            return res

    def getsubfromhtml(self, url, sub):
        """ getsubfromhtml(url, sub)

        parse the html table to find relative link to the submission html file
        complete the url and either return it or
        store the 10-k html file
        url - url to the submission
        sub - part os a pattern to search
        """
        resp = self.uq.query(url, self.hdr)
        #resp = self.query(url)
        rstr    = resp.read().decode('utf-8')
        # print(rstr)
        class MyHTMLParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    if hasattr(self, 'data') and sub == self.data:
                        if sub=='10-K' and '/ix?doc' in attrs[0][1]:
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                 attrs[0][1].split('=')[1])
                            self.data = tkurl
                            #print(tkurl)
                        elif sub!='10-K':
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                               attrs[0][1])
                            self.data = tkurl
                            #print(tkurl)
            def handle_data(self, data):
                if sub == data and not hasattr(self, 'data'):
                    self.data = sub
                    #print('data: %s' % (data) )

        parser = MyHTMLParser()
        parser.feed(rstr)
        if hasattr(parser, 'data'):
            tkurl = parser.data
            return tkurl

    def gensearchurls(self):
        """ gensearchurls()

        gensearchurls - 10-k files are published once a year or so
        and can be published on a schedule controlled by the company
        return a set of links to form files where the 10-K link may reside
        other submission files can be published at some schedule
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
        #surla.reverse()
        return surla

    def reportsubmissions(self, fp):
        """ reportsubmissions(fp)

        report latest submissions for a cik
        fp - file pointer to write
        """
        for k in self.submissions.keys():
            if len(self.submissions[k]) > 0:
                print('%s\t%s' % (k, self.submissions[k]) )

    def searchsubmissions(self, cik, directory):
        """ searchsubmissions(cik)

        search in the form.idx files for a time interval
        for a page that contains a link to the submissions for a cik
        return a dictionary containing the lastest submissions
        cik - central index key, required
        """
        surla = self.gensearchurls()
        ofn   = os.path.join(directory, 'form.idx')
        suba = ['10-Q','10-K','8-Q','8-K','20-F','40-F','6-K']
        latest={}
        for k in suba: latest[k]=''
        tktbl = None
        # search for submission types for each form.idx file
        for url in surla:
            resp = self.uq.query(url, self.hdr)
            self.uq.storequery(resp, ofn)
            # resp = self.query(url)
            # self.storequery(resp, tf=ofn)
            for sub in suba:
                tktbl = self.dogrep(cik, sub, ofn)
                if tktbl:
                    tkurl=self.getsubfromhtml(tktbl, sub)
                    if tkurl:
                        latest[sub]=tkurl
        os.unlink(ofn)
        self.submissions = latest
        return latest

# if __name__ == '__main__':
def main():
    LT = EDGARLatestsubmissions()

    argp = argparse.ArgumentParser(
              description='find the most recent submissions for cik')
    argp.add_argument("--cik", help="10-digit Central Index Key")
    argp.add_argument("--ticker", help="company ticker symbol")

    argp.add_argument("--directory", default='/tmp',
        help="directory to store the output")
    argp.add_argument('--file', help="where to store the output")

    args = argp.parse_args()

    cik = None
    if args.cik:
        cik = args.cik
    if args.ticker:
        cik = LT.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys,exit()

    LT.cik = cik

    latest = LT.searchsubmissions(cik, args.directory)

    fp = sys.stdout
    if args.file:
        try:
            fp = open(args.file, 'w')
        except Exception as e:
            print('%s: %s' % (args.file, e) )

    LT.reportsubmissions(fp)

if __name__ == '__main__':
    main()
