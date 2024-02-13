
#! /usr/bin/env python

#
# EDGARXBRLFramestoCSV
#

import sys
import argparse
import json

from edgarquery import xbrlframestocsv

def main():
    EP = xbrlframestocsv.EDGARXBRLFramestoCSV()

    argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
        xbrlframes json file after it has been altered to deal with its\
    multipart character and generate a csv file from its contents")

    argp.add_argument('--file', required=True,
          help="json file to process")
    argp.add_argument('--directory', help="where to deposit the fileѕ",
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

    EP.jsonparts(jd, odir=args.directory)

if __name__ == '__main__':
    main()
