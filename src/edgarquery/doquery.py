#! env python

#
# EDGARquery
#

import os
import datetime
import sys
import argparse
from functools import partial
import re
import urllib.request

class EDGARquery():

    def __init__(self, cik=None, cy=None, odir=None):
        """EDGARquery - search the SEC EDGAR site

         --cik        - 10-digit Central Index Key
         --cy         - calendar year e.g. CY2023, CY2023Q1, CY2023Q4I
         --file         - file to store output
        --companyconcept - company concept json file
           --cik
               leading 0s optional
           --frame - reporting frame, default us-gaap
               e.g us-gaap, ifrs-full, dei, srt
           --fact - fact to collect, default URS-per-shares
               e.g AccountsPayableCurrent, AccountsAndNotesReceivableNet
           --file - default /tmp/companyconcept.$frame.$fact.json
        or
        --companyfacts - all the company concepts data for a company
            --cik
            --file - default /tmp/$cik.json
        or
        --xbrlframes Extensible Business Markup Language
            --frame
            --fact
            --cy
        or
        --companyfactsearchzip - all the data from the XBRL Frame API
            and the XBRL Company Facts in a zip file
            --file - default /tmp/companyfact.zip
        --submissionzip -  public EDGAR filing history for all filers
            --file - default /tmp/submissions.zip
        or
        --financialstatementandnotesdataset - data extracted from
          reports filed from 2009 to present. does not include certain
          metadata filed. filed quarterly until 11/2020. filed monthly
          after that
          --cy calendar year e.g. CY2015Q2, CY2023M12
        """
        self.cik        = cik
        self.cy         = cy
        if odir: self.odir = odir
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.odir = os.path.abspath(self.odir)
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')

        # https://www.bellingcat.com/resources/2023/12/18/
        #     new-tools-dig-deeper-into-hard-to-aggregate-us-corporate-data/
        self.ctkrs      = 'https://www.sec.gov/files/company_tickers.json'
        self.xbrlrss    = 'https://www.sec.gov/Archives/edgar/xbrlrss.all.xml'

        self.xbrl       = 'https://data.sec.gov/api/xbrl'
        self.ccurl      = '%s/companyconcept' % self.xbrl
        self.cfurl      = '%s/companyfacts'   % self.xbrl
        self.frurl      = '%s/frames'         % self.xbrl

        self.edi        = 'https://www.sec.gov/Archives/edgar/daily-index'
        self.cfzip      = '%s/xbrl/companyfacts.zip'    % self.edi
        self.subzip     = '%s/bulkdata/submissions.zip' % self.edi
        self.fsanurl    = 'https://www.sec.gov/files/dera/data/financial-statement-and-notes-data-sets'

        self.chunksize = 4194304
        self.argp      = None
        self.content   = None

        # xbrlframes is not yet well defined
        self.xfurl    = "https://data.sec.gov/api/xbrl/frames"

    def gency(self):
        """gency - generate a CY type I vslue for the previous quarter
        """
        dt = datetime.datetime.now()
        y  = dt.year
        if dt.month >=1 and dt.month <=3: # previous year
            q='4'
            y = y - 1
        # previous quarter
        elif dt.month >=4 and dt.month <=6:  q='1'
        elif dt.month >=7 and dt.month <=9:  q='2'
        else:                                q='3'
        cy = 'CY%sQ%sI' % (y, q)
        return cy

    def query(self, url=None):
        """query(url) - query a url

         url - url of file to retrieve
        """
        try:
            req = urllib.request.Request(url, headers=self.hdr)
            resp = urllib.request.urlopen(req)
            return resp
        except urllib.error.URLError as e:
            print("Error %s(%s): %s" % ('query', url, e.reason),
            file=sys.stderr )
            sys.exit(1)

    def storequery(self, qresp, file):
        """storequery(qresp, file) - store the query response in a file

        resp - the query response
        file   - filename that will hold the query response
        """
        if not qresp: 
            print('storequery: no content', file=sys.stderr)
            sys.exit(1)
        if not file:
            print('storequery: no output filename', file=sys.stderr)
            sys.exit(1)
        of = os.path.abspath(file)
        # some downloads can be somewhat large
        with open(of, 'wb') as f:
            parts = iter(partial(qresp.read, self.chunksize), b'')
            for c in parts:
                f.write(c)
            #if c: f.write(c)
            f.flush()
            os.fsync(f.fileno() )
            return

    def companyconcept(self, cik=None, frame='us-gaap', fact=None, file=None):
        """companyconcept(cik, frame, fact, file)

        all xbrl disclosures for one company in JSON
        cik             - 10-digit Central Index Key - required
        frame - reporting frame e.g us-gaap, ifrs-full, dei, srt
        fact - fact to collect e.g AccountsPayableCurrent
        """

        if not cik or not fact:
            print('companyconcept(frame, cik, fact)', file=sys.stderr)
            self.argp.print_help()
            sys.exit(1)

        if not file:
            file = os.path.join(self.odir,
              'CompanyConcept.CIK%s.%s.%s.json' % (cik.zfill(10), frame, fact) )
        url = '%s/CIK%s/%s/%s.json' % (self.ccurl, cik.zfill(10), frame, fact)
        resp = self.query(url)
        self.storequery(resp, file)

    def companyfacts(self, cik=None, file=None):
        """companyfacts 

        all the company concepts data for a company
        cik - 10-digit Central Index Key required
        file - file to store the json
        """
        if not cik:
            print('companyfacts(cik)', file=sys.stderr)
            self.argp.print_help()
            sys.exit(1)

        if not file:
            file=os.path.join(self.odir,
                'CompanyFacts.CIK%s.json' % (cik.zfill(10)) )
        url = '%s/CIK%s.json' % (self.cfurl, cik.zfill(10))
        resp = self.query(url)
        self.storequery(resp, file)

    def xbrlframes(self, frame='us-gaap', fact=None,
                   units='USD', cy=None, file=None):
        """xbrlframes(frame, fact, units, cy, file)

        aggregates one fact for each reporting entity that is
         last filed that most closely fits the calendrical period requested.
         This API supports for annual, quarterly and instantaneous data:
         frame - reporting frame e.g us-gaap, ifrs-full, dei, srt
         fact - fact to collect e.g AccountsPayableCurrent, USD-per-shares
         cy   - calendar year e.g. CY2023, CY2023Q1, CY2023Q4I
         only the I version seems to be available
         file - file to store the output
        """
        if not frame or not fact or not units or not cy:
            print('xbrlframes(frame, fact, units, cy)', file=sys.stderr)
            self.argp.print_help()
            sys.exit(1)
        # does not enforce legal dates yet
        cypat = '^CY[0-9]{4}([Q][1-4][I]?)?$'
        cyre  = re.compile(cypat)
        if cyre.match(cy) == None:
            print('xbrlframes: CY forms CY2023, cy2023Q1, or CY2023Q1I',
                  file=sys.stderr)
        if not file:
            file=os.path.join(self.odir, 'XBRLFrames.%s.%s.%s.%s.json' %
                  (frame, fact, units, cy))
        url = '%s/%s/%s/%s/%s.json' % (self.frurl, frame, fact, units, cy)
        resp = self.query(url)
        self.storequery(resp, file)

    def companyfactsarchivezip(self, file=None):
        """companyfactsearchzip(file)

        all the data from the XBRL Frame API
          and the XBRL Company Facts in a zip file
         file - file to store output
        """
        if not file:
            file=os.path.join(self.odir, 'companyfacts.zip')
        resp=self.query(self.cfzip)
        self.storequery(resp, file)

    def submissionszip(self, file=None):
        """submissionzip(file)

        public EDGAR filing history for all filers
        file - file to store output
        """
        if not file:
            file=os.path.join(self.odir, 'submissions.zip')
        resp=self.query(self.subzip)
        self.storequery(resp, file)

    def financialstatementandnotesdataset(self, cy=None, file=None):
        """ financialstatementandnotesdataset(cy, file)

        text summaries in a zip file
        cy - YYYYQ[1-4] from 2009-112020 YYYYMM after 11/2020
        file - file to store output
        """
        if not file:
            file=os.path.join(self.odir, 'fsan.zip')
        if 'CY' in cy or 'Q' in cy:
            if 'CY' in cy:
                cy = cy[2:]
            if 'Q' in cy:
                cya =  cy.split('Q')
            if len(cya) != 2 or int(cya[0]) > 2020 or int(cy[1]) > 4:
                print('financialstatementandnotesdataset cy in wrong format')
                sys.exit(1)
            url = '%s/%sq%s_notes.zip' % (self.fsanurl, cya[0],
                                          cya[1]) 
        else:
            assert int(cy), 'cy not an integer'
            now = datetime.datetime.now()
            if 'M' in cy:
                cya = cy.split('M')
            else:
                cya = [cy[0:4], cy[4:]]
            if int(cya[0]) < 2022 or int(cya[0]) > now.year:
                print('cy not a legal year', file=sys.stderr)
                sys.exit(1)
            if int(cya[1]) > 12:
                print('cy not a legal month', file=sys.stderr)
                sys.exit(1)
            y = cya[0]
            m = cya[1]
            url = '%s/%s_%s_notes.zip' % (self.fsanurl, y, m.zfill(2) )
        resp=self.query(url)
        self.storequery(resp, file)

