#!/bin/bash

# Prvo kreiraj ciljnu strukturu ako ne postoji
mkdir -p src/astronomical_watch

# Lista foldera koje želiš prebaciti.
FOLDERS="core net offline routes script services solar astro"

for F in $FOLDERS; do
    if [ -d "$F" ]; then
        echo "Premestam $F u src/astronomical_watch/$F"
        mv "$F" "src/astronomical_watch/"
    else
        echo "Folder $F ne postoji, preskacem."
    fi
done

# Sada ažuriraj sve import linije u svim .py fajlovima u projektu
echo "Ažuriram import puteve u .py fajlovima..."
find . -type f -name "*.py" ! -path "./src/astronomical_watch/*" | while read -r FILE; do
    sed -i \
        -e 's/from core\./from astronomical_watch.core./g' \
        -e 's/from net\./from astronomical_watch.net./g' \
        -e 's/from offline\./from astronomical_watch.offline./g' \
        -e 's/from routes\./from astronomical_watch.routes./g' \
        -e 's/from script\./from astronomical_watch.script./g' \
        -e 's/from services\./from astronomical_watch.services./g' \
        -e 's/from solar\./from astronomical_watch.solar./g' \
        -e 's/from astro\./from astronomical_watch.astro./g' \
        "$FILE"
done

echo "Premestanje i ažuriranje gotovo! Proveri src/astronomical_watch/ i testiraj aplikaciju."