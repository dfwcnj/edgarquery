#! /usr/bin/env python

#
# EDGARCompanyFactstoCSV
#

import os
import sys
import argparse
import json
import re

class EDGARCompanyFactstoCSV():

    def __init(self, jsonfile=None):
        """ EDGARCompanyFactstoCSV

        parse sec edgar company facts json file for a CIK
        facts for a CIK seem to come in two parts so I have to
        the file to enclose its contents in brackets[] separateѕ by ,
        the python json library excepts complaining about an extra
        when it finishes the first part and encounters the
        part
        """
        self.jsonfile = jsonfile
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
        """ recdesc(js, ix)

        parse an SEC EDGAR company facts json file   \
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

    def jsonparts(self, directory): # files seem to be in 2 parts
        """ jsonparts

        if the json file was just one dictionary
        just traverse the dictionary or else
        traverse the top level json array
        that I added to the SEC EDGAR file
        directory - directory for the output
        """
        if type(self.jsondict) == type({}):
            self.jsonpart(self.jsondict, directory)
        else:
            type(self.jsondict) == type([]), 'jsonparts: js not an array'
            pts =  [p for p in self.jsondict]
            for pt in pts:
                self.jsonpart(js=pt, directory=directory)

    def jsonpart(self, js, directory):
        """ jsonpart(js)

        js - json to parse
        directory - directory for the output
        """
        assert type(js) == type({}), 'jsonpart: part not a dictionary'
        self.cik = js['cik']
        self.enm = js['entityName']
        self.jsonfacts(facts=js['facts'], directory=directory)

    def jsonfacts(self, facts, directory):
        """ jsonfacts(facts) parse companyfacts json file

        facts - json file containing SEC EDGAR companyfacts
        directory - directory for the output
        """
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
                    self.jsonfactcsv(recs=facts[k][t]['units'][ut],
                        directory=directory)

    def jsonfactcsv(self, recs, directory):
        """ jsonfactcsv(recs) - dump company facts file to csv

        recs - individual company facts
        directory - directory for the output
        """
        if '/' in self.units:
            self.units = re.sub('/', '', self.units)
            print('\t%s' % (self.units), file=sys.stderr)
        fn = os.path.join(directory,
             'CompanyFacts.CIK%s_%s_%s_%s.csv' % ( self.cik, self.facttype,
                                                   self.factnm, self.units) )
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

    argp.add_argument('--file', required=True,
                help="json file to process")
    argp.add_argument('--directory', help="where to deposit the csv fileѕ",
                      default='/tmp')

    args = argp.parse_args()

    EP.jsonfile = args.file
    try:
        with open(args.file, 'r') as f:
            jd = json.load(f)
            EP.jsondict = jd
    except Error as e:
        print('%s parse failed' % args.file)
        sys.exit(1)

    EP.jsonpart(js=jd, directory=args.directory)
    #EP.recdesc(jd, 1)

if __name__ == '__main__':
    main()
