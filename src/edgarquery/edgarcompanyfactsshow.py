#! env python

import datetime
import os
import sys
import argparse
import csv
import json
import re
import urllib.request
import webbrowser
import zipfile

import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

try:
    import ebquery
    import tickerd
except ImportError as e:
    from edgarquery import ebquery
    from edgarquery import tickerd

class CompanyFactsShow():

    def __init__(self):
        """ CompanyFactsShow

        collect SEC EDGAR company facts for a CIK and display them in
        your browser
        """

        self.xbrl     = 'https://data.sec.gov/api/xbrl'
        self.cfurl    = '%s/companyfacts'   % self.xbrl
        self.turl     = 'https://www.sec.gov/files/company_tickers.json'
        self.seurl    = 'https://www.sec.gov/Archives/edgar'
        self.cfzurl   = '%s/daily-index/xbrl/companyfacts.zip' % self.seurl

        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')

        self.uq = ebquery._EBURLQuery()
        self.td = tickerd.TickerD()


    def getcikforticker(self, ticker):
        return self.td.getcikforticker(ticker)

    def getcompanyfactszip(self, dir):
        ofn = os.path.join(dir, 'companyfacts.zip')
        if os.path.isfile(ofn):
            return ofn
        resp = self.uq.query(self.cfzurl, self.hdr)
        self.uq.storequery(resp, ofn)
        return ofn

    def processjson(self, cik, rstr):
        """ processjson(js)

        load the company facts query string into a json structure 
        and process them with jsonfacts()
        rstr - json string to parse
        """
        jsd = json.loads(rstr)
        assert type(jsd) == type({}), 'jsonpart: part not a dictionary'
        self.enm = jsd['entityName']
        return self.facts2html(cik, jsd['facts'])

    def facts2html(self, cik, facts):
        """ jsonfacts(facts) parse companyfacts json file

        construct the html page with the json structure
        facts - json structure containing SEC EDGAR companyfacts
        """
        assert type(facts) == type({}), 'jsonfacts: facts not a dictionary'
        htmla = []
        htmla.append('<html>')


        if type(cik) == type(1):
            cik = '%d' % (cik)

        ch = self.td.getrecforcik(cik)
        if ch == None:
            print('jsonfacts: no ticker data for %s' % cik,
                  file=sys.stderr)
            return None
        ttl = 'Company Facts: CIK%s' % (cik.zfill(10) )
        if 'title' in ch.keys():
            ttl = 'Company Facts: %s CIK%s' % (ch['title'], cik.zfill(10) )

        htmla.append('<head>')
        htmla.append('<h1>%s</h1>' % (ttl) )
        htmla.append('<script src="https://cdn.plot.ly/plotly-2.32.0.min.js" charset="utf-8"></script>')
        htmla.append('</head>')

        fka = [k for k in facts.keys()]
        for fi in range(len(fka) ):
            k = fka[fi]
            self.facttype = k           # dei or us-gaap
            assert type(facts[k]) == type({}), \
                'jsonfacts: %s not a dictionary' % self.k

            htmla.append('<p>fact type: %s</p>' % (self.facttype) )

            fta = [ft for ft in facts[k].keys()]
            for ti in range(len(fta) ):
                t = fta[ti]

                label = facts[k][t]['label']
                if label and 'Deprecated' in label:
                    continue
                htmla.append('<p>tag: %s</p>' % (t) )
                htmla.append('<p>label: %s</p>' % (label) )

                descr = facts[k][t]['description']
                if not descr:
                    descr = 'No description'
                htmla.append('<h3>Description: %s</h3>' % (descr) )

                units = facts[k][t]['units']
                assert type(units) == type({}), \
                    'jsonfacts: units not a dictionary'
                uka = [u for u in units.keys() ]
                for ui in range(len(uka) ):
                    uk = uka[ui]
                    htmla.append('<p>units: %s</p>' % (uk) )

                    #self.units = uk
                    #htmla.append('<div id="%s%s%s">' % (k, t, uk) )
                    assert type(units[uk]) == type([]), \
                        'jasonfacts %s is not an array'
                    fig = self.jsonfactplot(units[uk], label)

                    figjs = fig.to_json()

                    htmla.append('<div id="fig%s%s%s">' % (fi, ti, ui) )
                    htmla.append('<script>')
                    htmla.append('var figobj = %s;\n' % figjs)
                    htmla.append('Plotly.newPlot("fig%s%s%s", figobj.data, figobj.layout, {});' % (fi,ti,ui) )
                    htmla.append('</script>')
                    htmla.append('</div>')

                    tbl = self.jsonfacttable(units[uk], label)
                    htmla.extend(tbl)
        return htmla

    def jsonfactplot(self, recs, label):
        """ jsonfactplot(self, recs, label)

        plot the first two columns of the fact array
        recs - company fact rows
        label - label
        """

        ld=None
        for i in range(len(recs)):
            if recs[i]['form'] == '10-K':
                cd = datetime.datetime.strptime(recs[i]['end'], '%Y-%m-%d')
                if ld != None and cd <= ld:
                    recs[i]['form'] = '%s ' % recs[i]['form']
            ld = datetime.datetime.strptime(recs[i]['end'], '%Y-%m-%d')

        ia = [i for i in range(len(recs)) if recs[i]['form']=='10-K']
        dates = [recs[i]['end'] for i in ia]
        vals = [recs[i]['val'] for i in ia]
        for i in range(len(vals)):
            if type(vals[i]) != type(0):
                vals[i] = 0

        fig = go.Figure(go.Scatter(
            x = dates,
            y = vals
        ))
        return fig

    def jsonfacttable(self, recs, label):
        """ jsonfacttable(recs)

        construct an html table from the rows of a company fact
        recs - company fact rows
        """
        htmla = []
        htmla.append('<table border=1 >')

        ka = ['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame']
        hd = '</th><th scope="col">'.join(ka)
        htmla.append('<tr><th scope="col">%s</th></tr>' % (hd) )
        cap = '<caption>%s</caption>' % (label)
        htmla.append(cap)
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
            htmla.append('<tr><td scope="row">%s</td></tr>' % (rw) )
        htmla.append('</table>')
        return htmla

    def savefacthtml(self, cik, htmla, directory):
        """ savefacthtml(directory)

        save the generated html in the specified directory with the
        name CompanyFactsCIK$cik.html
        cik - central index key
        htmla - company facts html in array format
        directory - where to store the generated html
        """
        if type(cik) == type(1):
            cik = '%d' % (cik)
        htmlfile = os.path.join(directory,
            'CompanyFactsCIK%s.html' % cik.zfill(10) )
        with open(htmlfile, 'w') as fp:
            fp.write(''.join(htmla) )
        return htmlfile

    def show(self, htmlfile):
        """ show()

        display the generated html in a web browser
        """
        webbrowser.open('file://%s' % htmlfile)

    def getcompanyfacts(self, cik):
        """ getcompanyfacts(cik)

        collectall the SEC EDGAR company facts  data for a company
        return the query response as a python string
        """
        url = '%s/CIK%s.json' % (self.cfurl, cik.zfill(10))
        resp = self.uq.query(url, self.hdr)
        if resp == None:
            return resp
        rstr = resp.read().decode('utf-8')
        return rstr

    def getcompanyfactsfromzip(self, cik, cfz):
        """companyfactsfromzip(cik, cfz)
        collectall the SEC EDGAR company facts  data for a company
        and store them in an html file
        cik - Central Index Key
        cfz - companyfacts.zip file downloaded from SEC
        """
        if not os.path.exists(cfz):
            print('no %s' % zf, file=sys.stderr)
            sys.exit()
        zfp = zipfile.ZipFile(cfz, 'r')
        nl = zfp.namelist()
        cfn = 'CIK%s.json' % cik.zfill(10)
        if cfn not in nl:
            return None
        jstr = None
        with zfp.open(cfn) as np:
            jstr = np.read()

        htmla = self.processjson(cik,jstr)
        return htmla

    def companyfactsfromnet(self, cik):
        """companyfacts 

        collectall the SEC EDGAR company facts  data for a company
        and store them in an html file
        cik - Central Index Key
        """
        rstr = self.getcompanyfacts(cik)
        if rstr == None:
            print('companyfacts: no data for %s' % cik, file=sys.stderr)
            return None
        else:
            htmla = self.processjson(cik, rstr)
            return htmla

    def companyfacts(self, cik, cfz):
        if cfz == None:
            return self.companyfactsfromnet(cik)
        return self.getcompanyfactsfromzip(cik, cfz)

