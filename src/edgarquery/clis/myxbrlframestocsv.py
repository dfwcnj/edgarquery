
#! /usr/bin/env python

#
# EDGARXBRLFramestoCSV
#

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

    EP.argp = argp
    if args.odir: EP.odir = args.directory

    EP.jsonfile = args.file
    try:
        with open(args.file, 'r') as f:
            jd = json.load(f)
            EP.jsondict = jd
    except Error as e:
        print('%s parse failed' % args.file)
        sys.exit(1)

    EP.jsonparts(jd)

if __name__ == '__main__':
    main()
