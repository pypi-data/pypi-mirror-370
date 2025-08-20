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

from magnumnp.common import timedmethod, constants
from magnumnp.field_terms import LinearFieldTerm
import torch

__all__ = ["IntergrainExchangeField", "RKKYField", "BiquadraticRKKYField"]

class IntergrainExchangeField(LinearFieldTerm):
    r"""
    Intergrain - Exchange interaction between two domains gives rise to the following energy contribution:

    .. math::

        E^\text{iex} = -\int\limits_\Gamma J_\text{iex} \, \vec{m}_i \cdot \vec{m}_j \, d\vec{A},

    where :math:`\Gamma` is the interface between two layers :math:`i` and :math:`j`
    with magnetizations :math:`\vec{m}_i` and :math:`\vec{m}_j`, respectively.

    :Example:

      .. code::

        # create state with named domains from mesh
        state = State(mesh)
        state.material["iex"] = J_iex

        # create domains as bool arrays, e.g:
        domain1 = torch.zeros(n, dtype=torch.bool)
        domain1[n[0]//2:,:,:] = True

        domain2 = torch.zeros(n, dtype=torch.bool)
        domain2[:-n[0]//2:,:,:] = True

        # rotate magnetization within one subdomain
        state.m[domain1] = torch.tensor([np.cos(phi), np.sin(phi), 0])

        # without interface layer, two seperate exchange fields need to be defined
        exchange1 = ExchangeField(Aex1, domain1)
        exchange2 = ExchangeField(Aex2, domain2)
        iex = IntergrainExchangeField(domain1, domain2)
    """
    def __init__(self, domain1, domain2):
        self._domain1 = domain1
        self._domain2 = domain2

    @timedmethod
    @torch.compile
    def h(self, state):
        m1 = state.m * state.material["iex"]
        m2 = m1.clone()
        m1[~self._domain1] = 0
        m2[~self._domain2] = 0

        # sum h1 over all next neighbors
        h1 = m1*0.
        h1[:-1,:,:,:] += m2[ 1:,:,:,:] / state.mesh.dx[0]
        h1[ 1:,:,:,:] += m2[:-1,:,:,:] / state.mesh.dx[0]

        h1[:,:-1,:,:] += m2[:, 1:,:,:] / state.mesh.dx[1]
        h1[:, 1:,:,:] += m2[:,:-1,:,:] / state.mesh.dx[1]

        h1[:,:,:-1,:] += m2[:,:, 1:,:] / state.mesh.dx[2]
        h1[:,:, 1:,:] += m2[:,:,:-1,:] / state.mesh.dx[2]

        # sum h2 over all next neighbors
        h2 = m2*0.
        h2[:-1,:,:,:] += m1[ 1:,:,:,:] / state.mesh.dx[0]
        h2[ 1:,:,:,:] += m1[:-1,:,:,:] / state.mesh.dx[0]

        h2[:,:-1,:,:] += m1[:, 1:,:,:] / state.mesh.dx[1]
        h2[:, 1:,:,:] += m1[:,:-1,:,:] / state.mesh.dx[1]

        h2[:,:,:-1,:] += m1[:,:, 1:,:] / state.mesh.dx[2]
        h2[:,:, 1:,:] += m1[:,:,:-1,:] / state.mesh.dx[2]

        h = m1 * 0.
        h[self._domain1] = h1[self._domain1]
        h[self._domain2] = h2[self._domain2]

        h /= constants.mu_0 * state.material["Ms"]
        return h.nan_to_num(posinf=0, neginf=0)




