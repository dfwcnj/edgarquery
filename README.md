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

edgarquery.py retrieves files described in
https://www.sec.gov/edgar/sec-api-documentation

query SEC EDGAR site NOTE thæt EQEMAILADDR env variable is required and must
contain a valid User-Agent such as your email address

options:
  -h, --help            show this help message and exit
  --cik CIK             10-digit Central Index Key
  --cy CY               calendar year e.g. CY2023, CY2023Q1, CY2023Q4I
  --frame FRAME         reporting frame e.g us-gaap, ifrs-full, dei, srt
  --units UNITS         USD or shares
  --fact FACT           fact to collect e.g AccountsPayableCurrent, USD-per-
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


