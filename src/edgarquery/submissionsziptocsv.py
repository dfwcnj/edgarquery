#! /usr/bin/env python3

import os
import sys
import argparse
import json
import zipfile

class EDGARSubmissionsziptoCSV():

    def __init__(self, zipfile=None, odir=None):
        self.zipfile = zipfile    # zip filename
        self.zfo     = None       # zip file object
        if odir: self.odir = odir # output directory
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.argp    = None       # argument parser
        self.js      = None       # json object
        self.ziplist = None       # list of files in zip file

        self.hdr   = "'cik','company','filingDate','reportDate','acceptanceDateTime','act','form','fileNumber','filmNumber','items','size','isXBRL','isInlineXBRL','primaryDocument','primaryDocDescription'"

    # recurse over the json to show its structure
    def recdesc(self, js, ix):
        """ recdesc parse an SEC EDGAR company facts json file   \
          js - dictionary returned by python json.load()       \
          ix - indent index to make the hierarchy more visible \
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
        """listzip - collect the list of json files in the zip file"""
        self.ziplist = self.zfo.namelist()
        # self.ziplist.sort() # order may be important
        return

    def zipread(self, file):
        """zipread - return the contents of file in the zipfile\n\
         file - name of the file to read
        """
        return self.zfo.read(file)

    def jstocsv(self, js, ofp, hdr=None):
        """jstocsv - extract js contents to a csv file\n\
         js  - json dictionary to convert\n\
         fp  - file object to contain the csv\n\
         hdr - header of column labels\n\
         NOTE: not all of the top level data is extracted
        """
        if not js or not ofp:
            self.argp.print_help()
            sys.exit(1)
        assert type(js) == type({}), 'jstocsv: js is not a dictionary'

        cik   = js['cik']

        name  = js['name']
        fgs   = js['filings']['recent']

        ann   = fgs['accessionNumber']
        fda   = fgs['filingDate']
        rda   = fgs['reportDate']
        adta  = fgs['acceptanceDateTime']
        aa    = fgs['act']
        fa    = fgs['form']
        fna   = fgs['fileNumber']
        fmna  = fgs['filmNumber']
        ita   = fgs['items']
        sza   = fgs['size']
        isXa  = fgs['isXBRL']
        isiXa = fgs['isInlineXBRL']
        pda   = fgs['primaryDocument']
        pdda  = fgs['primaryDocDescription']

        if hdr: print(hdr, file=ofp)
        for i in range(len(ann)-1 ):
            str='%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % \
                  (cik, name, ann[i], rda[i], adta[i], aa[i], fa[i], fna[i],
                  fmna[i], ita[i], sza[i], isXa[i], isiXa[i], pda[i], pdda[i])
            print(str, file=ofp)


    def sometocsv(self, fa):
        """sometocsv - convert list of json files from zip file to csv\n\
         fa - list containing files to convert\n\
         NOTE: not all of the top level data is extracted\n\
         NOTE there will one csv file per json file\n\
         NOTE json files containing the string "submission" are skipped
        """
        for f in fa:
            # not sure how these json file fit in here
            if 'submission' in f:
                pass
            jsstr=self.zipread(f).decode("utf-8") 
            js = json.loads(jsstr)
            # json filename is $cik.json
            jn = '%s/submissions.%s.csv' % (self.odir, f.split('.')[0])
            try:
                with open(jn, 'w') as fp:
                    self.jstocsv(js, ofp=fp, hdr=self.hdr)
            except Exception as e:
                print('%s: %s' % (jn, e) )
                sys.exit(1)

    def combinesometocsv(self, fa, fn):
        """combineseometocsv - convert json files into one large csv file\n\
         fa - list of json files to convert\n\
         fn - name of file that will contain the csv\n\
         NOTE: not all of the top level data is extracted\n\
         NOTE json files containing the string "submission" are skipped
        """
        try:
            with open(fn, 'w') as fp:
                print(self.hdr, file=fp)
                for f in fa:
                    if 'submission' in f:
                        pass
                    jsstr=self.zipread(f).decode("utf-8") 
                    js = json.loads(jsstr)
                    self.jstocsv(js, ofp=fp)

        except Exception as e:
            print('%s: %s' % (fn, e), file=sys.stderr )
            sys.exit(1)

def main():
    'EDGARSubmissionsziptoCSV - convert json files in submissions.zip\n\
     to csv\n\
     --zipfile - path to the submissions.zip file\n\
     --odir    - directory to store the output, default /tmp\n\
     --files   - name(s) of json file to convert\n\
     --all     - process all json files(w/o submission in name)\n\
     --combine - combine csvs into one file'
    ES = EDGARSubmissionsziptoCSV()
    argp = argparse.ArgumentParser(description='Extract one or more json\
    files from an SEC EDGAR submissions.zip file and convert to CSV')

    argp.add_argument('--zipfile', help="submissions.zip file to process\
     - required")
    argp.add_argument('--odir', help="where to deposit the output",
                      default='/tmp')
    argp.add_argument('--files', help="comma separated(no spaces) content\
                                 file(s) to process")
    argp.add_argument('--all', action='store_true', default=False,
                      help="process all submissions.zip files")
    argp.add_argument('--combine', action='store_true', default=False,
                      help="convert all/some submissions.zip json\
                                   files into one csv file")

    args = argp.parse_args()

    if not args.zipfile:
        argp.print_help()
        sys.exit(1)

    ES.argp = argp
    if args.odir: ES.odir = args.odir
    elif os.environ['EQODIR']: ES.odir = os.environ['EQODIR']

    try:
        with zipfile.ZipFile(args.zipfile, mode='r') as ES.zfo:
            ES.zipfile = args.zipfile
            ES.listzip()

            if args.all and args.combine:
                ES.combinesometocsv(ES.ziplist,
                    fn='%s/allsubmissions.csv' % (ES.odir))
                sys.exit(0)
            elif args.all:
                ES.sometocsv(self.ziplist)
                sys.exit(0)

            if args.files:
                if ',' in args.files:
                    fa = args.files.split(',')
                else: fa = [args.files]
                if args.combine:
                    ES.combinesometocsv(fa,
                    fn='%s/somesubmissions.csv' % (ES.odir))
                    sys.exit(0)
                else:
                    ES.sometocsv(fa)
                    sys.exit(0)

    except zipfile.BadZipfile as e:
       print('open %s: %s', (args.zipfile, e) )
       sys.exit(1)


main()
