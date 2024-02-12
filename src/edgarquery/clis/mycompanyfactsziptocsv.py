
#! env python

#
# EDGARCompanyFactsziptoCSV
#

import argparse
import zipfile

from edgarquery import companyfactsziptocsv


def main():
    ES = companyfactsziptocsv.EDGARCompanyFactsziptoCSV()

    argp = argparse.ArgumentParser(description='Extract one or more json\
    files from an SEC EDGAR companyfacts.zip file and convert to CSV')

    argp.add_argument('--zipfile', required = True,
        help="submissions.zip file to process - required")
    argp.add_argument('--odir', help="where to deposit the output",
                      default='/tmp')
    argp.add_argument('--files', help="comma separated(no spaces) content\
                                 file(s) to process a subset of\
                                 the files in the zip file")

    args = argp.parse_args()

    if not args.zipfile:
        argp.print_help()
        sys.exit(1)
    ES.argp = argp
    if args.odir: ES.odir = args.odir

    try:
        with zipfile.ZipFile(args.zipfile, mode='r') as ES.zfo:
            ES.zipfile = args.zipfile

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
