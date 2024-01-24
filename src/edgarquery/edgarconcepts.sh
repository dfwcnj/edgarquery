#! /bin/bash

for F in $(ls $EQODIR/CompanyFacts*.csv |xargs basename); do
    # echo $F
    echo $F | while IFS='.' read -ra FA; do
        CC=${FA[3]}
        echo $CC
    done
done | sort -u > $EQODIR/Concepts.txt

