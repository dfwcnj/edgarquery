
#! /usr/bin/env python

#
# EDGARCompanyFactstoCSV
#

import sys
import argparse
import json

from edgarquery import companyfactstocsv


def main():
    EP = companyfactstocsv.EDGARCompanyFactstoCSV()
    argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
        companyfacts json file after it has been altered to deal with its\
    multipart character and generate CSV files from its content")

    argp.add_argument('--file', required=True,
                help="json file to process")
    argp.add_argument('--directory', help="where to deposit the csv fileѕ",
                      default='/tmp')

    args = argp.parse_args()

    EP.jsonfile = args.file
    try:
        with open(args.file, 'r') as f:
            jd = json.load(f)
            EP.jsondict = jd
    except OSError as e:
        print('%s parse failed' % args.file)
        sys.exit(1)

    if args.directory:
        EP.jsonparts(odir=args.directory)
    else:
        EP.jsonparts()
    #EP.recdesc(jd, 1)


if __name__ == '__main__':
    main()
