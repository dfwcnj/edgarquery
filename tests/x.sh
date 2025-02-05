#! /bin/zsh
set -ex

echo $EQDIR
echo $EQODIR

# big files
# if ! test -f /tmp/companyfacts.zip; then
# edgarquery --companyfactsarchivezip \
# fi
#                                             --ticker amzn
# edgarquery --submissionszip
if ! test -f /tmp/submissions.zip; then
    edgarquery  --submissionszip
fi
sleep 5

edgarsubmissionsziptocsv --zipfile $EQODIR/submissions.zip \
    --files CIK0000831001.json,CIK0001665650.json,CIK0000019617.json

# SEC needs a user-agent
curl --user-agent $EQEMAIL --output /private/tmp/sitemap.xml \
     https://www.sec.gov/Archives/edgar/daily-index/sitemap.xml
curl --user-agent $EQEMAIL --output /private/tmp/company_tickers.json \
     https://www.sec.gov/files/company_tickers.json
for f in company.idx crawler.idx form.idx master.idx \
         xbrl.idx sitemap.quarterlyindexes.xml; do
    curl --user-agent $EQEMAIL --output $EQODIR/$f \
         https://www.sec.gov/Archives/edgar/full-index/$f
done


for ticker in msft amzn nvda smci; do
    edgarquery --companyfacts --ticker $ticker
done

for fct in OperatingIncomeLoss; do
    edgarquery  --companyconcept --ticker amzn --fact $fct
done
for fct in Revenues \
           GrossProfit \
           EarningsPerShareBasic \
           Dividends \
           EquityPublicFloat \
           CostofGoodsandServicesSold \
           OperatingIncomeLoss; do
    edgarquery --companyconcept --ticker msft --fact $fct
    edgarquery --companyconcept --ticker nvda --fact $fct
    edgarquery --companyconcept --ticker smci --fact $fct
done

for fct in GrossProfit \
    EarningsPerShareBasic \
    AssetsCurrent \
    DebtCurrent \
    LongTermDebt; do
    for CY in CY2009Q2I CY2023Q1I CY2023Q2I CY2023Q3I; do
        echo $CY
        edgarquery --xbrlframes --cy $CY --fact $fct
    done
done

for F in $(ls $EQODIR/CompanyFacts*.json |xargs basename); do
    echo $F
    edgarcompanyfactstocsv --file $EQODIR/$F --directory $EQODIR
done

for F in $(ls $EQODIR/CompanyConcept*.json |xargs basename); do
    echo $F
    edgarcompanyconcepttocsv --file $EQODIR/$F --directory $EQODIR
done

for F in $(ls $EQODIR/XBRLFrames*.json |xargs basename); do
    echo $F
    edgarxbrlframestocsv --file $EQODIR/$F --directory $EQODIR
done

#edgarsubmissionszipṫocsv --zipfile $EQODIR/submissions.zip --all


for ticker in avd msft amzn nvda smci; do
    #latest10K --ticker $ticker
    #latestsubmissions --ticker $ticker
    edgarsubmissions --ticker $ticker
    edgarsubmissions --ticker $ticker --year 2022
done

edgartickerstocsv
curl --user-agent $EQEMAIL --output /private/tmp/company_tickers.json \
     https://www.sec.gov/files/company_tickers.json

##############################################################################
exit
##############################################################################



