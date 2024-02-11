
#! /usr/bin/env python

#
# EDGARXBRLFramestoCSV
#

import os
import sys
import argparse
import json

import edgarquery

EP = edgarquery.xbrlframestocsv.EDGARXBRLFramestoCSV()

argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
    xbrlframes json file after it has been altered to deal with its\
multipart character and generate a csv file from its contents")

argp.add_argument('--file', help="json file to process")
argp.add_argument('--odir', help="where to deposit the fileѕ",
                  default='/tmp')

args = argp.parse_args()

if not args.file:
    argp.print_help()
    sys.exit(1)
EP.argp = argp
if args.odir: EP.odir = args.odir

EP.jsonfile = args.file
try:
    with open(args.file, 'r') as f:
        jd = json.load(f)
        EP.jsondict = jd
except Error as e:
    print('%s parse failed' % args.file)
    sys.exit(1)

EP.jsonparts(jd)


