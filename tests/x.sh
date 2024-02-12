#! /bin/bash
set -ex

echo $EQDIR
echo $EQODIR


PY=~/anaconda3/bin/python

# big files
# ~/anaconda3/bin/python $EQDIR/doquery.py --companyfactsarchivezip \
#                                             --cik 1018724
# ~/anaconda3/bin/python $EQDIR/doquery.py --submissionszip
#~/anaconda3/bin/python $EQDIR/doquery.py --submissionszip
#sleep 5

$PY $EQDIR/submissionsziptocsv.py --zipfile $EQODIR/submissions.zip \
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


for cik in 1318605 1018724 1045810; do
    $PY $EQDIR/doquery.py --companyfacts --cik $cik
done

for fct in AccountsPayableCurrent EarningsPerShareBasic; do
    $PY $EQDIR/doquery.py --companyconcept --cik 1318605 --fact $fct
    $PY $EQDIR/doquery.py --companyconcept --cik 1018724 --fact $fct
    $PY $EQDIR/doquery.py --companyconcept --cik 1045810 --fact $fct
done

for fct in AccountsPayableCurrent AssetsCurrent DebtCurrent \
    LongTermDebt ; do
    for CY in CY2009Q2I CY2023Q1I CY2023Q2I CY2023Q3I; do
        echo CY
        $PY $EQDIR/doquery.py --xbrlframes --cy $CY --fact $fct
    done
done

for F in $(ls $EQODIR/CompanyFacts*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        OF=${FA[1]}.json
        echo  $OF
        sed -f $EQDIR/sedfile $EQODIR/$F > $EQODIR/CF.$OF
        ls -l $EQODIR/CF.$OF
        $PY $EQDIR/companyfactstocsv.py --file $EQODIR/CF.$OF --odir $EQODIR
        break
    done
done

for F in $(ls $EQODIR/CompanyConcept*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        OF=${FA[1]}.json
        echo  $OF
        sed -f $EQDIR/sedfile $EQODIR/$F > $EQODIR/CC.$OF
        ls -l $EQODIR/CC.$OF
        $PY $EQDIR/companyconcepttocsv.py --file $EQODIR/CC.$OF --odir $EQODIR
        break
    done
done

for F in $(ls $EQODIR/XBRLFrames*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        OF=${FA[4]}.json
        echo  $OF
        sed -f $EQDIR/sedfile $EQODIR/$F > $EQODIR/XF.$OF
        ls -l $EQODIR/XF.$OF
        $PY $EQDIR/xbrlframestocsv.py --file $EQODIR/XF.$OF --odir $EQODIR
        break
    done
done

#$PY $EQDIR/submissionszipṫocsv.py --zipfile $EQODIR/submissions.zip \
#    --all


for cik in 5981 1318605 1018724 1045810; do
    #$PY $EQDIR/latest10K.py --cik $cik
    #$PY $EQDIR/latestsubmissions.py --cik $cik
    $PY $EQDIR/submissions.py --cik $cik
    $PY $EQDIR/submissions.py --cik $cik --year 2008
done

$EQDIR/tickerstocsv.py

##############################################################################
exit
##############################################################################



