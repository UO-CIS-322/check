"""
Trial run of a student project, starting from a configuration
file.  This is the part of the auto-testing process that is
the same whether it is run from a web server or from
the command line.

General scheme:  We have a set of steps that either succeed
or fail.  The start with a context that is a dictionary,
and which contains enough information for running that step.
If they succeed, the dictionary is augmented with information for
the next step, and they return True. The context["messages"]
may also be augmented, but success can be silent. If the step fails
(e.g., we can't download the repo, or the 'make install' fails,
or we encounter an unexpected error), then the step returns
False and the context["messages"] field is definitely augmented.

For each project, we expect two scripts in test/projX : 
  test.sh <proj-path> <portnum> starts server, runs any automated tests, 
  leaves server running for manual tests. 
  cleanup.sh stops server, deletes anything that needs deleting. 
  test.sh may also leave a time-bomb for destroying the test
  process after K minutes (tentatively 10). 
Requirements (assumptions) about the structure of student projects
is in ../README.md --- we impose this common structure so that we 
can factor much of the manipulation out of start.sh and cleanup.sh
to here.  
"""

import configparser
import os
import arrow
import random
import subprocess

import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.DEBUG)
log = logging.getLogger(__name__)


CRED_FIELDS = ["author", "repo"]


def trial(context):
    """
    Initially we expect the context dict to contain two fields:
    "credentials" is the .ini file that includes, among other things,
    student name and repository URL.
    "messages" is where we place log output, including error messages.
    Successful steps need not add to the messages, but failures
    must always add explanatory messages.
    """
    log.debug("Entering trial")
    log.debug("Context: {}".format(context))
    settings = read_config(context["credentials"])
    log.debug("Configuration settings: {}".format(settings))
    repo_remote = settings["repo"]
    clone_path = tmp_path("clone")
    context["repo_remote"] = repo_remote
    context["clone_path"] = clone_path

    log.debug("Preparing to clone and install")

    ok = (clone_repo(context)
              and install(context))

    # The following steps are contingent only on passing
    # installation, i.e., we run tests even if style check fails
    if ok:
          ok = stylecheck(context)
          ok = testit(context) and ok 

    log.debug("Returned from trial")
    log.debug("Log messages: {}".format(context["messages"]))

    return ok

