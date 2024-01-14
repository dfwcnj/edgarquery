# EDGAR query
# https://www.sec.gov/developer
# https://www.sec.gov/edgar/search-and-access
# https://www.sec.gov/edgar/sec-api-documentation
# https://www.sec.gov/edgar/search/
#

import os
import datetime
import sys
import argparse
from functools import partial
import shutil
import re
import urllib.request

# import xml
# import json
# for json files too large to process
# https://github.com/ICRAR/ijson
# import ijson

class EDGARquery():

    def __init__(self, cik=None, cy=None):
        'EDGARquery - search the SEC EDGAR site                          \
         --cik        - 10-digit Central Index Key                       \
         --cy         - calendar year e.g. CY2023, CY2023Q1, CY2023Q4I   \
         --tf         - file to store output                             \
        --companyconcept - company concept json file                     \
           --cik                                                         \
               leading 0s optional                                       \
           --frame - reporting frame, default us-gaap                    \
               e.g us-gaap, ifrs-full, dei, srt                          \
           --fact - fact to collect, default URS-per-shares              \
               e.g AccountsPayableCurrent, AccountsAndNotesReceivableNet \
           --tf - default /tmp/companyconcept.$frame.$fact.json          \
        or                                                               \
        --companyfacts - all the company concepts data for a company     \
            --cik                                                        \
            --tf - default /tmp/$cik.json                                \
        or                                                               \
        --xbrlframes Extensible Business Markup Language                 \
            --frame                                                      \
            --fact                                                       \
            --cy                                                         \
        or                                                               \
        --companyfactsearchzip - all the data from the XBRL Frame API    \
            and the XBRL Company Facts in a zip file                     \
            --tf - default /tmp/companyfact.zip                          \
        --submissionzip -  public EDGAR filing history for all filers    \
            --tf - default /tmp/submissions.zip                          \
        '
        self.cik        = cik
        self.cy         = cy

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

        self.tdir       = '/tmp'

        self.chunksize = 4194304
        self.argp      = None
        self.content   = None
        # self.hdr     = {'User-Agent' : os.environ['EQEMAILADDR'] }
        self.hdr       = None

        # xbrlframes is not yet well defined
        self.xfurl    = "https://data.sec.gov/api/xbrl/frames"

    def gency(self):
        'gency - generate a CY type I vslue for the previous quarter '
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
        'query - query an EDGAR URL             \
         url  - EDGAR URL to query - required  \
         not yet implemented \
        '
        try:
            req = urllib.request.Request(url, headers=self.hdr)
            resp = urllib.request.urlopen(req)
            return resp
        except urllib.error.URLError as e:
            print("Error %s(%s): %s" % ('query', url, e.reason),
            file=sys.stderr )
            sys.exit(1)

    def storequery(self, qresp, tf):
        'storequery - store the query response in a file \
        resp - the query response
        tf   - filename that will hold the query response
        '
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
            if c: f.write(c)
            return

    def companyconcept(self, cik=None, frame='us-gaap', fact=None, tf=None):
        'companyconcept - all xbrl disclosures for one company in JSON \
         cik             - 10-digit Central Index Key - required        \
         frame - reporting frame e.g us-gaap, ifrs-full, dei, srt            \
         fact - fact to collect e.g AccountsPayableCurrent   \
        '

        if not cik or not fact:
            print('companyconcept(frame, cik, fact)', file=sys.stderr)
            self.argp.print_help()
            sys.exit(1)

        if not tf:
            tf=os.path.abspath('%s/CompanyConcept.CIK%s.%s.%s.json' %
                (self.tdir, cik.zfill(10), frame, fact) )
        url = '%s/CIK%s/%s/%s.json' % (self.ccurl, cik.zfill(10), frame, fact)
        resp = self.query(url)
        self.storequery(resp, tf)

    def companyfacts(self, cik=None, tf=None):
        'companyfacts - all the company concepts data for a company   \
        cik - 10-digit Central Index Key required                     \
        '
        if not cik:
            print('companyfacts(cik)', file=sys.stderr)
            self.argp.print_help()
            sys.exit(1)

        if not tf:
            tf=os.path.abspath('%s/CompanyFacts.CIK%s.json' % (self.tdir,
                               cik.zfill(10)) )
        url = '%s/CIK%s.json' % (self.cfurl, cik.zfill(10))
        resp = self.query(url)
        self.storequery(resp, tf)

    def xbrlframes(self, frame='us-gaap', fact=None,
                   units='USD', cy=None, tf=None):
        'xbrlframes - aggregates one fact for each reporting entity that is  \
         last filed that most closely fits the calendrical period requested. \
         This API supports for annual, quarterly and instantaneous data:     \
         frame - reporting frame e.g us-gaap, ifrs-full, dei, srt            \
         fact - fact to collect e.g AccountsPayableCurrent, USD-per-shares   \
         cy   - calendar year e.g. CY2023, CY2023Q1, CY2023Q4I               \
         only the I version seems to be available                            \
        '
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
        if not tf:
            tf=os.path.abspath('%s/XBRLFrames.%s.%s.%s.%s.json' % (self.tdir,
                               frame, fact, units, cy))
        url = '%s/%s/%s/%s/%s.json' % (self.frurl, frame, fact, units, cy)
        resp = self.query(url)
        self.storequery(resp, tf)

    def companyfactsarchivezip(self, tf=None):
        'companyfactsearchzip - all the data from the XBRL Frame API \
            and the XBRL Company Facts in a zip file                 \
         tf - file to store output                                   \
        '
        if not tf:
            tf=os.path.abspath('%s/companyfacts.zip' % self.tdir )
        resp=self.query(self.cfzip)
        self.storequery(resp, tf)

    def submissionszip(self, tf=None):
        'submissionzip -  public EDGAR filing history for all filers \
         tf - file to store output                                   \
        '
        if not tf:
            tf=os.path.abspath('%s/submissions.zip' % self.tdir )
        resp=self.query(self.subzip)
        self.storequery(resp, tf)

