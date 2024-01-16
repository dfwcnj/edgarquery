#! /usr/bin/env python

#
# companyfactstocsv.py.py - parse sec edgar company facts json file for a CIK
#     company facts for a CIK seem to come in two parts so I have to
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

class EDGARCompanyFactstoCSV():

    def __init(self, jsonfile=None, odir='/tmp'):
        self.argp     = None
        self.jsonfile = jsonfile
        self.odir     = odir
        self.jsondict = None
        self.cik      = None
        self.enm      = None

        self.facttype = None
        self.factnm   = None
        self.label    = None
        self.descr    = None
        self.unit     = None

    # recurse over the json to show its structure
    def recdesc(self, js, ix):
        ' recdesc parse an SEC EDGAR company facts json file   \
          js - dictionary returned by python json.load()       \
          id - indent index to make the hierarchy more visible \
        '
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

    def jsonparts(self): # files seem to be in 2 parts
        ' jsonparts - traverse the top level json array \
          that I added to the SEC EDGAR file            \
        '
        assert type(self.jsondict) == type([]), 'jsonparts: js not an array'
        pts =  [p for p in self.jsondict]
        for pt in pts:
            self.jsonpart(pt)

    def jsonpart(self, pt):
        assert type(pt) == type({}), 'jsonpart: part not a dictionary'
        self.cik = pt['cik']
        self.enm = pt['entityName']
        self.jsonfacts(pt['facts'])

    def jsonfacts(self, facts):
        assert type(facts) == type({}), 'jsonfacts: facts not a dictionary'
        fka = [k for k in facts]
        for k in fka:
            self.facttype = k           # dei or us-gaap
            assert type(facts[k]) == type({}), \
                'jsonfacts: %s not a dictionary' % self.k
            fta = [ft for ft in facts[k]]
            for t in fta:
                self.factnm = t
                self.label = facts[k][t]['label']
                self.descr = facts[k][t]['description']
                assert type(facts[k][t]['units']) == type({}), \
                    'jsonfacts: units not a dictionary'
                uta = [u for u in facts[k][t]['units'] ]
                for ut in uta:
                    self.units = ut
                    assert type(facts[k][t]['units'][ut]) == type([]), \
                        'jasonfacts %s is not an array'
                    self.jsonfactcsv(facts[k][t]['units'][ut])

    def jsonfactcsv(self, recs):
        if '/' in self.units:
            self.units = re.sub('/', '', self.units)
            print('\t%s' % (self.units), file=sys.stderr)
        fn = ('%s/CompanyFacts.CIK%s.%s.%s.%s.csv' % (self.odir,
              self.cik, self.facttype, self.factnm, self.units) )
        # print('factparse: %s' % (fn), file=sys.stderr )
        try:
            with open(fn, 'w') as filep:
                print('end,val,accn,fy,fp,form,filed', file=filep)
                ca = [c for c in recs]
                for c in ca:
                    end   = c['end'];  val   = c['val']
                    accn  = c['accn']; fy    = c['fy']
                    fp    = c['fp'];   form  = c['form']
                    filed = c['filed']
                    rec = "'%s','%s','%s','%s','%s','%s','%s'" % (end, val,
                           accn, fy, fp, form, filed)
                    print(rec, file=filep)
        except Exception as e:
            print('%s %s: %s' % (self.jsonfile, fn, e), file=sys.stderr )
            sys.exit(1)

def main():
    EP = EDGARCompanyFactstoCSV()
    argp = argparse.ArgumentParser(description="Parse an SEC EDGAR\
        companyfacts json file after it has been altered to deal with its\
    multipart character and generate CSV files from its content")

    argp.add_argument('--file', help="json file to process")
    argp.add_argument('--odir', help="where to deposit the csv fileѕ",
                      default='/tmp')

    args = argp.parse_args()

    if not args.file:
        argp.print_help()
        sys.exit(11)
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

    EP.jsonparts()
    #EP.recdesc(jd, 1)


main()
