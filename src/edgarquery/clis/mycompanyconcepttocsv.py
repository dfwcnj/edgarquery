
#! /usr/bin/env python

#
# EDGARCCompanyConcept
#     second part
#

import os
import sys
import argparse
import json
import re

from edgarquery import companyconcepttocsv

def main(*args, **kwarg):
    EP = companyconcepttocsv.EDGARCompanyConcepttoCSV()
    argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
        companyconcepts json file after it has been altered to deal\
        with its multipart character and generate a csv file from \
        its contents")

    argp.add_argument('--file', required=True,
               help="json file to process")
    argp.add_argument('--odir', help="where to deposit the fileѕ",
                      default='/tmp')

    args = argp.parse_args()

    if args.odir: EP.odir = args.odir

    EP.jsonfile = args.file
    try:
        with open(args.file, 'r') as f:
            jd = json.load(f)
            EP.jsondict = jd
    except Error as e:
        print('%s parse failed' % args.file)
        sys.exit(1)

    EP.jsonparts(jd, odir=args.odir)
    #EP.recdesc(jd, 1)

if __name__ == '__main__':
    main(*args, **kwarg)

