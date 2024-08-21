#! /usr/bin/env python

#
# EDGARLatestSubmission
#

import os
import sys
import json

try:
    from edgarquery import ebquery
except ImportError as e:
    import ebquery

class EDGARSubmissionsPivot():

    def __init__(self):
        """ EDGARLatestSubmission

        retrieve the SEC submissions json file and pivot the
        columns to rows
        """
        self.jsurl   = 'https://data.sec.gov/submissions/CIK%s.json'
        if 'EQEMAIL' in os.environ:
            self.hdr     = {'User-Agent' : os.environ['EQEMAIL'] }
        else:
            print('EQEMAIL environmental variable must be set to a valid \
                   HTTP User-Agent value such as an email address')
        self.uq = ebquery._EBURLQuery()

    def pivotsubmissions(self, cik):
        """ pivotsubmissions(cik)
        retrieve the submissions json file for a CIk and return
        the column names along with the columns rendered to a 
        list of rows
        cik - the SEC central index key for a company
        """
        url = self.jsurl  % (cik.zfill(10) )
        resp = self.uq.query(url, self.hdr)
        if resp == None:
            return None
        rstr    = resp.read().decode('utf-8')
        js = json.loads(rstr)
        hdr = [k for k in js['filings']['recent'].keys()]
        lr = len(js['filings']['recent'][hdr[0]])
        rows=[]
        for i in range(lr):
            row = []
            for k in hdr:
                row.append(js['filings']['recent'][k][i])
            rows.append(row)
        return hdr, rows

