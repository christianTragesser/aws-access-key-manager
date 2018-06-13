#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -e

echo -e "\n Creating Lambda binary for upload:\n" 
mkdir $SCRIPT_DIR/compile
cp $SCRIPT_DIR/*.py $SCRIPT_DIR/compile
pip install -r requirements.txt -t $SCRIPT_DIR/compile
cd $SCRIPT_DIR/compile && zip -r ../key_man.zip ./* && cd $SCRIPT_DIR
rm -rf $SCRIPT_DIR/compile
ls -alh | grep key_man.zip
echo -e "\n  AWS Lambda bundle key_man.zip created!\n"