# TODO: interface should be generalized and simplified
class RKKYField(object):
    r"""
    Interlayer-Exchange interaction between two layers gives rise to the following energy contribution:

    .. math::

        E^\text{rkky} = -\int\limits_\Gamma J_\text{rkky} \, \vec{m}_i \cdot \vec{m}_j \, d\vec{A},

    where :math:`\Gamma` is the interface between two layers :math:`i` and :math:`j`
    with magnetizations :math:`\vec{m}_i` and :math:`\vec{m}_j`, respectively.

    Special care has to be taken, if domain walls or partial domain walls are formed across the RKKY interface.
    In this case higher order approximations of the magnetization needs to be used near the interface in order to
    accurately describe e.g. the equilibrium magnetization or critical switching fields.
    (see Suess et al. "Accurate finite difference micromagnetic of magnetis including RKKY interaction -- analytical solution and comparision to standard micromagnetic codes")

    :param J_rkky: Interlayer-Exchange constant :math:`J_\text{rkky}`
    :type J_rkky: float
    :param dir: normal direction of the interface (currently "z" is hard-coded")
    :type filename: str
    :param id1: Index of the first layer
    :type id1: int
    :param id2: Index of the second layer
    :type id2: int
    :param order: appoximation order of the magnetization near the interface (default = 0)
    :type order: int, optional

    :Example:

      .. code::

        # create state with named domains from mesh
        state = State(mesh)

        # create domains as bool arrays, e.g:
        domain1 = torch.zeros(n, dtype=torch.bool)
        domain1[n[0]//2:,:,:] = True

        domain2 = torch.zeros(n, dtype=torch.bool)
        domain2[:-n[0]//2:,:,:] = True

        # rotate magnetization within one subdomain
        state.m[domain1] = torch.tensor([np.cos(phi), np.sin(phi), 0])

        # without interface layer, two seperate exchange fields need to be defined
        exchange1 = ExchangeField(Aex1, domain1)
        exchange2 = ExchangeField(Aex2, domain2)
        rkky = RKKYField(J_rkky, "z", id1, id2)
    """
    def __init__(self, J_rkky, dir, id1, id2, order = 0):
        self._J_rkky = J_rkky
        if dir != "z":
            raise ValueError("Currently only dir='z' is implemented!")
        self._dir = dir #TODO: dir is ignored
        self._id1 = min(id1,id2)
        self._id2 = max(id1,id2)
        self._order = order

    @timedmethod
    @torch.compile
    def h(self, state):
        h = torch.zeros_like(state.m)
        dz = state.mesh.dx_tensor[2].reshape(1,1,-1,1)
        if self._order != 0 and not state.mesh.is_equidistant:
            raise ValueError("[RKKYField] higher order RKKY is only implemented for equidistant fields! (use order=0)")
        if self._order == 0:
            m1 = state.m[:,:,(self._id1,),:]
            m2 = state.m[:,:,(self._id2,),:]
        elif self._order == 1:
            m1 = 1.5 * state.m[:,:,(self._id1,),:] - 0.5 * state.m[:,:,(self._id1-1,),:]
            m2 = 1.5 * state.m[:,:,(self._id2,),:] - 0.5 * state.m[:,:,(self._id2+1,),:]
        elif self._order == 2:
            m1 = 15./8. * state.m[:,:,(self._id1,),:] - 5./4. * state.m[:,:,(self._id1-1,),:] + 3./8.* state.m[:,:,(self._id1-2,),:]
            m2 = 15./8. * state.m[:,:,(self._id2,),:] - 5./4. * state.m[:,:,(self._id2+1,),:] + 3./8.* state.m[:,:,(self._id2+2,),:]

        h[:,:,(self._id1,),:] = self._J_rkky * (m2 - (m1*m2).sum(axis = 3, keepdim=True) * m1)
        h[:,:,(self._id2,),:] = self._J_rkky * (m1 - (m1*m2).sum(axis = 3, keepdim=True) * m2)

        h /= constants.mu_0 * state.material["Ms"] * dz
        return h.nan_to_num(posinf=0, neginf=0)

    @torch.compile
    def E(self, state):
        m1 = state.m[:,:,(self._id1,),:]
        m2 = state.m[:,:,(self._id2,),:]
        dx = state.mesh.dx_tensor[0].reshape(-1,1,1,1)
        dy = state.mesh.dx_tensor[1].reshape(1,-1,1,1)
        if self._order == 1:
            m1 += 0.5 * ( state.m[:,:,(self._id1,),:] - state.m[:,:,(self._id1-1,),:])
            m2 += 0.5 * (-state.m[:,:,(self._id2,),:] + state.m[:,:,(self._id2+1,),:])
        elif self._order == 2:
            m1 += 0.25 * (3*state.m[:,:,(self._id1,),:] - 4*state.m[:,:,(self._id1-1,),:] + state.m[:,:,(self._id1-2,),:])
            m2 += 0.25 * (3*state.m[:,:,(self._id2,),:] - 4*state.m[:,:,(self._id2+1,),:] + state.m[:,:,(self._id2+2,),:])

        E = -(dx * dy * self._J_rkky * m1 * m2).sum()
        return E


# TODO: interface should be generalized and simplified
class BiquadraticRKKYField(object):
    r"""
    Biquadratic surface exchange couplong between two layers gives rise to the following energy contribution:

    .. math::

        E^\text{biquadratic} = -\int\limits_\Gamma J_\text{biquadratic} \, (\vec{m}_i \cdot \vec{m}_j)^2 \, d\vec{A},

    where :math:`\Gamma` is the interface between two layers :math:`i` and :math:`j` with magnetizations :math:`\vec{m}_i` and :math:`\vec{m}_j`, respectively.

    The effective field is given by:

    .. math::

        \vec{h}^\text{biquadratic}_i = \frac{2 J_\text{biquadratic}} {M_s \Delta z \mu_0} \, (\vec{m}_i \cdot \vec{m}_j) \, \vec{m}_j,

    with the interlayer exchange constant :math:`J_\text{biquadratic}`.
    """
    def __init__(self, J_rkky_BQ, dir, id1, id2):
        self._J_rkky_BQ = J_rkky_BQ
        if dir != "z":
            raise ValueError("Currently only dir='z' is implemented!")
        self._dir = dir
        self._id1 = min(id1,id2)
        self._id2 = max(id1,id2)

    @timedmethod
    @torch.compile
    def h(self, state):
        h = torch.zeros(state.mesh.n + (3,))
        dz = state.mesh.dx_tensor[2].reshape(1,1,-1,1)

        m1 = state.m[:,:,self._id1,:]
        m2 = state.m[:,:,self._id2,:]

        m12 = (m1*m2).sum(axis=-1, keepdim=True)
        h[:,:,self._id1,:] = 2. * self._J_rkky_BQ * m12 * m2
        h[:,:,self._id2,:] = 2. * self._J_rkky_BQ * m12 * m1

        #TODO: find out why there is a 2x discrepancy compared with oommf
        h /= constants.mu_0 * state.material["Ms"] * dz

        return h.nan_to_num(posinf=0, neginf=0)

    @torch.compile
    def E(self, state):
        m1 = state.m[:,:,self._id1,:]
        m2 = state.m[:,:,self._id2,:]
        dx = state.mesh.dx_tensor[0].reshape(-1,1,1)
        dy = state.mesh.dx_tensor[1].reshape(1,-1,1)

        E = -dx * dy * self._J_rkky_BQ * (m1*m2).sum(dim=-1,keepdim=True)**2
        return E.sum()
