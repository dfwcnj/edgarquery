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
    from edgarquery import edgarlatestsubmission
    from edgarquery import tickerd
except ImportError as e:
    import edgarlatestsubmission
    import tickerd


def main():
    LS = edgarlatestsubmission.EDGARLatestSubmission()

    argp = argparse.ArgumentParser(
              description='find the most recent 10-K for ticker or cik')
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
        cik = LS.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys.exit()

    LS.searchSubmission(cik, '10-K', args.link, args.directory, args.show)

if __name__ == '__main__':
    main()
