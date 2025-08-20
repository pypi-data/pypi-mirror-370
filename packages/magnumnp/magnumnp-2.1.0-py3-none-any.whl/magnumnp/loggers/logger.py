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
from magnumnp.loggers import ScalarLogger, FieldLogger
from magnumnp.common import logging

__all__ = ["Logger"]

class Logger(object):
    """
    Combined Scalar- and Field-Logger class

    *Arguments*
        directory (:class:`str`)
            The name of the log file
        scalars ([:class:`str` | :class:`function`])
            The columns to be written to the log file
        scalars_every (:class:`int`)
            Write scalar to log file every nth call
        fields ([:class:`str` | :class:`function`])
            The columns to be written to the log file
        fields_every (:class:`int`)
            Write fields to log file every nth call

    *Example*
        .. code-block:: python

            # provide key strings with are available in state
            logger = Logger('data', ['m', demag.h], ['m'], fields_every = 100)

            # Actually log fields
            state = State(mesh)
            logger << state
    """
    def __init__(self, directory, scalars = [], fields = [], scalars_every = 1, fields_every = 1):
        self.loggers = {}
        self._resume_time = None
        if len(scalars) > 0:
            self.loggers["scalars"] = ScalarLogger(os.path.join(directory, "log.dat"), scalars, every = scalars_every)
        if len(fields) > 0:
            self.loggers["fields"] = FieldLogger(os.path.join(directory, "fields.pvd"), fields, every = fields_every)

    def log(self, state):
        if state.t == self._resume_time: # avoid logging directly after resume
            self._resume_time = None
            return
        for logger in self.loggers.values():
            logger << state

    def __lshift__(self, state):
        self.log(state)

    def resume(self, state):
        """
        Tries to resume from existing log files. If resume is possible
        the state object is updated with latest possible values of t
        and m and the different log files are aligned and resumed.
        If resume is not possible the state is not modiefied and the
        simulations starts from the beginning.

        *Arguments*
            state (:class:`State`)
                The state to be resumed from the log data
        """
        last_recorded_step = self.loggers["fields"].last_recorded_step()
        if last_recorded_step is None:
            logging.warning("Resume not possible. Start over.")
            return

        resumable_step = min(map(lambda logger: logger.resumable_step(), self.loggers.values()))
        assert resumable_step >= last_recorded_step + 1

        state.m, state.t = self.loggers["fields"].step_data(last_recorded_step, "m")
        logging.info_green("Resuming from step %d (t = %g)." % (last_recorded_step, state.t))

        for logger in self.loggers.values():
            logger.resume(last_recorded_step + 1)

        self._resume_time = state.t

    def is_resumable(self):
        """
        Returns True if logger can resume from log files.

        *Returns*
            :class:`bool`
                True if resumable, False otherwise
        """
        return self.loggers["fields"].last_recorded_step() is not None
