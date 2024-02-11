
# EDGAR query

import os
import datetime
import sys
import argparse
from functools import partial
import re
import urllib.request

import edgarquery


def main():
    EQ = edgarquery.doquery.EDGARquery()

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

    if args.companyfactsarchivezip and args.tf:
        EQ.companyfactsarchivezip(tf=args.tf)
        sys.exit()
    elif args.companyfactsarchivezip:
        EQ.companyfactsarchivezip()
        sys.exit()

    if args.submissionszip and args.tf:
        EQ.submissionszip(tf=args.tf)
        sys.exit()
    elif args.submissionszip:
        EQ.submissionszip()
        sys.exit()

    if args.financialstatementandnotesdataset and not args.cy:
        EQ.argp.print_help()
        sys.exit()
    elif args.financialstatementandnotesdataset and args.tf:
        EQ.financialstatementandnotesdataset(cy=args.cy, tf=args.tf)
        sys.exit()
    elif args.financialstatementandnotesdataset:
        EQ.financialstatementandnotesdataset(cy=args.cy)
        sys.exit()

main()

