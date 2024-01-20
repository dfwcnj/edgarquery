#! /usr/bin/env python

#
# companyconcepttocsv.py.py.py - parse sec edgar companyconcept json file for a CIK
#     company concept for a CIK seem to come in two parts so I have to
#     edit the file to enclose its contents in brackets[] separateѕ by ,
#     otherwise the python json library excepts complaining about an extra
#     character when it finishes the first part and encounters the
#     second part
#

import os
import sys
import argparse
import json
import re

class EDGARCompanyConcepttoCSV():

    def __init(self, jsonfile=None, odir=None):

        self.argp     = None
        self.jsonfile = jsonfile
        if odir: self.odir = odir
        elif os.environ['EQODIR']: self.odir = os.environ['EQODIR']
        else: self.odir = '/tmp'
        self.jsondict = None
        self.cik      = None
        self.enm      = None

        self.facttype = None
        self.factnm   = None
        self.label    = None
        self.descr    = None
        self.units    = None

        self.of       = None

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

    def jsonparts(self, js):
        """ jsonparts - if the json was a single dictionary just process
           it or else traverse the top level json array
           that I added to the SEC EDGAR file
        """
        if type(self.jsondict) == type({}):
            self.jsonpart(self.jsondict)
        else:
            assert type(self.jsondict) == type([]), 'jsonparts: js not an array'
            pts =  [p for p in self.jsondict]
            for pt in pts:
                self.jsonpart(pt)

    def jsonpart(self, pt):
        assert type(pt) == type({}), 'jsonpart: part not a dictionary'
        self.cik = pt['cik']
        self.taxonomy = pt['taxonomy']
        self.tag = pt['tag']
        self.label = pt['label']
        self.enm = pt['entityName']
        self.units = pt['units']
        print('%s %s %s' % (self.enm, self.label, pt['description']) )
        # just one
        for k in pt['units'].keys():
            unit = k
        unit = re.sub('/', '', unit)
        # have to open the file here because the file contains two
        # json dictionaries
        ofn = '%s/CompanyConcept.CIK%s.%s.%s.%s.csv' % (self.odir, self.cik,
                                         self.tag, self.cik, unit)
        print(ofn)
        try:
            self.of = open(ofn, 'w')
            # csv header
            print('end,val,accn,fy,fp,form,filed', file=self.of)
        except Exception as e:
            print('open(%s) failed: e', (ofn, e) )
            sys.exit(1)
        self.jsonconceptcsv(self.units)

    def jsonconceptcsv(self, units):
        assert type(units) == type({}), 'jsonfacts: facts not a dictionary'
        ka = units.keys()
        for k in ka:
            assert type(units[k]) == type([]), 'jasonconcept units[%s] \
                                           not an array' % k
            for u in units[k]:
                assert type(u) == type({}), 'not a dictionary'
                print("'%s','%s','%s','%s','%s','%s','%s'" % (u['end'],
                      u['val'], u['accn'], u['fy'], u['fp'], u['form'],
                      u['filed']), file=self.of )


def main():
    EP = EDGARCompanyConcepttoCSV()
    argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
        companyconcepts json file after it has been altered to deal with its\
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



