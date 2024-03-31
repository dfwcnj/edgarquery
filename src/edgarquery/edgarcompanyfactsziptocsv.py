#! env python

#
# EDGARCompanyFactsziptoCSV
#

import os
import sys
import argparse
import json
import zipfile

class EDGARCompanyFactsziptoCSV():

    def __init__(self, zipfile=None, directory=None):
        """ EDGARCompanyFactsziptoCSV

        convert the contents of a submissions.zip file retrieved from
        the SEC FRED site and convert to csv
        XXX finish me
        """
        self.zipfile = zipfile    # zip filename
        self.zfo     = None       # zip file object
        self.js      = None       # json object
        self.ziplist = None       # list of files in zip file

    # recurse over the json to show its structure
    def recdesc(self, js, ix):
        """ recdesc(js, ix) show structure of a json file
        parse an SEC EDGAR company facts json file   \
        js - dictionary returned by python json.load()       \
        id - indent index to make the hierarchy more visible \
        """
        ind = '  ' * ix
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
        """listzip() - collect name list of zip file"""
        self.ziplist = self.zfo.namelist()
        # self.ziplist.sort() # order may be important
        return

    def zipread(self, file):
        """zipread(file) return contents of file in a zip file

        file - name of file to read
        """
        return self.zfo.read(file)

    def jstocsv(self, js, directory):
        """jstocsv(js)

        extract js contents to csv files
        NOTE: not all of the top level data is extracted
        js  - json dictionary to convert
        directory - directory to output the json csv file
        """
        if not directory: directory = self.directory
        assert type(js) == type({}), 'jstocsv: js is not a dictionary'

        # json filename is $cik.json
        ncik = '%s' % (js['cik'])
        cik = 'CIK%s' % (ncik.zfill(10) )
        entityName = js['entityName']
        fta = js['facts'].keys()
        for ft in fta:
            fna = js['facts'][ft].keys()
            for fn in fna:
                lbl = js['facts'][ft][fn]['label']
                #descr = js['facts'][ft][fn]['description']
                units = js['facts'][ft][fn]['units']
                unit = None
                for k in units.keys():
                    unit = k
                if '/' in unit:
                    unit = ''.join(unit.split('/') )
                fnm = '%s_%s_%s_facts.csv' % (cik, fn, unit)
                jn = os.path.join(directory, fnm)
                with open(jn, 'w') as fp:
                    ha = []
                    for fact in js['facts'][ft][fn]['units'][unit]:
                        if len(ha) == 0:
                            for n in fact.keys():
                                ha.append("'%s'," % (n) )
                            print(''.join(ha), file=fp )
                        ra = []
                        for n in fact.keys():
                            ra.append("'%s'," % (fact[n]) )
                        print(''.join(ra), file=fp )




    def sometocsv(self, fa):
        """sometocsv(fa)

        convert list of json files from zip file to csv\n\
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
            #self.recdesc(js, ix=1)
            self.jstocsv(js, directory)


def main():
    ES = EDGARCompanyFactsziptoCSV()
    argp = argparse.ArgumentParser(description='Extract one or more json\
    files from an SEC EDGAR companyfacts.zip file and convert to CSV')

    argp.add_argument('--zipfile', required=True,
        help="submissions.zip file to process. Іt can be downloadæd\
            with edgarquery.query")
    argp.add_argument('--directory', help="where to deposit the output",
                      default='/tmp')
    argp.add_argument('--files', help="comma separated(no spaces) content\
                                 file(s) to process a subset of\
                                 the files in the zip file")

    args = argp.parse_args()

    try:
        with zipfile.ZipFile(args.zipfile, mode='r') as ES.zfo:
            ES.zipfile = args.zipfile

            if args.files:
                if ',' in args.files:
                    fa = args.files.split(',')
            else:
                ES.listzip()
                fa = ES.ziplist

            ES.sometocsv(fa, directory=args.directory)

    except zipfile.BadZipfile as e:
       print('open %s: %s', (args.zipfile, e) )
       sys.exit(1)

if __name__ == '__main__':
    main()
