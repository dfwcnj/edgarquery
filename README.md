# EDGARquery

[![PyPI - Version](https://img.shields.io/pypi/v/edgarquery.svg)](https://pypi.org/project/edgarquery)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/edgarquery.svg)](https://pypi.org/project/edgarquery)

-----

**Table of Contents**

- [Installation](#installation)
```console
pip install edgarquery
```

- [License](#license)
`edgarquery` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

-[Usage]

Use edgarquery.py as a command to retrieve EDGAR files, then use the
appropriate *tocsv.py file as a command to generate CSV file(s)

edgarquery.py retrieves files described in
https://www.sec.gov/edgar/sec-api-documentation

query SEC EDGAR site NOTE thæt EQEMAILADDR env variable is required and must
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

edgarquery.py contains the class EDGARquery

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

EDGARCompanyFactstoCSV class generates csv files from the json file
          returned by EDGARquery.companyfacts. Note that a somewhat
	  large number of csv files are generated

EDGARXBRLFramestoCSV class generates a csv file for the json file
          returned by EDGARquery.xbrlframes


