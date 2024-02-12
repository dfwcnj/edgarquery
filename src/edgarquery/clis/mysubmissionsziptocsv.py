
#! /usr/bin/env python3

#
# EDGARSubmissionsziptoCSV
#

import argparse
import zipfile

from edgarquery import submissionsziptocsv

def main():
    ES = submissionsziptocsv.EDGARSubmissionsziptoCSV()
    argp.add_argument('--zipfile', required=True,
        help="submissions.zip file to process - required")
    argp.add_argument('--odir', help="where to deposit the output",
                  default='/tmp')
    argp.add_argument('--files', help="comma separated(no spaces) content\
                             file(s) to process a subset of the\
                             files in the zip file")

    args = argp.parse_args()

    ES.argp = argp
    if args.odir: ES.odir = args.odir
    elif os.environ['EQODIR']: ES.odir = os.environ['EQODIR']

    try:
        with zipfile.ZipFile(args.zipfile, mode='r') as ES.zfo:
            ES.zipfile = args.zipfile
            ES.listzip()

            if args.files:
                if ',' in args.files:
                    fa = args.files.split(',')
            else:
                ES.listzip()
                fa = ES.ziplist

            ES.sometocsv(fa)

    except zipfile.BadZipfile as e:
       print('open %s: %s', (args.zipfile, e) )
       sys.exit(1)

if __name__ == '__main__':
    main()
