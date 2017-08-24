#! /bin/bash
#
# Usage: test.sh path-to-project
#
SUT=$1
capture="/tmp/,$$"
# echo "Capturing to ${capture}"
echo "Testing project in $1"
cd ${SUT}
# source env/bin/activate  ## Starting with project 2
ls
# echo "python3 hello.py  &> ${capture}"
python3 hello.py  &> ${capture} 
expect="Hello world"
got=`cat ${capture}`
echo "Expected output: ${expect}"
echo "Got output:      ${got}"


