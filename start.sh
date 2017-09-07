#! /bin/bash
#
# Start the auto-checker service as a background
# process, savng the process number (of the lead process)
# in service_pid.
#
# Usage: bash start.sh
# Effects: In addition to starting a flask service under gunicorn,
# file SERVICE_PID will be overwritten (or created) with the
# process number of the gunicorn service just started.
# Limitations:  The virtual environment must be installed
# in the 'env' sub-directory of this directory.  Although this 
# script should work when invoked manually, as well as from the
# Makefile, virtual environment location may fail if it is
# invoked through a symbolic link. 
#
# See design rationale at the end of this file
#
this=${BASH_SOURCE[0]}
here=`dirname ${this}`
source ${here}/env/bin/activate
pushd autocheck
gunicorn --bind="0.0.0.0:8000" flask_grader:app &
pid=$!
popd
echo ${pid} >SERVICE_PID
echo "Green unicorn server started on PID ${pid}"

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
