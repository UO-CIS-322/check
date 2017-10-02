#! /bin/bash
#
# Usage: test.sh path-to-project
#

##########################################
#  Set context from command line argument
#  and location of this script
##########################################
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


#############################################
# Selectively override defaults to control
# the project
#############################################
echo "Copying test credentials"
cp ${HERE}/test_credentials.ini ${SUT}/pageserver/credentials.ini
echo "Credentials file in effect: "
cat ${SUT}/syllabus/credentials.ini

#############################################
# Start server running
#############################################
cd ${SUT}
source env/bin/activate  ## Starting with project 2
echo "Starting server"
# python3 pageserver.py  &> ${capture} &
make service 
server_pid=$!
echo "Server PID ${server_pid}"
echo "Sleeping 2 seconds to let server start"
sleep 2

#############################################
#  Test server?   For this one, we need an
#  eyeball check
#############################################
echo "You may now test on port 8000"
echo "When done, go to /shutdown"
echo ""

