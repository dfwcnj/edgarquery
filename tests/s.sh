#! /bin/ksh
set -ex

for cik in $( head /private/tmp/tickers.csv | grep -v cik |cut -f1 -d',' | sed "s/\'//g" ); do
    #python src/edgarquery/companyfactsshow.py --cik $cik --show
    edgarcompanyfactsshow --cik $cik --show
done