def main():
    argp = argparse.ArgumentParser(description='parse EDGAR company\
    facts for a ticker or cik and display them in a browser')
    argp.add_argument('--cik', help='Centralized Index Key for the company')
    argp.add_argument('--fromcfz', action='store_true',
            help='download and use SEC companyfacts.zip file to show '
                 'company data based on CIK. '
                 'if the file is already downloaded, it is reused, but '
                 'if not it can take a while to download 1.2gb')
    argp.add_argument('--ticker', help='Ticker for the company')
    argp.add_argument('--directory', default='/tmp',
        help='where to store the html file to display')

    args = argp.parse_args()
    if not args.cik and not args.ticker:
        argp.print_help()
        sys.exit()

    CFS = CompanyFactsShow()

    cik = None
    cfz = None
    if args.cik:
        cik = args.cik
    elif args.ticker:
        cik = CFS.getcikforticker(args.ticker)
    if cik == None:
        argp.print_help()
        sys.exit()

    if args.fromcfz:
        cfz = CFS.getcompanyfactszip(args.directory)

    htmla = CFS.companyfacts(cik, cfz)
    if htmla == None:
        print('no data', file=sys.stderr)
        sys.exit()
    htmlfile=CFS.savefacthtml(cik, htmla, args.directory)
    CFS.show(htmlfile)

if __name__ == '__main__':
    main()
