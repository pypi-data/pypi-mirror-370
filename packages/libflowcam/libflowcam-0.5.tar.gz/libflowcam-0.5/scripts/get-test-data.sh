#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
cd ..
mkdir -p testdata
cd testdata

SHAOUT=($(cat flowcam_polina_pontoon_1807_r1/* | sha256sum -b))
SHAOUT=${SHAOUT[0]}
if [ "$SHAOUT" = "41401b12423df4dd8f40b362d4cdb4ebf21718f202324af82d2b9c5b7f1d0c7e" ]; then
    echo "Test data OK, skipping download"
else
    echo "Test data hash ($SHAOUT) did not match expected output, redownloading data"
    rm -r flowcam_polina_pontoon_1807_r1
    wget https://repo.alexbaldwin.dev/open-data/flowcam/2025-07-18/r1.zip
    unzip r1.zip
    rm r1.zip
fi
