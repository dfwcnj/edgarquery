
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

import edgarquery


ES = edgarquery.submissions.EDGARSubmissions()

now = datetime.datetime.now()
year = now.year

argp = argparse.ArgumentParser(
          description='find the most recent submissions for cik')
argp.add_argument("--cik", required=True,
        help="10-digit Central Index Key")
argp.add_argument("--year", required=False,
    help="year to search for submissions if not current year")
argp.add_argument("--file", required=False,
    help="store the output in this file")

args = argp.parse_args()

if args.year: year = int(args.year)

ES.cik = args.cik
ES.searchformindices(args.cik, year)
ES.reportsubmissions(args.file)

