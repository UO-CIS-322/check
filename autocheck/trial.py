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
"""

import configparser
import os
import arrow
import subprocess

import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)
log = logging.getLogger(__name__)


CRED_FIELDS = ["author", "repo" ]

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

    ok = ( clone_repo( context)
          and install(context)
          and testit(context))

    log.debug("Returned from clone and install")
    log.debug("Log messages: {}".format(context["messages"]))
    
    return ok

def read_config(path):
    log.debug("Entering read_config")
    config = configparser.ConfigParser()
    config.read(path)
    settings = { }
    for field in CRED_FIELDS:
        settings[field] = config["DEFAULT"].get(field, "not specified")
    return settings
        
def clone_repo( context ):
    """Attempt to clone the repository"""
    log.debug("Entering clone_repo")
    clone_path =  context["clone_path"]
    repo_remote = context["repo_remote"]
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
    log.debug("Entering install")
    clone = context["clone_path"]
    log.debug("Working in directory {}".format(clone))
    makelog = ""
    try:
         makelog = subprocess.check_output(
            ["make", "install"],
            cwd=clone, 
            stderr=subprocess.STDOUT,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is? 
         context["messages"] += makelog
         log.debug("Make output: {}".format(makelog))
         return True
    except subprocess.CalledProcessError as exception: 
        log.error("Installation failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += makelog
        context["messages"] += exception.output
        return False

def testit(context):
    log.debug("Entering testit")
    clone = context["clone_path"]    
    project = context["project"]
    this_dir = os.path.dirname( __file__ )
    test_path = os.path.join(this_dir,  "..", "tests", project)
    test_script = os.path.join(test_path, "test.sh")
    log.debug("Looking for test script at {}".format(test_path))
    try:
        testlog = subprocess.check_output(
            [test_script, clone],
            cwd=test_path, 
            stderr=subprocess.STDOUT,
            # encoding='utf-8' )       # Not supported in Python 3.4
            universal_newlines=True)   # but this is? 
        context["messages"] += testlog
        log.debug("Testing output: {}".format(testlog))
        return True
    except subprocess.CalledProcessError as exception: 
        log.error("Testing failed: {}".format(exception))
        log.error("Output: {}".format(exception.output))
        context["messages"] += testlog
        context["messages"] += exception.output
        return False

       
def tmp_path(name,dir="/tmp"):
    """Return a unique local path in /tmp based on name."""
    # While Python's UUID module could do this,
    # we don't need universal uniqueness, so a shorter
    # name based on timestamp will do.  Leading comma
    # encourages daily cleanup. 
    ts = arrow.now().timestamp
    return "{}/,{}.{}".format(dir,name[0:8],ts)
