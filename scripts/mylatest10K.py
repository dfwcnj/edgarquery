
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

import edgarquery

LT = edgarquery.latest10K.EDGARLatest10K()

argp = argparse.ArgumentParser(
          description='find the most recent 10-K for cik')
argp.add_argument("--cik", required=True,
    help="10-digit Central Index Key")
argp.add_argument("--link",
      action='store_true', default=False,
      help="return the url for the latest 10-K")

args = argp.parse_args()

LT.cik = args.cik
LT.search10K(args.cik, link=args.link)

