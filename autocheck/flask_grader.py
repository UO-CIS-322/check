"""
Flask app gets project description
including github URL

"""

import os
import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from werkzeug.utils import secure_filename

import json
import logging
import config       # Reads from config.ini and command line

import arrow        # For timestamp in file name creation
import subprocess   # Installation process

import trial  # The part of auto-grading that does not depend on flask

###
# Globals
###
app = flask.Flask(__name__)
proxied = __name__ != "__main__"
CONFIG = config.configuration(proxied=proxied)
app.config.from_object(CONFIG)
app.logger.debug("Configuration: {}".format(app.config))

# config = configparser.ConfigParser()
app.logger.debug("Uploads to '{}'".format(app.config["UPLOAD_FOLDER"]))
MAX_CONTENT_LENGTH = 64 * 1024  # 64K is plenty for a config file


###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template("index.html")


@app.route('/_upload', methods=['POST'])
def upload_project():
    """Upload of credentials file for
    checking. There are several steps, each enabling the next, and none
    requiring intervention if successful.  Each step is a Python
    function which is executed in the request context and can call
    flask.flash to report progress or problems.  Each step may return a
    truthy value to enable the next step, or a falsy value to indicate
    that the submit/build/run process has failed.  We pass along a
    dictionary in which we stash useful information along the way.
    """
    app.logger.debug("Entering _upload")
    credentials_path = tmp_path("cred.ini")

    # The remainder of the processing should be in trial.py.
    # We give trial the path to a credentials file and a
    # context into which it can place messages.
    context = {"credentials": credentials_path,
               "messages":  ""
               }

    proj_app = flask.request.form["project"]
    app.logger.debug("Project+App is {}".format(proj_app))
    proj, projname = proj_app.split(":")
    app.logger.debug("Project: {}".format(proj))
    app.logger.debug("App: {}".format(projname))

    context["project"] = proj  # Example proj0, proj1, etc
    context["app"] = projname  # Example hello, pageserver, etc


    # The credentials upload step is within the flask
    # context, and
    ok = (check_file_upload(request)
          and upload_credentials(context))
    app.logger.debug("Uploaded credentials to {}".format(credentials_path))
    if not ok:
        flask.flash("Credentials upload failed")
        return flask.render_template("failed.html")
        # return flask.redirect(url_for("index"))
    app.logger.debug("Preparing call-out to trial module")
    ok = trial.trial(context)
    app.logger.debug("Returned from trial module")
    # For the display ... 
    flask.g.messages = context["messages"]
    flask.g.port = context["port"]
    # For subsequent steps (after current state is lost)
    flask.session["clone_path"] = context["clone_path"]
    flask.session["project"] = context["project"]
    if ok:
        flask.g.status = "OK"
    else:
        flask.g.status = "Errors"


    return flask.render_template("test_output.html")

@app.route("/_kill")
def _kill():
    # Here: Kill the job
    context = { "project": flask.session["project"],
                "clone_path": flask.session["clone_path"], 
                "messages": "Attempting shut down"
              }
    
    trial.shutdown(context)
    flask.flash("Should kill off process using PID in {}"
                      .format(context["clone_path"]))
    flask.flash(context["messages"])
    return flask.redirect(flask.url_for("index"))

##################
#
# Functions used by routes
#
##################


def check_file_upload(request):
    """Attempt to upload a credentials file.
    If successful, returns True and leaves file
    at grading_path/credentials.ini.
    If disallowed or unsuccessful, returns False.
    """
    if 'cfgfile' not in request.files:
        flash('No file part')
        return False
    file = request.files['cfgfile']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return False
    if not allowed_file(file.filename):
        flash("File name is not permitted: {}".format(file.filename))
        return False
    return True


def upload_credentials(project_context):
    """Attempt to upload the credentials file"""
    file = request.files['cfgfile']
    credentials_path = project_context["credentials"]
    try:
        file.save(credentials_path)
        flash('file uploaded to {}'.format(credentials_path))
        return True
    except Exception as e:
        flask.flash("Failed to upload credentials file; unknown problem")
        flask.flash("Encountered this exception: {}".format(e))
        return False


def allowed_file(filename):
    """May the user upload files named liked this?"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "ini"


def tmp_path(name, dir=app.config["UPLOAD_FOLDER"]):
    """Return a unique local path in /tmp based on name."""
    # While Python's UUID module could do this,
    # we don't need universal uniqueness, so a shorter
    # name based on timestamp will do.  Leading comma
    # encourages daily cleanup.
    ts = arrow.now().timestamp
    return "{}/,{}.{}".format(dir, name[0:8], ts)


##################
#
# Error handling
#
##################


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


@app.errorhandler(403)
def page_not_found(error):
    app.logger.debug("403: Forbidden")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('403.html'), 403


@app.errorhandler(500)
def page_not_found(error):
    app.logger.debug("500: Internal error")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('500.html'), 500


#################
#
# Functions used within the templates
#
#################

@app.template_filter('fmtdate')
def format_arrow_date(date):
    try:
        normal = arrow.get(date)
        return normal.format("ddd MM/DD/YYYY")
    except ParserError:
        return "(bad date {})".format(date)


#############
#
# Set up to run in gunicorn or
# stand-alone.
#
app.secret_key = "fixme please"
if __name__ == "__main__":
    print("Opening for global access on port {}".format(5000))
    app.run(port=5000, host="0.0.0.0")
