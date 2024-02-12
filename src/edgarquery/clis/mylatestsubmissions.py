
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

from edgarquery import latestsubmissions

def main(*args, **kwarg):
    LT = edgarquery.latestsubmissions.EDGARLatestsubmissions()

    argp = argparse.ArgumentParser(
              description='find the most recent submissions for cik')
    argp.add_argument("--cik", required=True,
        help="10-digit Central Index Key")

    argp.add_argument('--file', help="json file to process")

    args = argp.parse_args()

    LT.cik = args.cik
    latest = LT.searchsubmissions(args.cik)

    if args.file:
        with open(file, w) as fp:
            print("'formtype','formurl'", file=fp)
            for k in latest.keys():
                if len(latest[k]) > 0:
                    print('%s\t%s' % (k, latest[k]), file=fp )
    else:
        for k in latest.keys():
            if len(latest[k]) > 0:
                print('%s\t%s' % (k, latest[k]) )

if __name__ == '__main__':
    main(*args, **kwarg)
