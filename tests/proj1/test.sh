#! /bin/bash
#
# Usage: test.sh path-to-project port
#

#DEBUG
echo "Script test.sh called with these args: $*"


# Where is this script?  
this_script=${BASH_SOURCE[0]}
dir_raw=`dirname ${this_script}`
dir_actual=`(cd ${dir_raw}; pwd)`


# per http://www.ostricher.com/2014/10/the-right-way-to-get-the-directory-of-a-bash-script/
HERE=${dir_actual}
echo "This script directory: ${HERE}"
#
SUT=$1
PORT=$2
capture="/tmp/,$$"
echo "Testing project in ${SUT} at port  |${PORT}|"
echo "Copying sub-folder ${HERE}/sample_site into ${SUT}"
cp -r ${HERE}/sample_site ${SUT}
echo "Copying test credentials"
cp ${HERE}/test_credentials.ini ${SUT}/pageserver/credentials.ini
echo "Credentials file in effect: "
cat ${SUT}/pageserver/credentials.ini
#
#
cd ${SUT}
echo "Starting server"
bash ./start.sh -P ${PORT}  &> ${capture} 
server_pid=$!
echo "Server PID ${server_pid} on port ${PORT}"

echo "Sleeping 2 seconds to let server start"
sleep 2

echo ""
echo "Accessing sample page, should be ok"
curl localhost:${PORT}/simple_page.html 2>&1 
echo ""
echo ""
echo "Accessing sample css, should be ok"
sleep 1
curl localhost:${PORT}/simple.css 2>&1 
echo ""
echo ""
echo "Accessing illegal path, should be forbidden"
sleep 1
curl localhost:${PORT}/~/sample_page.html 2>&1 
echo ""
echo ""
echo "Accessing non-existent page, should be 404 error"
sleep 1
curl localhost:${PORT}/nopage.html 2>&1 
echo ""
echo ""
echo "Server diagnostic output:"
cat ${capture}
echo ""