# if __name__ == '__main__':
def main():
    EQ = EDGARquery()

    EQ.argp = argparse.ArgumentParser(description="query SEC EDGAR site\
        NOTE thæt EQEMAIL env variable is required and\
        must contain a valid User-Agent such as your email address")

    EQ.argp.add_argument("--cik", required=False,
        help="10-digit Central Index Key")
    EQ.argp.add_argument("--cy", required=False,
        help="calendar year e.g. CY2023, CY2023Q1, CY2023Q4I")

    EQ.argp.add_argument("--frame", required=False,
        help="reporting frame e.g us-gaap, ifrs-full, dei, srt")
    EQ.argp.add_argument("--units", required=False,
        default='USD', help="USD or shares")
    EQ.argp.add_argument("--fact", required=False,
        help="fact to collect e.g AccountsPayableCurrent, USD-per-shares")

    EQ.argp.add_argument("--file", required=False,
       help="file in which to store the output\n\
           argument allowed for each query type\n\
           defaults provided for each download in /tmp")

    EQ.argp.add_argument("--companyconcept",
       action='store_true', default=False,
       help="returns all the XBRL disclosures from a single company \n\
             --cik required\n\
             --frame - default us-gaap\n\
             --fact  - default USD-per-shares")
    EQ.argp.add_argument("--companyfacts",
       action='store_true', default=False,
       help="aggregates one fact for each reporting entity that is  \n\
         last filed that most closely fits the \n\
         calendrical period requested\n\
           --cik required")
    EQ.argp.add_argument("--xbrlframes",
       action='store_true', default=False,
       help="returns all the company concepts data for a CIK\n\
           --cy required")
    EQ.argp.add_argument("--companyfactsarchivezip",
       action='store_true', default=False,
       help="returns daily companyfacts index in a zip file")
    EQ.argp.add_argument("--submissionszip",
       action='store_true', default=False,
       help="returns daily index of submissions in a zip file")
    EQ.argp.add_argument("--financialstatementandnotesdataset",
       action='store_true', default=False,
       help="returns zip file with financial statement and notes summaries\n\
           --cy required")

    args = EQ.argp.parse_args()

    if not args.companyconcept and not args.companyfacts and \
       not args.xbrlframes and not args.companyfactsarchivezip and \
       not args.submissionszip and not args.financialstatementandnotesdataset:
        EQ.argp.print_help()
        sys.exit(1)

    # check for legal combination of arguments
    if (args.companyfacts and args.companyconcept):
        EQ.argp.print_help()
        sys.exit(1)
    if (args.companyfactsarchivezip and args.submissionszip):
        EQ.argp.print_help()
        sys.exit(1)
    if (args.cik and args.cy):
        EQ.argp.print_help()
        sys.exit(1)

    if args.companyconcept and not args.cik:
        EQ.argp.print_help()
        sys.exit(1)
    if args.companyconcept and args.cik and args.frame and args.fact:
        if args.file:
            EQ.companyconcept(cik=args.cik, frame=args.frame, fact=args.fact,
                        file=args.file)
            sys.exit()
        else:
            EQ.companyconcept(cik=args.cik, frame=args.frame, fact=args.fact)
            sys.exit()
    elif args.companyconcept and args.cik and args.fact:
        if args.file:
            EQ.companyconcept(cik=args.cik, fact=args.fact,
            file=args.file)
            sys.exit()
        else:
            EQ.companyconcept(cik=args.cik, fact=args.fact)
            sys.exit()
    elif args.companyconcept:
        if args.file:
            EQ.companyconcept(cik=args.cik, file=args.file)
            sys.exit()
        else:
            EQ.companyconcept(cik=args.cik)
            sys.exit()

    if args.xbrlframes and not args.cy:
        EQ.argp.print_help()
        sys.exit()
    if args.xbrlframes and args.frame and args.fact and args.units:
        EQ.xbrlframes(cy=args.cy, frame=args.frame, fact=args.fact,
                      units=args.units)
        sys.exit()
    elif args.xbrlframes and args.fact and args.units:
        EQ.xbrlframes(cy=args.cy, fact=args.fact, units=args.units)
        sys.exit()
    elif args.xbrlframes and args.fact:
        EQ.xbrlframes(cy=args.cy, fact=args.fact)
        sys.exit()
    elif args.xbrlframes:
        EQ.xbrlframes(cy=args.cy)
        sys.exit()

    if args.companyfacts and not args.cik:
        EQ.argp.print_help()
        sys.exit()
    if args.companyfacts and args.cik and args.file:
        EQ.companyfacts(cik=args.cik, file=args.file)
        sys.exit()
    elif args.companyfacts:
        EQ.companyfacts(cik=args.cik)
        sys.exit()

    if args.companyfactsarchivezip and args.file:
        EQ.companyfactsarchivezip(file=args.file)
        sys.exit()
    elif args.companyfactsarchivezip:
        EQ.companyfactsarchivezip()
        sys.exit()

    if args.submissionszip and args.file:
        EQ.submissionszip(file=args.file)
        sys.exit()
    elif args.submissionszip:
        EQ.submissionszip()
        sys.exit()

    if args.financialstatementandnotesdataset and not args.cy:
        EQ.argp.print_help()
        sys.exit()
    elif args.financialstatementandnotesdataset and args.file:
        EQ.financialstatementandnotesdataset(cy=args.cy,
        file=args.file)
        sys.exit()
    elif args.financialstatementandnotesdataset:
        EQ.financialstatementandnotesdataset(cy=args.cy)
        sys.exit()

if __name__ == '__main__':
    main()