def shutdown(context):
    """
    After trial, and after a pause for manual testing, we 
    try to clean up. 
    """
    log.debug("Entering shutdown")
    clone = context["clone_path"]
    project = context["project"]
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,  "..", "tests", project)
    test_script = os.path.join(test_path, "cleanup.sh")
    log.debug("Looking for shutdown script at {}".format(test_path))
    context["messages"] = "\n*** Shutting down ***\n"
    testlog = "*** Call to subprocess shutdown.sh did not complete ***"
    try:
        testlog = subprocess.check_output(
            [test_script, clone],
            cwd=test_path,
            stderr=subprocess.STDOUT,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is?
        context["messages"] += testlog
        log.debug("Shutdown output: {}".format(testlog))
        return True
    except subprocess.CalledProcessError as exception:
        log.error("Cleanup failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += testlog
        context["messages"] += exception.output
        return False



def read_config(path):
    log.debug("Entering read_config")
    config = configparser.ConfigParser()
    config.read(path)
    settings = {}
    for field in CRED_FIELDS:
        settings[field] = config["DEFAULT"].get(field, "not specified")
    return settings


def clone_repo(context):
    """Attempt to clone the repository"""
    log.debug("Entering clone_repo")
    clone_path = context["clone_path"]
    repo_remote = context["repo_remote"]
    context["messages"] += "\n*** Cloning ***\n"
    try:
        installation = subprocess.check_output(
            ["git", "clone", repo_remote, clone_path],
            stderr=subprocess.STDOUT,
            # encoding='utf-8')        # Not supported in Python 3.4
            universal_newlines=True)   # But this is?
        log.info("Installation messages: {}".format(installation))
        context["messages"] += installation
        listing = subprocess.check_output(
            ["ls", "-p", "-C", "-B",  clone_path],
            stderr=subprocess.STDOUT,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is?
        context["messages"] += listing
        return True
    except subprocess.CalledProcessError as exception:
        log.error("Installation failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += exception.output
        return False


def install(context):
    """Installation includes copying the credentials file
    and calling the Makefile installation recipe.
    """
    log.debug("Entering install")
    clone = context["clone_path"]
    log.debug("Working in directory {}".format(clone))
    makelog = "\n*** Installing ***\n"
    try:
        cred_file_path = os.path.join(context["app"], "credentials.ini")
        makelog += subprocess.check_output(
            ["cp", context["credentials"], cred_file_path],
            cwd=clone,
            stderr=subprocess.STDOUT,
            universal_newlines=True)
        makelog += "** Contents of application sub-folder **\n"
        makelog += subprocess.check_output(
            ["ls", "-p", "-C", "-B",  context["app"]], 
            cwd=clone,
            stderr=subprocess.STDOUT,
            universal_newlines=True)
        makelog += subprocess.check_output(
            ["make", "install"],
            cwd=clone,
            stderr=subprocess.STDOUT,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is
        context["messages"] += makelog
        log.debug("Make output: {}".format(makelog))
        return True
    except subprocess.CalledProcessError as exception:
        log.error("Installation failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += makelog
        context["messages"] += "Encountered exception"
        # context["messages"] += str(exception.output)
        context["messages"] += str("Exception: {}".format(exception))
        return False


def testit(context):
    log.debug("Entering testit")
    clone = context["clone_path"]
    project = context["project"]
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,  "..", "tests", project)
    test_script = os.path.join(test_path, "test.sh")
    port = choose_port()
    context["port"] = port
    assert isinstance(port,str), "Port should be in string form"
    log.debug("Will run on port {}".format(port))

    log.debug("Looking for test script at {}".format(test_path))
    context["messages"] += "\n*** Testing ***\n"
    testlog = "*** Call to subprocess test.sh did not complete ***"
    try:
        log.debug("Args: {}".format([test_script, clone, port]))
        testlog = subprocess.check_output(
            [test_script, clone, port],
            cwd=test_path,
            stderr=subprocess.STDOUT,
            timeout=15,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is?
        testlog += "\n*Automated tests complete*\n"
        context["messages"] = testlog
        log.debug("Testing output: {}".format(testlog))
        return True
    except subprocess.TimeoutExpired as exception:
        log.error("Testing timed out: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += testlog
        context["messages"] += exception.output
        return False
    except subprocess.CalledProcessError as exception:
        log.error("Testing failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += testlog
        context["messages"] += exception.output
        return False


def stylecheck(context):
    log.debug("Entering stylecheck")
    clone = context["clone_path"]
    project = context["project"]
    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir,  "..", "tests", project)
    log.debug("Attempting pycodestyle script at {}".format(test_path))
    testlog = "\n*** PEP 8 standards check ***\n"
    try:
        testlog = subprocess.check_output(
            ["pycodestyle", clone],
            cwd=test_path,
            stderr=subprocess.STDOUT,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is?
        context["messages"] += testlog
        log.debug("Style check output: {}".format(testlog))
        return True
    except subprocess.CalledProcessError as exception:
        log.error("Checking failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += testlog
        context["messages"] += exception.output
        return False
    
def choose_port():
    """Return as string a randomly selected port number in a range that 
    is typically available to user processes, and avoiding those 
    typically used by default in flask and gunicorn.  Not guaranteed to 
    be currently available  (this might be fixed in the future if 
    it turns out to be a problem). 
    """
    port = random.randrange(8500,9999)
    return str(port)


def tmp_path(name, dir="/tmp"):
    """Return a unique local path in /tmp based on name."""
    # While Python's UUID module could do this,
    # we don't need universal uniqueness, so a shorter
    # name based on timestamp will do.  Leading comma
    # encourages daily cleanup.
    ts = arrow.now().timestamp
    return "{}/,{}.{}".format(dir, name[0:8], ts)
