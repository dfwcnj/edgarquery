#! /bin/bash
set -ex

EQDIR=~/Documents/enc/Documents/dfwc/projects/edgarquery/src/edgarquery
echo $EQDIR

ODIR=/private/tmp

PY=~/anaconda3/bin/python

# big files
# ~/anaconda3/bin/python $EQDIR/edgarquery.py --companyfactsarchivezip \
#                                             --cik 1018724
# ~/anaconda3/bin/python $EQDIR/edgarquery.py --submissionszip

# doesn't work for people
# ~/anaconda3/bin/python $EQDIR/edgarquery.py --companyfactsarchivezip --cik 315090

# SEC needs a user-agent
curl --user-agent $EQEMAILADDR --output /private/tmp/sitemap.xml \
     https://www.sec.gov/Archives/edgar/daily-index/sitemap.xml
curl --user-agent $EQEMAILADDR --output /private/tmp/company_tickers.json \
     https://www.sec.gov/files/company_tickers.json
for f in company.zip crawler.idx form.zip master.zip \
         xbrl.zip sitemap.quarterlyindexes.xml; do
    curl --user-agent $EQEMAILADDR --output $ODIR/$f \
         https://www.sec.gov/Archives/edgar/full-index/$f
done


for cik in 1318605 1018724 1045810; do
    $PY $EQDIR/edgarquery.py --companyfacts --cik $cik
    $PY $EQDIR/edgarquery.py --companyfacts --cik $cik
    $PY $EQDIR/edgarquery.py --companyfacts --cik $cik
done

for fct in AccountsPayableCurrent EarningsPerShareBasic; do
    $PY $EQDIR/edgarquery.py --companyconcept --cik 1318605 --fact $fct
    $PY $EQDIR/edgarquery.py --companyconcept --cik 1018724 --fact $fct
    $PY $EQDIR/edgarquery.py --companyconcept --cik 1045810 --fact $fct
done

for fct in AccountsPayableCurrent AssetsCurrent DebtCurrent \
    LongTermDebt ; do
    for CY in CY2009Q2I CY2023Q1I CY2023Q2I CY2023Q3I; do
        echo CY
        $PY $EQDIR/edgarquery.py --xbrlframes --cy $CY --fact $fct
    done
done

for F in $(ls $ODIR/CompanyFacts*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        OF=${FA[1]}.json
        echo  $OF
        sed -f $EQDIR/sedfile $ODIR/$F > $ODIR/CF.$OF
        ls -l $ODIR/CF.$OF
        $PY $EQDIR/companyfactstocsv.py --file $ODIR/CF.$OF --odir $ODIR
        break
    done
done

for F in $(ls $ODIR/CompanyConcept*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        OF=${FA[1]}.json
        echo  $OF
        sed -f $EQDIR/sedfile $ODIR/$F > $ODIR/CC.$OF
        ls -l $ODIR/CC.$OF
        $PY $EQDIR/companyconcepttocsv.py --file $ODIR/CC.$OF --odir $ODIR
        break
    done
done

for F in $(ls $ODIR/XBRLFrames*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        OF=${FA[4]}.json
        echo  $OF
        sed -f $EQDIR/sedfile $ODIR/$F > $ODIR/XF.$OF
        ls -l $ODIR/XF.$OF
        $PY $EQDIR/xbrlframestocsv.py --file $ODIR/XF.$OF --odir $ODIR
        break
    done
done


##############################################################################
exit
##############################################################################



