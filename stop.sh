#! /bin/bash
#
# Stop the auto-checker service started by start.sh
# It's process ID should be in ./SERVICE_PID
#
# See design notes in start.sh
# 
this=${BASH_SOURCE[0]}
here=`dirname ${this}`
pushd ${here}
pid=`cat SERVICE_PID`
numpat='^[0-9]+$'
if [[ ${pid} =~  ${numpat} ]]; then
    # That looks like a process ID ...
    echo "Killing process ${pid}"
    kill -9 ${pid}
else
    echo "Didn't find expected value in ${here}/SERVICE_PID"
    echo "Found /${pid}/"
    echo "Didn't match /${numpat}/"
fi;
popd


#
#
#
# Design notes:
# This is a shell script outside the Makefile so that we
# can make sure it is run by bash, with one shell process
# running the whole script.  Make uses a separate shell
# process for each line of a recipe, making it difficult to
# capture the process ID.  Also Make can use a different
# shell, and may act differently between Windows and Unix.
#
# see also: stop.sh
