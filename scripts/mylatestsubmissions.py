
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

import edgarquery


LT = edgarquery.latestsubmissions.EDGARLatestsubmissions()

argp = argparse.ArgumentParser(
          description='find the most recent submissions for cik')
argp.add_argument("--cik", required=True,
    help="10-digit Central Index Key")

args = argp.parse_args()

LT.cik = args.cik
latest = LT.searchsubmissions(args.cik)
for k in latest.keys():
    if len(latest[k]) > 0:
        print('%s\t%s' % (k, latest[k]) )