def main():
    EQ = EDGARquery()

    EQ.argp = argparse.ArgumentParser(description="query SEC EDGAR site\
        NOTE thæt EQEMAILADDR env variable is required and\
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
    EQ.argp.add_argument("--tf", required=False,
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
       help="returns daily companyfacts index in a zip file\n\
           --cik required")
    EQ.argp.add_argument("--submissionszip",
       action='store_true', default=False,
       help="returns daily index of submissions in a zip file")

    args = EQ.argp.parse_args()

    try:
        EQ.hdr = {'User-Agent' : os.environ['EQEMAILADDR'] }
    except KeyError:
        print('EQEMAILADDR env variable required\n', file=sys.stderr)
        EQ.argp.print_help()
        sys.exit(1)

    if not args.companyconcept and not args.companyfacts and \
       not args.xbrlframes and not args.companyfactsarchivezip and \
       not args.submissionszip:
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
        if args.tf:
            EQ.companyconcept(cik=args.cik, frame=args.frame, fact=args.fact,
                        tf=args.tf)
            sys.exit()
        else:
            EQ.companyconcept(cik=args.cik, frame=args.frame, fact=args.fact)
            sys.exit()
    elif args.companyconcept and args.cik and args.fact:
        if args.tf:
            EQ.companyconcept(cik=args.cik, fact=args.fact, tf=args.tf)
            sys.exit()
        else:
            EQ.companyconcept(cik=args.cik, fact=args.fact)
            sys.exit()
    elif args.companyconcept:
        if args.tf:
            EQ.companyconcept(cik=args.cik, tf=args.tf)
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
    if args.companyfacts and args.cik and args.tf:
        EQ.companyfacts(cik=args.cik, tf=args.tf)
        sys.exit()
    elif args.companyfacts:
        EQ.companyfacts(cik=args.cik)
        sys.exit()

    if args.companyfactsarchivezip and not args.cik:
        EQ.argp.print_help()
        sys.exit()
    if args.companyfactsarchivezip and args.cik and args.tf:
        EQ.companyfactsarchivezip(tf=args.tf)
        sys.exit()
    elif args.companyfactsarchivezip and args.cik:
        EQ.companyfactsarchivezip()
        sys.exit()

    if args.submissionszip and args.tf:
        EQ.submissionszip(tf=args.tf)
        sys.exit()
    elif args.submissionszip:
        EQ.submissionszip()
        sys.exit()

main()

