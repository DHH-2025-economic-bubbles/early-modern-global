#!/bin/bash

cd data
download_file() {
    case $1 in
        "bl_newspapers_meta.csv")
            curl https://a3s.fi/dhh-newspaper/bl_newspapers_meta.txt > bl_newspapers_meta.csv
            ;;
        "bln-places.csv")
            curl https://a3s.fi/dhh-newspaper/bln-places.csv > bln-places.csv
            ;;
        "burney-titles.csv")
            curl https://a3s.fi/dhh-newspaper/burney-titles.csv > burney-titles.csv
            ;;
        "nichols-titles.csv")
            curl https://a3s.fi/dhh-newspaper/nichols-titles.csv > nichols-titles.csv
            ;;
        "chunks_for_blast.tar")
            curl https://a3s.fi/dhh-newspaper/chunks_for_blast.tar > chunks_for_blast.tar
            ;;
        "json_res.tar")
            curl https://a3s.fi/dhh-newspaper/json_res.tar > json_res.tar
            ;;
        "nichols_XML")
            curl https://a3s.fi/dhh-newspaper/nichols_XML > nichols_XML
            ;;
        *)
            echo "no data like this: $1"
            ;;
    esac
}

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <file1> <file2> ..."
    exit 1
fi

for file in "$@"; do
    download_file "$file"
done

cd ..