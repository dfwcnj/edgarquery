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
    from edgarquery import ebquery
    from edgarquery import tickerd
except ImportError as e:
    import ebquery
    import tickerd

class EDGARSubmissions():

    def __init__(self):
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
              HTTP User-Agent value such as an email address', file=sys.stderr)
            sys.exit(1)
        self.now     = datetime.datetime.now()
        self.uq = ebquery._EBURLQuery()
        self.td = tickerd.TickerD()
        self.chunksize =4294967296 # 4M
        self.submissionsdict=None


    def getcikforticker(self, ticker):
        return self.td.getcikforticker(ticker)

    def getgrepdata(self, lns):
        """ getgrepdata(lns)

        collect the results of a search of form data for a cik
        """
        if len(lns) > 0:
            subdict = {}
            #soa = so.decode('utf-8').split('\n')
            for ln in lns:
                if len(ln) == 0: continue
                lna = ln.split()
                date = lna[-2]
                cik  = lna[-3]
                ftype = lna[0]
                # if ftype == '4': print(ln, file=sys.stderr)
                url = '%s/%s-index.htm' % (self.rprefix,
                      lna[-1].split('.')[0] )
                if lna[0] == 'SC' or lna[1] == 'POS':
                    ftype = '%s %s' % (lna[0], lna[1])
                    subdict['%s %s' % (lna[0], lna[1])] = url
                else:
                    ftype = lna[0]
                    subdict[lna[0]] = url
                #self.submissionsdict[cik][ftype][date]['frmurl'] = url
                if ftype not in self.submissionsdict[cik].keys():
                    self.submissionsdict[cik][ftype]={}
                    self.submissionsdict[cik][ftype][date]= {}
                    self.submissionsdict[cik][ftype][date]['frmurl']=url
                elif date not in self.submissionsdict[cik][ftype].keys():
                    self.submissionsdict[cik][ftype][date]={}
                    self.submissionsdict[cik][ftype][date]['frmurl']=url
                else:
                    self.submissionsdict[cik][ftype][date]['frmurl']=url

    def pgrep(self, pat=None, fn=None):
        """ pgrep

        simulate grap when command does not exist
        pat - regular expression to match
        fn - name of file to search
        """
        if not pat and not fn:
            print('pgrep pat and fn required', file=sys.stderr)
            sys.exit(1)
        recs = []
        rc = re.compile(pat)
        with open(fn, 'r') as f:
            for line in f:
                if rc.search(line):
                    recs.append(line)

        return recs

    def dogrep(self, cik=None, fn=None):
        """ dpgrep

        desparately try to grep for something
        cik - central index key for which to search
        fn - name of file to search
        """
        if not cik and not fn:
            print('dogrep: fn, and cik required', file=sys.stderr)
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
                    self.getgrepdata(soa)
                if se:
                    err = se.decode('utf-8')
                    print(err, file=sys.stderr)
                    sys.exit(1)
                #os.unlink(fn)
            except Exception as e:
                print('grep url: %s' % (e), file=sys.stderr)
                sys.exit(1)
        else:
            res = self.pgrep(pat, fn)
            self.getgrepdata(res)

    def gethtmldata(self, cik, ftype, date, dict):
        frmurl = dict['frmurl']
        for ft in dict.keys():
            if ft == 'frmurl': continue
            rpturl = dict[ft]
            if ft not in self.submissionsdict[cik].keys():
                self.submissionsdict[cik][ft] = {}
            if date not in self.submissionsdict[cik][ft].keys():
                self.submissionsdict[cik][ft][date]={}
            self.submissionsdict[cik][ft][date]['frmurl'] = frmurl
            self.submissionsdict[cik][ft][date]['rpturl'] = rpturl

    def queryhtml(self, subtype, url):
        """

        parse the html table to find relative link to the
        submission html file
        complete the url and either return it or
        store the 10-k html file
        subtype - pattern to find
        url - url whose contents to search
        """
        resp = self.uq.query(url, self.hdr)
        # resp = self.query(url)
        rstr    = resp.read().decode('utf-8')
        # print('queryhtml: %s' % (url) )
        class MyHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.subdict = {}
            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    # if 'cgi-bin' in attrs[0][1]: return  # responsible parties
                    if 'browse-edgar' in attrs[0][1]: return
                    if 'filename' in attrs[0][1]: return
                    #if '.xml' in attrs[0][1]: return
                    if '.jpg' in attrs[0][1]: return
                    if len(attrs[0]) > 2:
                        print(attrs, file=sys.stderr)
                    if len(attrs[0])==2 and \
                           ('.htm' not in attrs[0][1] and \
                           ('_' in attrs[0][1] and 'txt' in attrs[0][1])):
                        return
                    if hasattr(self, 'data'):
                        if 'CERTIFICATION OF' in self.data: return
                        # if 'DOCUMENT' in self.data: return
                        sub = self.data
                        if sub=='10-K' and '/ix?doc' in attrs[0][1]:
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                 attrs[0][1].split('=')[1])
                            self.subdict[sub] = tkurl
                            # print('%s\t%s' % (sub, tkurl) )
                        elif '.xml' in attrs[0][1]:
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                               attrs[0][1])
                            self.subdict[subtype] = tkurl
                            # print('%s\t%s' % (sub, tkurl) )
                        else:
                            if 'own-disp' in attrs[0][1]:
                                return
                            tkurl =  '%s%s' % ('https://www.sec.gov',
                                               attrs[0][1])
                            self.subdict[sub] = tkurl
                            # print('%s\t%s' % (sub, tkurl) )

            def handle_data(self, data):
                if self.lasttag == 'td' and '\n' not in data:
                    self.data = data
                    #print('data: %s' % (data), file=sys.stderr )

        parser = MyHTMLParser()
        parser.feed(rstr)
        if hasattr(parser, 'subdict'):
            dict = parser.subdict
            dict['frmurl'] = url
            return dict
        #if hasattr(parser, 'data'):
        #    tkurl = parser.data
        #    return tkurl

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
            surla.append('%s/%d/QTR2/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR3/form.idx' % (self.sprefix, yr) )
            surla.append('%s/%d/QTR4/form.idx' % (self.sprefix, yr) )
        return surla

    def reportsubmissions(self, file, directory):
        fp = sys.stdout
        if file:
            ofn=file
            if directory: 
               ofn=os.path.join(directory, file)
            try:
                fp = open(ofn, 'w')
            except IOError as e:
                print('%s: %s' % (file, e) )
                sys.exit(1)
        print("'CIK','type','date','frmurl','rpturl'", file=fp)
        for cik in self.submissionsdict.keys():
            for ftype in self.submissionsdict[cik].keys():
                for date in self.submissionsdict[cik][ftype].keys():
                    ra = []
                    if 'frmurl' not in \
                        self.submissionsdict[cik][ftype][date].keys():
                            print('frmurl %s %s %s' % (cik, ftype, date),
                                   file=sys.stderr)
                            continue
                    else:
                        frmurl = \
                            self.submissionsdict[cik][ftype][date]['frmurl']
                    if 'rpturl' not in \
                        self.submissionsdict[cik][ftype][date].keys():
                            print('rpturl %s %s %s' % (cik, ftype, date),
                                file=sys.stderr)
                            continue
                    else:
                        rpturl = \
                            self.submissionsdict[cik][ftype][date]['rpturl']
                    ra.append("'%s'," % (cik) )
                    ra.append("'%s'," % (ftype) )
                    ra.append("'%s'," % (date) )
                    ra.append("'%s'," % (frmurl) )
                    ra.append("'%s'"  % (rpturl) )
                    print(''.join(ra), file=fp)


    def searchformindices(self, cik, year, directory):
        """ searchsubmissions(cik, year)

        search in the form.idx files for a page that
        contains a link to the submissions for a cik
        return a dictionary containing the lastest submissions
        cik - central index key
        year - year to search
        """
        # to avoid dictionary resize during iteration exception
        htmldicts={}
        self.submissionsdict={}
        self.submissionsdict[cik] = {}
        surla = self.gensearchurls(year)
        ofn   = os.path.join(directory, 'form.idx')
        tktbl = None
        # download each form.idx file in turn
        # for each form.idx search for the cik
        for url in surla:
            resp = self.uq.query(url, self.hdr)
            self.uq.storequery(resp, ofn)
            # resp = self.query(url)
            # self.storequery(resp, tf=ofn)
            #print('\tSEARCHING for %s in %s' % (cik, url), file=sys.stderr )
            self.dogrep(cik, ofn)
        for cik in self.submissionsdict.keys():
            htmldicts[cik]={}
            for ftype in self.submissionsdict[cik].keys():
                htmldicts[cik][ftype]={}
                for date in self.submissionsdict[cik][ftype].keys():
                    htmldicts[cik][ftype][date]=[]
                    url = self.submissionsdict[cik][ftype][date]['frmurl']
                    # search the html page
                    dict = self.queryhtml(ftype, url)
                    if not dict:
                        print('%s %s' % (ftype, url), file=sys.stderr )
                    htmldicts[cik][ftype][date].append(dict)
        for cik in htmldicts.keys():
            for ftype in htmldicts[cik].keys():
                for date in htmldicts[cik][ftype].keys():
                    for dict in htmldicts[cik][ftype][date]:
                        self.gethtmldata(cik, ftype, date, dict)
        os.unlink(ofn)

# if __name__ == '__main__':
def main():
    LS = EDGARSubmissions()

    now = datetime.datetime.now()
    year = now.year

    argp = argparse.ArgumentParser(
              description='find the most recent submissions for cik')
    argp.add_argument("--cik", help="10-digit Central Index Key")
    argp.add_argument("--ticker", help="company ticker symbol")
    argp.add_argument("--year", required=False,
        help="year to search for submissions if not current year")

    argp.add_argument("--file", required=False,
        help="store the output in this file")
    argp.add_argument("--directory", default='/tmp',
        help="store the output in this directory")

    args = argp.parse_args()

    if args.year: year = int(args.year)

    cik = None
    if args.cik:
        cik = args.cik
    if args.ticker:
        cik = LS.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys.exit()

    LS.cik = args.cik
    LS.searchformindices(cik, year, directory=args.directory)
    LS.reportsubmissions(file=args.file, directory=args.directory)

if __name__ == '__main__':
    main()
