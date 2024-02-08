#! /usr/bin/env python

#
# xbrlframestocsv.py
#

import os
import sys
import argparse
import json

class EDGARXBRLFramestoCSV():

    def __init(self, jsonfile=None, odir=None):
        """ EDGARXBRLFramestoCSV

        parse sec edgar xbrl frame file for a CY
        frame for a CY seem to come in two parts so I have to
        the file to enclose its contents in brackets[] separateѕ by ,
        the python json library excepts complaining about an extra
        when it finishes the first part and encounters the second part
        """
        self.argp     = None
        self.jsonfile = jsonfile
        if odir: self.odir = odir # output directory
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.odir = os.path.abspath(self.odir)
        self.jsondict = None
        self.cy       = None
        self.enm      = None

        self.taxonomy = None
        self.tag   = None
        self.ccp   = None
        self.uom   = None
        self.label    = None
        self.descr    = None
        self.unit     = None

    # recurse over the json to show its structure
    def recdesc(self, js, ix):
        """ recdesc(js, ix)

        parse an SEC EDGAR company facts json file
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

    def jsonparts(self, js):
        """jsonparts(js)

        traverse the top level json array that I added to the SEC EDGAR file
        this may no longer be necessary
        js - json file whose top level structure is an array
        """
        if type(self.jsondict) == type({}):
            self.jsonpart(self.jsondict)
        else:
            assert type(self.jsondict) == type([]), 'jsonparts: js not an array'
            pts =  [p for p in self.jsondict]
            for pt in pts:
                self.jsonpart(pt)

    def jsonpart(self, pt):
        """ jsonpart(pt)

        parse the xbrl frames json data
        pt - the json to parse
        """
        assert type(pt) == type({}), 'jsonpart: part not a dictionary'
        self.cy = pt['ccp']
        self.taxonomy = pt['taxonomy']
        self.tag = pt['tag']
        self.label = pt['label']
        self.uom = pt['uom']
        print('%s %s %s' % (self.cy, self.label, pt['description']) )
        # have to open the file here because the file contains two
        # json dictionaries
        ofn = os.path.join(self.odir, 'XBRLFrame.%s.%s.%s.%s.csv' % (self.cy,
                                     self.tag, self.taxonomy, self.uom) )
        print(ofn)
        try:
            self.of = open(ofn, 'w')
            # csv header

            print('accn,cik,entityName,loc,end,val', file=self.of)
        except Exception as e:
            print('open(%s) failed: e', (ofn, e) )
            sys.exit(1)
        self.jsonxbrlframecsv(pt['data'])

    def jsonxbrlframecsv(self, data):
        """ jsonxbrlframecsv(data)

        write the xbrl frames data to a csv file
        data - contents of the xbrl frames json 'data' key
        """
        assert type(data) == type([]), 'xbrlframes: data not a array'
        for d in data:
            assert type(d) == type({}), 'xbrlframes: datum not a dictionay'
            print("'%s','%s','%s','%s','%s','%s'" % (d['accn'], d['cik'],
                                        d['entityName'], d['loc'],
                                        d['end'], d['val']), file=self.of )



if __name__ == '__main__':
    def main():
        EP = EDGARXBRLFramestoCSV()
        argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
            xbrlframes json file after it has been altered to deal with its\
        multipart character and generate a csv file from its contents")

        argp.add_argument('--file', help="json file to process")
        argp.add_argument('--odir', help="where to deposit the fileѕ",
                          default='/tmp')

        args = argp.parse_args()

        if not args.file:
            argp.print_help()
            sys.exit(1)
        EP.argp = argp
        if args.odir: EP.odir = args.odir

        EP.jsonfile = args.file
        try:
            with open(args.file, 'r') as f:
                jd = json.load(f)
                EP.jsondict = jd
        except Error as e:
            print('%s parse failed' % args.file)
            sys.exit(1)

        EP.jsonparts(jd)
        #EP.recdesc(jd, 1)

    main()

