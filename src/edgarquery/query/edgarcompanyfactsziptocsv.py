#! env python

import os
import sys
import argparse
import json
import zipfile

class EDGARCompanyFactsziptoCSV():

    def __init__(self, zipfile=None, odir=None):
        self.zipfile = zipfile    # zip filename
        self.zfo     = None       # zip file object
        if odir: self.odir = odir  # output directory
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.odir = os.path.abspath(self.odir)
        self.argp    = None       # argument parser
        self.js      = None       # json object
        self.ziplist = None       # list of files in zip file

    # recurse over the json to show its structure
    def recdesc(self, js, ix):
        """ recdesc parse an SEC EDGAR company facts json file   \
          js - dictionary returned by python json.load()       \
          id - indent index to make the hierarchy more visible \
        """
        ind = ' ' * ix
        if type(js) == type([]): # array
            print('    type array')
            da = [d for d in js]
            for d in da:
                self.recdesc(d, ix+1)
        elif type(js) == type({}): # dictionary
            print('    type dictionary')
            for k in js.keys():
                print('%s key: %s' % (ind, k))
                self.recdesc(js[k], ix+1)
        else:
            print('%s value: %s' % (ind, js))             # value
            return

    def listzip(self):
        self.ziplist = self.zfo.namelist()
        # self.ziplist.sort() # order may be important
        return

    def zipread(self, file):
        return self.zfo.read(file)


def main():
    ES = EDGARCompanyFactsziptoCSV()
    argp = argparse.ArgumentParser(description='Extract one or more json\
    files from an SEC EDGAR companyfacts.zip file and convert to CSV')

    argp.add_argument('--zipfile', help="submissions.zip file to process\
     - required")
    argp.add_argument('--odir', help="where to deposit the output",
                      default='/tmp')
    argp.add_argument('--files', help="comma separates(no spaces) content\
                                 file(s) to process")
    argp.add_argument('--all', action='store_true', default=False,
        help="process all submissions.zip files")
    argp.add_argument('--combine', action='store_true', default=False,
        help="combine all submissions.zip files into one csv file")


    args = argp.parse_args()

    if not args.zipfile:
        argp.print_help()
        sys.exit(1)
    ES.argp = argp
    if args.odir: ES.odir = args.odir

    try:
        with zipfile.ZipFile(args.zipfile, mode='r') as ES.zfo:
            ES.zipfile = args.zipfile
            ES.listzip()

            js = json.loads(ES.zipread('CIK0001099219.json') )
            ES.recdesc(js, 1)

            if args.files:
                if ',' in args.files:
                    fa = args.files.split(',')

            pass

    except zipfile.BadZipfile as e:
       print('open %s: %s', (args.zipfile, e) )
       sys.exit(1)


main()
