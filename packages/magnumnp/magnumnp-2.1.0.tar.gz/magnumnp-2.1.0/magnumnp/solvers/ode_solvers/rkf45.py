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
from magnumnp.common import logging

__all__ = ["RKF45"]

#Runge-Kutta-Fehlberg method with stepsize control
class RKF45(object):
    def __init__(self, f, dt = 1e-15, atol = 1e-5, rtol = 1e-5):
        self._f = f
        self._dt = dt
        self._order = 4

        # Numerical Recipies 3rd Edition suggests these values:
        self._headroom = 0.9
        self._maxstep = 1e-10
        self._minscale = 0.2
        self._maxscale = 10.
        self._atol = atol
        self._rtol = rtol
        logging.info_green("[LLGSolver] using RKF45 solver (atol = %g)" % atol)

    def _try_step(self, t, x, **kwargs):
        f, dt = self._f, self._dt
        kwargs["state"]._dt = dt  # update current dt in state used by thermal field class
        k1 = dt * f(t,              x, **kwargs)
        k2 = dt * f(t +  1./ 4.*dt, x +      1./ 4.*k1, **kwargs)
        k3 = dt * f(t +  3./ 8.*dt, x +      3./32.*k1 +      9./32.*k2, **kwargs)
        k4 = dt * f(t + 12./13.*dt, x + 1932./2197.*k1 - 7200./2197.*k2 + 7296./2197.*k3, **kwargs)
        k5 = dt * f(t +      1.*dt, x +   439./216.*k1 -          8.*k2 + 3680./ 513.*k3 -  845./4104.*k4, **kwargs)
        k6 = dt * f(t +  1./ 2.*dt, x -    8. / 27.*k1 +          2.*k2 - 3544./2565.*k3 + 1859./4104.*k4 - 11./40.*k5, **kwargs)

        dx = 16./135.*k1 + 6656./12825.*k3 + 28561./56430.*k4 - 9./50.*k5 + 2./55.*k6
        rk_error = dx - (25./216.*k1 + 1408./2565.*k3 + 2197./4104.*k4 - 1./5.*k5)
        return x+dx, t+dt, rk_error

    def _optimal_stepsize(self, x, err, atol, rtol):
        norm = torch.linalg.norm((err / (atol + rtol*x.abs())).flatten(), torch.inf)
        if torch.isnan(norm):
            raise RuntimeError("Unexpected error norm= %.5g!" % norm)

        if norm > 1.1:
            # decrease step, no more than factor of 5, but a fraction S more
            # than scaling suggests (for better accuracy)
            r = self._headroom / torch.pow(norm, 1.0/self._order)
            if (r < self._minscale):
                r = self._minscale
        elif norm < 0.5:
            # increase step, but no more than by a factor of 5
            r = self._headroom / torch.pow(norm, 1.0/(self._order+1.0));
            if r > self._maxscale: # increase no more than factor of 5
                r = self._maxscale
            if r < 1.: # don't allow any decrease caused by S<1
                r = 1.
        else: # no change
            r = 1.

        dt_opt = self._dt * r
        if dt_opt > self._maxstep:
            dt_opt = self._maxstep
        return float(dt_opt)

    def step(self, t, x, dt, rtol = None, atol = None, **kwargs):
        t1 = t + dt
        while t < t1:
            _x1, _t1, err = self._try_step(t, x, **kwargs)
            if atol == None:
                atol = self._atol
            dt_opt = self._optimal_stepsize(x, err, atol, rtol or self._rtol)
            if self._dt > dt_opt or self._dt > t1 - t:
                # step size was too large, retry with optimal stepsize
                self._dt = min(dt_opt, t1 - t)
                logging.debug("REVERT step: %g, new step size: %g, time: %g" % (self._dt, dt_opt, t))
            else:
                # accept step, adapt stepsize for next step
                x = _x1
                t = _t1
                logging.debug("ACCEPT step: %g, new step size: %g, time: %g" % (self._dt, dt_opt, t))
                self._dt = dt_opt
                kwargs["state"]._step += 1
        return t, x
