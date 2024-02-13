
import sys
import argparse
from edgarquery import tickerstocsv

def main():

    argp = argparse.ArgumentParser(description="collect EDGAR\
    companyticker json files and convert them to csv")

    argp.add_argument('--file', required=False, help="json file to process")
    argp.add_argument('--directory', default='/tmp',
                help="where to deposit the fileѕ")

    args = argp.parse_args()

    tc = tickerstocsv.EDGARTickerstoCSV()

    tc.urljstocsv(odir=args.directory)

if __name__ == '__main__':
    main()
