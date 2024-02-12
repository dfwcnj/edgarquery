
#! /usr/bin/env python

#
# EDGARCompanyFactstoCSV
#

import os
import sys
import argparse
import json
import re

from edgarquery import companyfactstocsv


def main(*args, **kwarg):
    EP = companyfactstocsv.EDGARCompanyFactstoCSV()
    argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
        companyfacts json file after it has been altered to deal with its\
    multipart character and generate CSV files from its content")

    argp.add_argument('--file', required=True,
                help="json file to process")
    argp.add_argument('--odir', help="where to deposit the csv fileѕ",
                      default='/tmp')

    args = argp.parse_args()

    EP.jsonfile = args.file
    try:
        with open(args.file, 'r') as f:
            jd = json.load(f)
            EP.jsondict = jd
    except Error as e:
        print('%s parse failed' % args.file)
        sys.exit(1)

    if args.odir:
        EP.jsonparts(args.file, odir=args.odir)
    else:
        EP.jsonparts(args.file)
    #EP.recdesc(jd, 1)


if __name__ == '__main__':
    main(*args, **kwarg)
