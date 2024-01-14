#! /bin/bash
set -ex



# ls companyfacts*.json | while IFS='.' read -ra CFF; do echo ${CFF[1]}.json; done

TD=/private/tmp

for F in $(ls $TD/companyfacts*.json |xargs basename); do
    echo $F
    echo $F | while IFS='.' read -ra FA; do
        echo  ${FA[0]}
        echo  ${FA[1]}
        echo  ${FA[2]}
        break
    done
done
