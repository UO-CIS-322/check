#
# Many recipes need to be run in the virtual environment, 
# so run them as $(INVENV) command
INVENV = . env/bin/activate ;

install:	requirements.txt
	rm -rf env
	make env
##
##  Virtual environment
##     
env:
	python3 -m venv  env
	($(INVENV) pip install -r requirements.txt )

##
## Style checks  (for this project, not for projects being checked)
##
check:	env
	($(INVENV)  cd autocheck ; \
	 pycodestyle *.py )

# 'make run' runs Flask's built-in test server, reachable
#  only on localhost,  with debugging turned on unless it
# is unset in CONFIG.py.
# 'make service' runs under the Gunicorn server. 
# 

run:	env
	echo "Launching built-in server for localhost only"
	($(INVENV) python3 autocheck/flask_grader.py -C autocheck/config.ini)

service:	env
	echo "Launching green unicorn in background"
	($(INVENV)  cd autocheck ; \
                   gunicorn --bind="0.0.0.0:8000" \
                   flask_grader:app )&

##
## Run test suite. 
## Currently 'nose' takes care of this, but in future we 
## might add test cases that can't be run under 'nose' 
##
test:	env
	$(INVENV) nosetests

##
## Preserve virtual environment for git repository
## to duplicate it on other targets
##
dist:	env
	$(INVENV) pip freeze >requirements.txt


# 'clean' and 'veryclean' are typically used before checking 
# things into git.  'clean' should leave the project ready to 
# run, while 'veryclean' may leave project in a state that 
# requires re-running installation and configuration steps
# 
clean:
	rm -f *.pyc
	rm -rf __pycache__

veryclean:
	make clean
	rm -f CONFIG.py
	rm -rf env
	rm -f Makefile.local



