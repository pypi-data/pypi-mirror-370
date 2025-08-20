#
# This file is part of the magnum.np distribution
# (https://gitlab.com/magnum.np/magnum.np).
# Copyright (c) 2023 magnum.np team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import os
import sys

__all__ = ["logger", "set_log_level", "set_log_file", "set_log_script", "debug", "warning", "error", "info", "default", "info_green", "info_blue"]

INFO_GREEN = logging.INFO+5
INFO_BLUE = logging.INFO
DEFAULT = logging.CRITICAL
logging.addLevelName(INFO_GREEN, "INFO")
logging.addLevelName(INFO_BLUE, "INFO")
logging.addLevelName(DEFAULT, "")

# create magnum.fe logger
logger = logging.getLogger('magnum.np')

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt="%(asctime)s  %(name)s:%(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)

logger.setLevel(logging.INFO)

info = logger.info

RED = "\033[1;37;31m%s\033[0m"
BLUE = "\033[1;37;34m%s\033[0m"
GREEN = "\033[1;37;32m%s\033[0m"
CYAN = "\033[1;37;36m%s\033[0m"

def default(message, *args, **kwargs):
    logger.log(DEFAULT, message, *args, **kwargs)

def debug(message, *args, **kwargs):
    logger.debug(CYAN % message, *args, **kwargs)

def warning(message, *args, **kwargs):
    logger.warning(RED % message, *args, **kwargs)

def error(message, *args, **kwargs):
    logger.error(RED % message, *args, **kwargs)

def info_green(message, *args, **kwargs):
    logger.log(INFO_GREEN, GREEN % message, *args, **kwargs)

def info_blue(message, *args, **kwargs):
    logger.log(INFO_BLUE, BLUE % message, *args, **kwargs)

def set_log_level(level):
    """
    Set the log level of magnum.np specific logging messages.
    Defaults to :code:`INFO = 20`.

    *Arguments*
      level (:class:`int`)
        The log level
    """
    logger.setLevel(level)

def set_log_file(filename):
    """
    Store logging output to specified file.

    *Arguments*
        filename (:class:`str`)
    """
    # create directory if not existent
    if not os.path.dirname(filename) == '' and \
         not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    handler = logging.FileHandler(filename, mode='w')
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s  %(name)s:%(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)

def set_log_script(filename):
    """
    Copy run script to specified path

    *Arguments*
        filename (:class:`str`)
    """
    # create directory if not existent
    if not os.path.dirname(filename) == '' and \
         not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    open(filename, 'wb').write(open(sys.argv[0], 'rb').read())
