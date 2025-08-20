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

import torch
import os
from collections.abc import Iterable
from functools import reduce
from magnumnp.common import logging

__all__ = ["ScalarLogger"]

class ScalarLogger(object):
    def __init__(self, filename, columns, every = 1, fsync_every = 1):
        """
        Simple logger class to log scalar values into a tab separated file.

        *Arguments*
            filename (:class:`str`)
                The name of the log file
            columns ([:class:`str` | :class:`function`])
                The columns to be written to the log file
            every (:class:`int`)
                Write row to log file every nth call
            fsync_every (:class:`int`)
                Call fsync every nth write to empty OS buffer

        *Example*
            .. code-block:: python

                # provide key strings with are available in state
                logger = ScalarLogger('log.dat', ['t','m'])

                # provide func(state) or tuple (name, func(state))
                logger = ScalarLogger('log.dat', [('t[ns]', lambda state: state.t*1e9)])

                # provide predifined functions
                logger = ScalarLogger('log.dat', [demag.h, demag.E])

                # Actually log a row
                state = State(mesh)
                logger << state
        """
        # create directory if not existent
        if not os.path.dirname(filename) == '' and \
             not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self._filename = filename
        self._file     = None
        self._every    = every
        self._fsync_every = fsync_every * every
        self._i        = 0
        self._columns  = columns

    def add_column(self, column):
        if self._file is not None:
            raise RuntimeError("You cannot add columns after first log row has been written.")
        self._columns.append(column)

    def log(self, state):
        self._i += 1
        if ((self._i - 1) % self._every > 0):
            return

        values = []

        for column in self._columns:
            if isinstance(column, str):
                name = column
                raw_value = getattr(state, column)
            elif hasattr(column, '__call__'):
                try:
                    name = column.__self__.__class__.__name__ + "." + column.__name__
                except:
                    name = 'unnamed'
                raw_value = column(state)
            elif isinstance(column, tuple) or isinstance(column, list):
                name = column[0]
                raw_value = column[1](state)
            else:
                raise RuntimeError('Column type not supported.')

            if isinstance(raw_value, torch.Tensor):
                value = state.avg(raw_value).tolist()
            else:
                value = raw_value
            values.append((name, value))
        if self._file is None:
            self._file = open(self._filename, 'w')
            self._write_header(values)

        self._write_row(values)
        if ((self._i - 1) % self._fsync_every == 0):
            os.fsync(self._file.fileno())

    def __lshift__(self, state):
        self.log(state)

    def _write_header(self, columns):
        headings = []

        for column in columns:
            if isinstance(column[1], Iterable):
                if (len(column[1]) == 3):
                    for i in ('x', 'y', 'z'):
                        headings.append(column[0] + '_' + i)
                else:
                    for i in range(len(column[1])):
                        headings.append(column[0] + '_' + str(i))
            else:
                headings.append(column[0])

        format_str = "#" + "    ".join(["%-22s"] * len(headings)) + "\n"
        self._file.write(format_str % tuple(headings))
        self._file.flush()

    def _write_row(self, columns):
        flat_values = reduce(lambda x,y: x+y,
            map(lambda x: tuple(x[1]) if isinstance(x[1], Iterable) else (x[1],), columns))
        format_str = "    ".join(["%+.15e"] * len(flat_values)) + "\n"
        self._file.write(format_str % flat_values)
        self._file.flush()

    def __del__(self):
        if self._file is not None:
            self._file.close()

    def resumable_step(self):
        """
        Returns the last step the logger can resume from, e.g. if the logger
        logs every 10th step and the first (i = 0) step was already logged,
        the result is 10.

        *Returns*
            :class:`int`
                The step number the logger is able to resume from
        """
        if self._file is not None:
            raise RuntimeError("Cannot resume from log file that is already open for writing.")

        i = 0
        with open(self._filename, 'r') as f:
            for i, l in enumerate(f):
                pass
        return i * self._every

    def resume(self, i):
        """
        Try to resume existing log file from log step i. The log file
        is truncated accordingly.

        *Arguments*
            i (:class:`int`)
                The log step to resume from
        """
        number = (self.resumable_step() - i) / self._every

        # from https://superuser.com/questions/127786/efficiently-remove-the-last-two-lines-of-an-extremely-large-text-file
        count = 0
        #with open(self._filename, 'r+b') as f:
        #    f.seek(0, os.SEEK_END)
        #    end = f.tell()
        #    while f.tell() > 0:
        #        f.seek(-1, os.SEEK_CUR)
        #        char = f.read(1)
        #        if char != '\n' and f.tell() == end:
        #            raise RuntimeError("Cannot resume: logfile does not end with a newline.")
        #        if char == '\n':
        #            count += 1
        #        if count == number + 1:
        #            f.truncate()
        #            break
        #        f.seek(-1, os.SEEK_CUR)

        with open(self._filename, 'r+b', buffering=0) as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            while f.tell() > 0:
                f.seek(-1, os.SEEK_CUR)
                #print(f.tell())
                char = f.read(1)
                if char != b'\n' and f.tell() == end:
                    raise RuntimeError("Cannot resume: logfile does not end with a newline.")
                    #print ("No change: file does not end with a newline")
                    #exit(1)
                if char == b'\n':
                    count += 1
                if count == number + 1:
                    f.truncate()
                    break
                    #print ("Removed " + str(number) + " lines from end of file")
                    #exit(0)
                f.seek(-1, os.SEEK_CUR)

        self._i = i
        if self._i > 0:
            self._file = open(self._filename, 'a')
