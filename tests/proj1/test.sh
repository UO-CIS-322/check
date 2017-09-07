#! /bin/bash
#
# Usage: test.sh path-to-project
#
# Where is this script?  
this_script=${BASH_SOURCE[0]}
#echo "This source file: ${this_script}"
#echo "In directory " `dirname ${this_script}`
dir_raw=`dirname ${this_script}`
dir_actual=`(cd ${dir_raw}; pwd)`
#echo "Cleaned up ${dir_raw} to ${dir_actual}" 
# per http://www.ostricher.com/2014/10/the-right-way-to-get-the-directory-of-a-bash-script/
HERE=${dir_actual}
echo "This script directory: ${HERE}"
#
SUT=$1
capture="/tmp/,$$"
echo "Testing project in $1"
echo "Copying sub-folder ${HERE}/sample_site into ${SUT}"
cp -r ${HERE}/sample_site ${SUT}
echo "Copying test credentials"
cp ${HERE}/test_credentials.ini ${SUT}/pageserver/credentials.ini
echo "Credentials file in effect: "
cat ${SUT}/pageserver/credentials.ini
#
#
cd ${SUT}/pageserver
# source env/bin/activate  ## Starting with project 2
echo "Starting server"
python3 pageserver.py  &> ${capture} &
server_pid=$!
echo "Server PID ${server_pid}"

echo "Sleeping 2 seconds to let server start"
sleep 2

echo ""
echo "Accessing sample page, should be ok"
curl localhost:7777/simple_page.html 2>&1 
echo ""
echo ""
echo "Accessing sample css, should be ok"
sleep 1
curl localhost:7777/simple.css 2>&1 
echo ""
echo ""
echo "Accessing illegal path, should be forbidden"
sleep 1
curl localhost:7777/../sample_page.html 2>&1 
echo ""
echo ""
echo "Accessing non-existent page, should be 404 error"
sleep 1
curl localhost:7777/nopage.html 2>&1 
echo ""
echo ""
echo "Killing server"
kill ${server_pid}
echo ""
echo "Server diagnostic output:"
cat ${capture}

