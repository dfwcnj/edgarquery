#! /bin/bash

ODIR=/private/tmp
for F in $(ls $ODIR/CompanyFacts*.csv |xargs basename); do
    # echo $F
    echo $F | while IFS='.' read -ra FA; do
        CC=${FA[3]}
        echo $CC
    done
done | /usr/bin/sort -u > $ODIR/Concepts.txt

