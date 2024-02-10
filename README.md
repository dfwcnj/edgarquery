# EDGARquery

[![PyPI - Version](https://img.shields.io/pypi/v/edgarquery.svg)](https://pypi.org/project/edgarquery)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/edgarquery.svg)](https://pypi.org/project/edgarquery)

-----

**Table of Contents**

- [Installation](#installation)
```console
NOT YET only in test.pypi for now
pip install edgarquery
```

- [License](#license)
`edgarquery` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

-[Usage]

Right now, three environmental variables are needed:
EQDIR   - the location of the python scripts used only by x.sh

EQODIR  - the location to store the output
EQEMAIL - required by the SEC to download some of the files with curl.

Each script is standalone although some depend upon data downloaded by 
edgarqyery.py or by something like curl. The x.sh(I know) test script
shows some of the usage

Use query.py as a command to retrieve EDGAR files, then use the
appropriate *tocsv.py file as a command to generate CSV file(s)

query.py retrieves files described in
https://www.sec.gov/edgar/sec-api-documentation

query SEC EDGAR site NOTE thæt EQEMAIL env variable is required and must
contain a valid User-Agent such as your email address

options:
  -h, --help            show this help message and exit
  --cik CIK             10-digit Central Index Key
                        leading 0s are added if necessary
  --cy CY               calendar year e.g. CY2023, CY2023Q1, CY2023Q4I
  --frame FRAME         reporting frame e.g us-gaap, ifrs-full, dei, srt
  --units UNITS         USD or shares
  --fact FACT           fact to collect e.g AccountsPayableCurrent,
                                            AssetsCurrent, DebtCurrent
                        shares
  --tf TF               file in which to store the output argument allowed for
                        each query type defaults provided for each download in
                        /tmp
  --companyconcept      returns all the XBRL disclosures from a single company
                        --cik required --frame - default us-gaap --fact -
                        default USD-per-shares
  --companyfacts        aggregates one fact for each reporting entity that is
                        last filed that most closely fits the calendrical
                        period requested --cik required
  --xbrlframes          returns all the company concepts data for a CIK --cy
                        required
  --companyfactsarchivezip
                        returns daily companyfacts index in a zip file --cik
                        required
  --submissionszip      returns daily index of submissions in a zip file

query.py contains the class EDGARquery

EDGARquery.gency generates a CY type I value for the previous quarter

EDGARquery.query retrieves a url and returns the response

EDGARquery.storequery stores a url response in a file 

EDGARquery.companyconcept - all xbrl disclosures for one company in JSON
         cik   - 10-digit Central Index Key - required
                 leading zeros are added if necessary
         frame - reporting frame e.g us-gaap, ifrs-full, dei, srt
         fact  - fact to collect e.g AccountsPayableCurrent

EDGARquery.companyfacts - all the company concepts data for a company
        cik - 10-digit Central Index Key required
                 leading zeros are added if necessary

EDGARquery.xbrlframes - aggregates one fact for each reporting entity that
         was last filed that most closely fits the
         calendrical period requested.
         This API supports for annual, quarterly and instantaneous data:
         frame - reporting frame e.g us-gaap, ifrs-full, dei, srt
         fact - fact to collect
         cy   - calendar year e.g. CY2023, CY2023Q1, CY2023Q4I
         only the I version seems to be available 

EDGARquery.companyfactsearchzip - all the data from the XBRL Frame API
            and the XBRL Company Facts in a zip file

EDGARquery.submissionzip -  public EDGAR filing history for all filers

EDGARquery.financialstatementandnotesdataset - numeric summariæs of financial
        statements. 

edgarcompanyfactstocsv.py
EDGARCompanyFactstoCSV class generates csv files from the json file
          returned by EDGARquery.companyfacts. Note that a somewhat
          large number of csv files are generated

edgarcompanyconceptstocsv.py
EDGARCompanyConcepttoCSV convert the companyconcepts.json file retrieved
by query.py and convert to csv files

edgarxbrlframestocsv.py
EDGARXBRLFramestoCSV class generates a csv file for the json file
          returned by EDGARquery.xbrlframes

edgarcompanyfactsziptocsv.py
EDGARCompanyFactsziptoCSV - not yet implemented

edgarsubmissionsziptocsv.py
EDGARSubmissionsziptoCSV convert the json files in the submissions.zip
EDGAR file to csv files for each submitter

edgarlatest10k.py
EDGARLatest10K class find the url to the latest 10-K for a CIK

edgarlatestsubmissions.py
EDGARLatest10K class return the latest submissions for a CIK

edgarsubmissions.py
EDGARSubmissions class to return links to submissions for a CIK for a year

edgartickerstocsv.py
EDGARTickerstoCSV class to convert EDGAR company_tickers.json
company_tickers_exchange.json and company_tickers_mf.json to csv files



