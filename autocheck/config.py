"""
Configure the auto-checker from 
   config.ini
   command line
in that order (i.e., in opposite order of precedence). 

A configuration namespace module returned by this module is 
suitable for configuring the Flask applicaton object.  
FIXME:  Test this

configparser makes all configuration variables  lower case; 
Flask configuration object recognizes only upper case configuration 
variables.  To resolve this conflict, we convert all configuration
variables from .ini files to upper case. 


Potential extensions: 
  - Read multiple configuration files? (configparser can)
  - Use environment variables?  With what precedence relative 
    to configuration files? 
"""

import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.DEBUG)
log = logging.getLogger(__name__)


import configparser
import argparse

def command_line_args():
    """Returns namespace with settings from command line"""
    log.debug("-> Command line args")
    parser = argparse.ArgumentParser(description="CIS 322 Auto-Checker")
    parser.add_argument("-D", "--debug", dest="DEBUG",
                            action="store_const", const=True, 
                            help="Turn on debugging and verbose logging")
    parser.add_argument("-P", "--port", type=int, dest="PORT",
                            help="Port for Flask built-in server (only)")
    parser.add_argument("-C", "--config", type=str,
                            help="Alternate configuration file")
    parser.add_argument("--project", type=str,
                            help="Use configuration section")
    cli_args = parser.parse_args()
    log.debug("<- Command line args: {}".format(cli_args))
    return cli_args

def config_file_args(config_file_path, project=None):
    """Returns dict of values from the configuration file. 
    If the project kwarg is provided, we will take configuration 
    values from that section of the configuration file. 
    """
    log.debug("-> config file args")
    config = configparser.ConfigParser()
    config.read(config_file_path)
    section = project or "DEFAULT"
    args = config[section]
    log.debug("<- config file args: {}".format(args))
    return args

def imply_types(ns: dict):
    """Convert values to implied types.  We assume that strings of 
    digits should be integers, and True/False (with any casing) should 
    be boolean. """
    for var in ns:
        val = ns[var]
        if type(val) != str :
            continue
        if val.lower() == "true":
            ns[var] = True
        elif val.lower() == "false":
            ns[var] = False
        elif val.isdecimal():
            ns[var] = int(val)
            

def configuration():
    """
    Returns namespace (that is, object) of configuration 
    values, giving precedence to command line arguments over 
    configuration file values. 
    """
    log.debug("-> configuration")
    cli = command_line_args()
    cli_vars = vars(cli)  # Access the namespace as a dict
    log.debug("CLI variables: {}".format(cli_vars))
    config_file_path = cli_vars.get("config") or "config.ini"
    log.debug("Will read configuration file from '{}'".format(config_file_path))
    config_for_project = cli_vars.get("project", None)
    ini = config_file_args(config_file_path, config_for_project)
    log.debug("Config file args: {}".format(ini))
    # Fold into cli namespace with precedence for command line arguments
    for var_lower in ini:
        var_upper = var_lower.upper()
        log.debug("Variable '{}'".format(var_upper))
        if var_upper in cli_vars and cli_vars[var_upper]: 
            log.debug("Overridden by cli val '{}'".format(cli_vars[var_upper]))
        else: 
            log.debug("Storing in cli")
            cli_vars[var_upper] = ini[var_lower]

    imply_types(cli_vars)
        
    return cli


