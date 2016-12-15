# -*- coding: utf-8 -*-
#
# blahrgbot
# https://github.com/rmed/blahrgbot
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Rafael Medina García <rafamedgar@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Bot configuration."""

import logging
import os
import sys
from configparser import ConfigParser

from tinydb import TinyDB, Query
from tinydb_smartcache import SmartCacheTable

# Main settings
SETTINGS = {}

# Database
DB = None
SCREAM = Query()

def parse_conf():
    """Parse the configuration file and set relevant variables."""
    conf_path = os.path.abspath(os.getenv('BLAHRG_CONF', ''))

    if not conf_path or not os.path.isfile(conf_path):
        sys.exit('Could not find configuration file')

    parser = ConfigParser()
    parser.read(conf_path)

    # Telegram settings
    SETTINGS['token'] = parser['tg']['token']
    SETTINGS['owner'] = int(parser['tg']['owner'])

    # Media directory
    SETTINGS['media'] = os.path.abspath(parser['media']['path'])

    # TinyDB
    global DB
    DB = TinyDB(parser['db']['path'])
    DB.table_class = SmartCacheTable

def get_logger(name):
    """ Get a logger with the given name. """
    # Base logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Handler to stdout
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Formatting
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(name)s[%(funcName)s]: %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
