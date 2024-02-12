
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
from functools import partial

from edgarquery import latest10K

def main(*args, **kwarg):
    LT = latest10K.EDGARLatest10K()

    argp = argparse.ArgumentParser(
              description='find the most recent 10-K for cik')
    argp.add_argument("--cik", required=True,
        help="10-digit Central Index Key")
    argp.add_argument("--link",
          action='store_true', default=False,
          help="return the url for the latest 10-K")
    argp.add_argument("--directory", help="directory to store the output")

    args = argp.parse_args()

    LT.cik = args.cik
    if args.directory:
        LT.search10K(args.cik, link=args.link, odir=args.directory)
    else:
        LT.search10K(args.cik, link=args.link)

if __name__ == '__main__':
    main(*args, **kwarg)
