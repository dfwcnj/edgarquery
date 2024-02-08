#! /usr/bin/env python

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

class EDGARSubmissions():

    def __init__(self, odir=None):
        """ EDGARSubmissions

        retrieve submissions for a CIK for some year
        if the year is the current year, get submissions so far
        """
        self.sprefix = 'https://www.sec.gov/Archives/edgar/full-index'
        self.rprefix = 'https://www.sec.gov/Archives'
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid\
                   HTTP User-Agent value such as an email address')
        self.now     = datetime.datetime.now()
        if odir: self.odir = odir
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.odir = os.path.abspath(self.odir)
        self.chunksize =4294967296 # 4M

    def query(self, url=None):
        """query - retrieve a url
         url - url to retrieve
        """
        try:
            req = urllib.request.Request(url, headers=self.hdr)
            resp = urllib.request.urlopen(req)
            return resp
        except urllib.error.URLError as e:
            print("Error %s(%s): %s" % ('query', url, e.reason),
            file=sys.stderr )
            sys.exit(1)

    def storequery(self, qresp, tf):
        """storequery - store the query response in a file
        resp - the query response
        tf   - filename that will hold the query response
        """
        if not qresp:
            print('storequery: no content', file=sys.stderr)
            sys.exit(1)
        if not tf:
            print('storequery: no output filename', file=sys.stderr)
            sys.exit(1)
        of = os.path.abspath(tf)
        # some downloads can be somewhat large
        with open(of, 'wb') as f:
            parts = iter(partial(qresp.read, self.chunksize), b'')
            for c in parts:
                f.write(c)
            #if c: f.write(c)
            f.flush()
            os.fsync(f.fileno() )
            return

    def pgrep(self, pat=None, fn=None):
        """ pgrep

        simulate grap when command does not exist
        pat - regular expression to match
        fn - name of file to search
        """
        if not pat and not fn:
            print('pgrep pat and fn required')
            sys.exit(1)
        rc = re.compile(pat)
        with open(fn, 'r') as f:
            for line in f:
                if rc.search(line):
                    return line

    def dogrep(self, cik=None, fn=None):
        """ dpgrep

        desparately try to grep for something
        cik - central index key for which to search
        fn - name of file to search
        """
        if not cik and not fn:
            print('dogrep: fn, and cik required')
            sys.exit(1)

        cmd=None
        pat = ' %s ' % (cik)
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
                    subdict = {}
                    soa = so.decode('utf-8').split('\n')
                    for ln in soa:
                        if len(ln) == 0: continue
                        lna = ln.split()
                        htm = '%s/%s-index.htm' % (self.rprefix,
                              lna[-1].split('.')[0] )
                        if lna[0] == 'SC':
                            subdict['%s %s' % (lna[0], lna[1])] = htm
                        else:
                            subdict[lna[0]] = htm
                    return subdict
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

    def getsubfromhtml(self, subtype, url):
        """

        parse the html table to find relative link to the
        submission html file
        complete the url and either return it or
        store the 10-k html file
        subtype - pattern to find
        url - url whose contents to search
        """
        #print('\tSEARCHING %s %s' % (subtype, url), file=sys.stderr)
        print('\tSEARCHING %s %s' % (subtype, url) )
        resp = self.query(url)
        rstr    = resp.read().decode('utf-8')
        # print(rstr)
        class MyHTMLParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    # if 'cgi-bin' in attrs[0][1]: return  # responsible parties
                    if 'browse-edgar' in attrs[0][1]: return
                    if 'filename' in attrs[0][1]: return
                    if '.jpg' in attrs[0][1]: return
                    if len(attrs[0])==2 and \
                           ('.htm' not in attrs[0][1] and \
                           ('_' in attrs[0][1] and 'txt' in attrs[0][1])):
                        return
                    if hasattr(self, 'data'):
                        sub = self.data
                        if 'CERTIFICATION OF' in self.data: return
                        if sub=='10-K' and '/ix?doc' in attrs[0][1]:
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                 attrs[0][1].split('=')[1])
                            #self.data = tkurl
                            print('%s\t%s' % (sub, tkurl) )
                        elif sub!='10-K':
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                               attrs[0][1])
                            #self.data = tkurl
                            print('%s\t%s' % (sub, tkurl) )
            def handle_data(self, data):
                if self.lasttag == 'td' and '\n' not in data:
                    self.data = data
                    #print('data: %s' % (data) )

        parser = MyHTMLParser()
        parser.feed(rstr)
        if hasattr(parser, 'data'):
            tkurl = parser.data
            return tkurl

    def gensearchurls(self, yr):
        """ gensearchurls(yr)

        generate url set to search for submissions
        yr - year to search
        """
        surla = []
        if yr == datetime.datetime.now().year:
            mo = datetime.datetime.now().month
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            if mo > 3:
                surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr) )
            elif mo > 6:
                surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr) )
            elif mo > 9:
                surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr) )
            return surla
        else:
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR1/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr) )
        return surla

    def searchsubmissions(self, cik, year):
        """ searchsubmissions(cik, year)

        search in the form.idx files for a page that
        contains a link to the submissions for a cik
        return a dictionary containing the lastest submissions
        cik - central index key
        year - year to search
        """
        surla = self.gensearchurls(year)
        ofn   = os.path.join(self.odir, 'form.idx')
        tktbl = None
        # search for submission types for each form.idx file
        for url in surla:
            resp = self.query(url)
            self.storequery(resp, tf=ofn)
            #print('\tSEARCHING for %s in %s' % (cik, url), file=sys.stderr )
            print('\tSEARCHING for %s in %s' % (cik, url) )
            tkdict = self.dogrep(cik, ofn)
            if tkdict:
                for k in tkdict.keys():
                    tkurl=self.getsubfromhtml(k, tkdict[k])
        os.unlink(ofn)

if __name__ == '__main__':
    def main():
        LS = EDGARSubmissions()

        now = datetime.datetime.now()
        year = now.year

        argp = argparse.ArgumentParser(
                  description='find the most recent submissions for cik')
        argp.add_argument("--cik", required=True,
                help="10-digit Central Index Key")
        argp.add_argument("--year", required=False,
            help="year to search for submissions if not current year")

        args = argp.parse_args()

        if args.year: year = int(args.year)

        LS.cik = args.cik
        LS.searchsubmissions(args.cik, year)

    main()
