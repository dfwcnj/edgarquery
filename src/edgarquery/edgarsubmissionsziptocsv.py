#! /usr/bin/env python3

#
# EDGARSubmissionsziptoCSV
#

import os
import sys
import argparse
import json
import zipfile

class EDGARSubmissionsziptoCSV():

    def __init__(self, zipfile=None):
        """ EDGARSubmissionsziptoCSV

        export the contents of the submissions.zip file retrieved from
        SEC to csv files
        """
        self.zipfile = zipfile    # zip filename
        self.zfo     = None       # zip file object

        #self.hdr   = "'cik','company','filingDate','reportDate','acceptanceDateTime','act','form','fileNumber','filmNumber','items','size','isXBRL','isInlineXBRL','primaryDocument','primaryDocDescription'"

    # recurse over the json to show its structure
    def recdesc(self, js, ix):
        """ recdesc(js, ix)

        recdesc parse an SEC EDGAR company facts json file
        js - dictionary returned by python json.load()
        ix - indent index to make the hierarchy more visible
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
        ziplist =  self.zfo.namelist()
        # ziplist.sort() # order may be important
        return ziplist

    def zipread(self, file):
        """zipread - return the contents of file in the zipfile
         file - name of the file to read
        """
        return self.zfo.read(file)

        #self.hdr   = "'cik','company','filingDate','reportDate','acceptanceDateTime','act','form','fileNumber','filmNumber','items','size','isXBRL','isInlineXBRL','primaryDocument','primaryDocDescription'"

    def jstocsv(self, js, directory):
        """jstocsv(js)

        extract js contents to a csv file
        NOTE: not all of the top level data is extracted
        js  - json dictionary to convert
        """
        if not js:
            print('zipread: js argument required', file=sys.stderr)
            sys.exit(1)
        assert type(js) == type({}), 'jstocsv: js is not a dictionary'

        cik   = 'CIK%s' % (js['cik'].zfill(10) )
        name  = js['name']
        slen = 0
        fgs   = js['filings']['recent']
        ofn = os.path.join(directory, 'submissions.%s.csv' % (cik) )
        with open(ofn, 'w') as ofp:
            ha = ["'cik',", "'name'"]
            for k in fgs.keys():
                if slen == 0:
                    slen = len(fgs[k])
                    print('slen: %d' % slen)
                ha.append("'%s'," % (k) )

            print(''.join(ha), file=ofp)
            for i in range(slen-1):
                ra = ["'%s'," % cik, "'%s'," % name]
                for k in fgs.keys():
                    ra.append("'%s'," % (fgs[k][i]) )
                print(''.join(ra), file=ofp)


    def sometocsv(self, fa, directory):
        """sometocsv(fa)

        convert list of json files from zip file to csv
        fa - list containing files to convert
        NOTE: not all of the top level data is extracted
        NOTE there will one csv file per json file
        NOTE json files containing the string "submission" are skipped
        """
        for f in fa:
            # not sure how these json file fit in here
            if 'submission' in f:
                pass
            jsstr=self.zipread(f).decode("utf-8") 
            js = json.loads(jsstr)
            self.jstocsv(js, directory)

# if __name__ == '__main__':
def main():
    """EDGARSubmissionsziptoCSV - convert json files in submissions.zip
     to csv
     --zipfile - path to the submissions.zip file
     --directory    - directory to store the output, default /tmp
     --files   - name(s) of json file to convert
     if --files not supplied, process all files in the zip file
    """
    ES = EDGARSubmissionsziptoCSV()
    argp = argparse.ArgumentParser(description='Extract one or more json\
    files from an SEC EDGAR submissions.zip file and convert to CSV')

    argp.add_argument('--zipfile', help="submissions.zip file to process\
     - required")
    argp.add_argument('--directory', help="where to deposit the output",
                      default='/tmp')
    argp.add_argument('--files', help="comma separated(no spaces) content\
                                 file(s) to process a subset of the\
                                 files in the zip file")

    args = argp.parse_args()

    if not args.zipfile:
        argp.print_help()
        sys.exit(1)

    ES.argp = argp

    try:
        with zipfile.ZipFile(args.zipfile, mode='r') as ES.zfo:
            ES.zipfile = args.zipfile
            ES.listzip()

            if args.files:
                if ',' in args.files:
                    fa = args.files.split(',')
            else:
                fa = ES.listzip()

            ES.sometocsv(fa, directory=args.directory)

    except zipfile.BadZipfile as e:
       print('open %s: %s', (args.zipfile, e) )
       sys.exit(1)

if __name__ == '__main__':
    main()
