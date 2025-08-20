from .version import __version__

# -*- coding: utf-8 -*-

###
# © 2018 The Board of Trustees of the Leland Stanford Junior University
# Nathaniel Watson
# nathankw@stanford.edu
###

"""An API and scripts for submitting datasetss to the IGVF Portal.
"""

import os
import json
import logging
import sys

# see to it that only upper-case vars get exported
package_path = __path__[0]

# Define constants for a few properties that are common to all IGVF profiles:

#: The award property name that is common to all IGVF Portal object profiles.
AWARD_PROP_NAME = "award"

#: The aliases property name that is common to almost all IGVF Portal object profiles.
#: Notably, the following profiles lack this property as of 2018-04-03:
#: ['access_key_admin', 'publication', 'award', 'organism', 'page', 'image', 'user', 'lab']
ALIAS_PROP_NAME = "aliases"

#: The lab property name that is common to all IGVF Portal object profiles.
LAB_PROP_NAME = "lab"

#: dict. Stores the lab property to the value of the environment variable `IGVF_LAB` to serve as
#: the default lab when submitting an object to the Portal.
#: ``igvf_utils.connection.Connection.post()`` will use this default if this property doesn't
#: appear in the payload.
LAB = {}
try:
    LAB = {LAB_PROP_NAME: os.environ["IGVF_LAB"]}
except KeyError:
    pass

#: str. Stores the prefix to add to each record alias when doing a POST operation.
#: Most profiles have an 'alias' key, which stores a list of alias names that are
#: useful to the lab. When POSTING objects to the Portal, these aliases must be prefixed
#: with the lab name and end with a colon, and this configuration variable stores that
#: prefix value.
LAB_PREFIX = ""
if LAB:
    LAB_PREFIX = LAB[LAB_PROP_NAME] + ":"

#: dict. Stores the award property to the value of the environment variable `IGVF_AWARD` to act as
#: the default award when submiting an object to the Portal.
#: ``igvf_utils.connection.Connection.post()`` will use this default if this property doesn't
#: appear in the payload, and the profile at hand isn't a member of the list
#: ``igvf_utils.utils.Profile.AWARDLESS_PROFILES``.
AWARD = {}
try:
    AWARD = {AWARD_PROP_NAME: os.environ["IGVF_AWARD"]}
except KeyError:
    pass

#: The relative ENCODE Portal URL that points to all the profiles (schemas).
PROFILES_URL = "profiles"

IGVF_SANDBOX_MODE = "sandbox"
IGVF_PROD_MODE = "prod"

#: A hash of known hosts one can connect to, where the key can be passed to the `igvf_mode` argument
#: when instantiating the `connection.Connection` class.
IGVF_MODES = {
    IGVF_SANDBOX_MODE: {"url": "https://api.sandbox.igvf.org/"},
    IGVF_PROD_MODE: {"url": "https://api.data.igvf.org/"}
}

#: The timeout in seconds when making HTTP requests via the ``requests`` module.
TIMEOUT = 60

#: The name of the debug ``logging`` instance.
DEBUG_LOGGER_NAME = "iu_debug"
#: The name of the error ``logging`` instance created in ``igvf_utils.connection.Connection()``,
#: and referenced elsewhere.
ERROR_LOGGER_NAME = "iu_error"
#: The name of the POST ``logging`` instance created in ``igvf_utils.connection.Connection()``,
#: and referenced elsewhere.
POST_LOGGER_NAME = "iu_post"

#: A ``logging`` instance that logs all messages sent to it to STDOUT.
debug_logger = logging.getLogger(DEBUG_LOGGER_NAME)
level = logging.DEBUG
debug_logger.setLevel(level)
f_formatter = logging.Formatter('%(asctime)s:%(name)s:\t%(message)s')
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(level)
ch.setFormatter(f_formatter)
debug_logger.addHandler(ch)

#: A ``logging`` instance that accepts messages at the ERROR level. 
error_logger = logging.getLogger(ERROR_LOGGER_NAME)
error_logger.setLevel(logging.ERROR)

del package_path
