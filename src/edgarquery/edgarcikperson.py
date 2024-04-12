#! env python

import os
import re
import sys
import argparse
import datetime
import zipfile
import sqlite3
import urllib.request
from functools import partial

try:
    from edgarquery import ebquery
except ImportError as e:
    import ebquery

class CIKPerson():

    def __init__(self):
        """ CIKPerson()

        collect CIK and name from form345 files
        store in an sqlite3 database
        """
        self.dbname = 'cikowner.db'
        self.dbcon = None
        self.dbcur = None
        self.y0     = 2006
        self.y1     = None
        self.iturl = 'https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets'
        self.uq = ebquery._EBURLQuery()
        self.chunksize =4294967296 # 4M

        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')

        self.cpdb = "CREATE TABLE IF NOT EXISTS cikperson ('CIK', 'Name', 'Relationship')"
        self.cpidx = "CREATE UNIQUE INDEX IF NOT EXISTS cikidx ON cikperson ('CIK', 'Relationship')"
        self.cpins = "INSERT OR IGNORE INTO cikperson VALUES (%s)"

    def cikpersontbl(self):
        """ cikpersontbl()

        create cikperson table and index if necessary
        """
        sql = self.cpdb
        self.dbcur.execute(sql)
        sql = self.cpidx
        self.dbcur.execute(sql)
        self.dbcon.commit()

    def dbconnect(self, cikpersondb):
       """ dbconnect(cikpersondb)

       create or connect to cikpersondb
       cikpersondb - full path to the sqlite3 database file
       """
       self.dbcon = sqlite3.connect(cikpersondb)
       self.dbcur = self.dbcon.cursor()

    def storecikowner(self, cik, owner, rel):
        """ storecikowner(cik, owner, rel)

        store the cik, owner, and relationship row
        into the sqlite3 database
        cik - central index key used by the SEC
        owner - owner name 
        rel - relationship of the owner to a submission
        """
        values = '"%s","%s","%s"' % (cik, owner, rel)
        # if "'" in owner: print(values, file=sys.stderr)
        sql = self.cpins % (values)
        self.dbcur.execute(sql)

    def form345zipfileiter(self, fzpath, file):
        """ form345zipfileiter(fzpath, iter)

        return an iterator for lines from file in fzpath
        fzpath - form345 zip file from fred.stlouisfed.org
        file  - file in the zip file to read
        """
        try:
            lna = []
            with zipfile.ZipFile(fzpath, mode='r') as zfp:
                fstr = zfp.read(file).decode("utf-8")
                lge = (line for line in fstr.splitlines() )
                return lge
        except zipfile.BadZipfile as e:
            print('open %s: %s', (fzpath, e) )
            sys.exit(1)

    def collectform345owners(self, fznm, fzpath):
        """ collectform345owners(fznm, fzpath)

        collect cik, name, and relationship from REPORTINGOWNER.tsv
        fznm - name of the form345.zip file
        fzpath - full path of where the file will be stored
        """

        url = '%s/%s' % (self.iturl, fznm)
        resp = self.uq.query(url, self.hdr)
        if not resp:
            return
        self.uq.storequery(resp, fzpath)
        # resp = self.query(url)
        # self.storequery(resp, fzpath)
        lge = self.form345zipfileiter(fzpath, 'REPORTINGOWNER.tsv')
        hdr = []
        for ln in lge:
            la =  re.split('\t', ln)
            if len(hdr) == 0:
                hdr = la
                continue
            self.storecikowner(la[1], la[2], la[3])
        self.dbcon.commit()
        os.unlink(fzpath)


    def reportcikpeople(self, fp):
        assert self.dbcur, 'no sqlite3 cursor'
        sql = 'SELECT * from cikperson'
        self.dbcur.execute(sql)
        hdr = [column[0] for column in self.dbcur.description]
        print('"%s"' % ('","'.join(hdr) ), file=fp )
        rows = self.dbcur.fetchall()
        for row in rows:
            print('"%s"' % ('","'.join(row) ), file=fp )

    def processform345files(self, cikpersondb, fp):
        """ processform345files(cikpersondb)

        connect to the cik person db
        create the table and index
        generate the form345.zip filenames to collect
        cikpersondb - full path name of the database
        """
        now = datetime.datetime.now()
        self.y1 = now.year + 1
        if now.month < 3:
            self.y1 = now.year

        self.dbconnect(cikpersondb)
        self.cikpersontbl()
        for y in range(self.y0, self.y1):
            for q in (1,2,3,4):
                fznm = '%dq%d_form345.zip' % (y,q)
                print('processform345files %s' % (fznm), file=sys.stderr )
                if y == now.year:
                    if now.month <=3: return
                    elif q == 1 and now.month <=3: return
                    elif q == 2 and now.month <=6: return
                    elif q == 3 and now.month <=9: return
                    elif q == 4: return
                self.collectform345owners(fznm, fznm)
        #self.reportcikpeople(fp)

def main():
    CP = CIKPerson()
    argp = argparse.ArgumentParser(prog='cikperson',
        description='extract CIK and person names from form345 zip files')
    argp.add_argument("--cikpersondb", default=':memory:',
        help="full path to the sqlite3  database - default in memory")
    argp.add_argument("--file",
        help="where to store the output - default stdout")

    args = argp.parse_args()

    fp = sys.stdout
    if args.file:
        with open(args.file, 'w') as fp:
            CP.processform345files(args.cikpersondb, fp)
            CP.reportcikpeople(fp)
    else:
        CP.processform345files(args.cikpersondb, fp)
        CP.reportcikpeople(fp)

if __name__ == '__main__':
    main()


