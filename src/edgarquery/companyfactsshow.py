#! env python

import os
import sys
import argparse
import csv
import json
import re
import urllib.request
import webbrowser

try:
    from edgarquery import common
except ImportError as e:
    import common

class CompanyFactsShow():

    def __init__(self):
        """ CompanyFactsShow

        collect SEC EDGAR company facts for a CIK and display them in
        your browser
        """
        self.cik      = None
        self.rstr     = None
        self.json     = None
        self.htmla    = []
        self.htmlfile = None
        self.tickd    = {}

        self.xbrl     = 'https://data.sec.gov/api/xbrl'
        self.cfurl    = '%s/companyfacts'   % self.xbrl
        self.turl     = 'https://www.sec.gov/files/company_tickers.json'

        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')

        self.uq = common._URLQuery()

    def tickers(self):
        resp = self.uq.query(self.turl, self.hdr)
        rstr = resp.read().decode('utf-8')
        jd = json.loads(rstr)
        for k in jd.keys():
            ck = jd[k]['cik_str']
            self.tickd[ck] = jd[k]


    def processjson(self, rstr):
        """ processjson(js)

        load the company facts query string into a json structure 
        and process them with jsonfacts()
        rstr - json string to parse
        """
        self.json = json.loads(rstr)
        assert type(self.json) == type({}), 'jsonpart: part not a dictionary'
        self.cik = self.json['cik']
        self.enm = self.json['entityName']
        self.jsonfacts(facts=self.json['facts'])

    def jsonfacts(self, facts):
        """ jsonfacts(facts) parse companyfacts json file

        construct the html page with the json structure
        facts - json structure containing SEC EDGAR companyfacts
        """
        assert type(facts) == type({}), 'jsonfacts: facts not a dictionary'
        htmla = []
        htmla.append('<html>')

        cik = '%d' % (self.cik)
        ch = self.tickd[self.cik]
        ttl = 'Company Facts: %s CIK%s' % (ch['title'], cik.zfill(10) )
        htmla.append('<head><h1>%s</h1></head>' % (ttl) )

        fka = [k for k in facts.keys()]
        for k in fka:
            self.facttype = k           # dei or us-gaap
            assert type(facts[k]) == type({}), \
                'jsonfacts: %s not a dictionary' % self.k

            htmla.append('<p>fact type: %s</p><br/>' % (self.facttype) )

            fka = [ft for ft in facts[k].keys()]
            for t in fka:
                #htmla.append('<h3> Fact Name: %s</h3>' % (t) )

                label = facts[k][t]['label']
                #htmla.append('<h4>Fact Label: %s</h4>' % (label) )

                descr = facts[k][t]['description']
                if not descr:
                    descr = 'No description'
                htmla.append('<h3>Description: %s</h3>' % (descr) )

                units = facts[k][t]['units']
                assert type(units) == type({}), \
                    'jsonfacts: units not a dictionary'
                uka = (u for u in units.keys() )
                for uk in uka:
                    self.units = uk
                    assert type(units[uk]) == type([]), \
                        'jasonfacts %s is not an array'
                    self.jsonfacttable(units[uk], label)
        #self.htmla.append('</html>')
        self.htmla.extend(htmla)


    def jsonfacttable(self, recs, label):
        """ jsonfacttable(recs)

        construct an html table from the rows of a company fact
        recs - company fact rows
        """
        self.htmla.append('<table border=1 >')

        ka = [k for k in recs[0].keys() ]
        hd = '</th><th scope="col">'.join(ka)
        self.htmla.append('<tr><th scope="col">%s</th></tr>' % (hd) )
        cap = '<caption>%s</caption>' % (label)
        self.htmla.append(cap)
        for r in recs:
            ra = [r[k] for k in r.keys()]
            for i in range(len(ra) ):
                if not ra[i]:
                    ra[i] = 'null'
                elif type(ra[i]) == type(1):
                    ra[i] = '%d' % (ra[i])
                elif type(ra[i]) == type(1.0):
                    ra[i] = '%f' % (ra[i])
            rw = '</td><td scope="row">'.join(ra)
            self.htmla.append('<tr><td scope="row">%s</td></tr>' % (rw) )
        self.htmla.append('</table>')

    def savefacthtml(self, directory):
        """ savefacthtml(directory)

        save the generated html in the specified directory with the
        name CompanyFactsCIK$cik.html
        directory - where to store the generated html
        """
        cik = '%d' % (self.cik)
        self.htmlfile = os.path.join(directory,
            'CompanyFactsCIK%s.html' % cik.zfill(10) )
        with open(self.htmlfile, 'w') as fp:
            fp.write(''.join(self.htmla) )

    def show(self):
        """ show()

        display the generated html in a web browser
        """
        webbrowser.open('file://%s' % self.htmlfile)

    def getcompanyfacts(self, cik):
        """ getcompanyfacts(cik)

        collectall the SEC EDGAR company facts  data for a company
        return the query response as a python string
        """
        self.cik = cik
        self.tickers()
        url = '%s/CIK%s.json' % (self.cfurl, cik.zfill(10))
        resp = self.uq.query(url, self.hdr)
        rstr = resp.read().decode('utf-8')
        return rstr

    def companyfacts(self, cik, directory):
        """companyfacts 

        collectall the SEC EDGAR company facts  data for a company
        and store them in an html file
        cik - Central Index Key
        directory - where to store the generated html file
        """
        rstr = self.getcompanyfacts(cik)
        self.processjson(rstr)

        self.savefacthtml(directory)


def main():
    argp = argparse.ArgumentParser(description='parse EDGAR company\
    facts for a cik and display them in a browser')
    argp.add_argument('--cik', required=True,
        help='Centralized Index Key for the company')
    argp.add_argument('--directory', default='/tmp',
        help='where to store the html file to display')
    argp.add_argument('--show', action='store_true', default=False,
        help='display the html in your browser')

    args = argp.parse_args()

    CFS = CompanyFactsShow()
    CFS.companyfacts(args.cik, args.directory)
    if args.show:
        CFS.show()

if __name__ == '__main__':
    main()
