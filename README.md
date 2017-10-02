# check

Check a CIS 322 project.  Designed to be used two ways: 

## Remote use (by students)

A web service for students to try turning in a credentials configuration file to check whether it can be cloned, installed, and run by the instructor.  The URL for remote checking, and notes on required project structure, will be published on Canvas as part of an assignment description.  

Note that this checker will be running on a small, weak computer.  We do not know yet whether the web service will be able to handle concurrent requests from many students.  It may be necessary to limit how many times each student may use the checker remotely. 

## Local use (by instructor or students)

### Instructor use

The instructor will use the core checking functions while grading.  By automating assessment of whether the project works, the instructor is freed to spend more time on critical evaluation of code readability, maintainability, documentation, etc. 

### Student use

Students can also run the checker themselves.  Ideally they should follow these steps in this order: 

* Unit test their project with nose
* Integration / system test at the command line
* Use this checker locally to make sure the deployment process will work, and to trouble-shoot issues
* Use this checker remotely to double-check that it will work for the instructor
* Turn credentials file in through Canvas, with confidence that it is
going to work as well for the instructor as it worked for them.

## Required Project Structure

The auto-checker depends on a common structure for each project.
Although it could be made more general, there would be a cost in the
complexity of setting up testing for each project.   Imposing a
uniform structure on each project simplifies both implementation and
use.

Each project has a top-level directory and a sub-directory for source
code, following recommendations from "[The Hitchikers Guide to Python](http://docs.python-guide.org/en/latest/writing/structure/#structure-of-the-repository)."

The top-level directory of the repository includes:

* A Makefile with recipes including *install*, *start*, and *stop*
* *requirements.txt* for building a virtual environment (starting with
project 2)
* Shell scripts *start.sh* and *stop.sh* for starting up and shutting
  down the web service constructed in the project.  *start.sh* takes a
  single optional argument, a TCP/IP port number.  *start.sh* saves
  the process ID of the server (or lead process of a server) in a
  local file, and *stop.sh* uses this local file to locate and kill
  the server.  Normally a Makefile recipes *make start* and *make
  stop* just call these shell scripts with a fixed port, but the checking script will
  call them directly so that it can vary the port number in order to
  accomodate checking of multiple projects concurrently.

Project 0 is not a server, so *start.sh* just runs the program to
completion, and *stop.sh* doesn't do anything.  Projects 0 and 1 do
not use Python virtual environments, so *make install* has less to
do.  These are treated as special cases of the general start-up, test,
shut-down scenario. 

A file *credentials.ini* must *not* be part of the repository.
It follows the standard of the Python *configparser* module.  It
should always include ```author``` (student name, which should match
the official name in the class roster), and ```repo``` (student project
repository URL on github).   Other required fields may vary by
project, but will typically include ```PORT```  (TCP/IP port on which
the server will listen), ```secret_key``` (key used by Flask to
cryptographically sign cookies), and ```DEBUG``` (*True* or *False*
setting for the Flask debug and logging level).   In projects
requiring user credentials for external services, such Google
calendars, the *credentials.ini* file will also include these user
credentials (hence the name).  The
*credentials.ini* file is placed in the source code subdirectory
(which will have a prescribed name for each project) before
installation.    When required credentials are associated with a
particular host address, instructor credentials will replace student
credentials in the *credentials.ini* file before installation, or
credentials will be overridden from the command line.  The instructor
will provide a *config.py* module that combines application default
configuration, configuration from the *credentials.py* file, and
optional overrides from the command line.

## Under the hood

The checker extensively uses the *subprocess* module of Python 3 to
install and execute code.  It uses the *configparser* module to read
configuration data from the *credentials.ini* file.  It uses the
standard *git* command-line program to clone the repository specified
in *credentials.ini*.

This software is still in development, and has not been used in a
class before Fall term 2017.  There will certainly be changes, some of
which may require modifications to the project repository structure.

