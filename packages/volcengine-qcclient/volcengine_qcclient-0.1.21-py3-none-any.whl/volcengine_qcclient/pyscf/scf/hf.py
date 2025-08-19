# Copyright (2025) Beijing Volcano Engine Technology Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tempfile
import requests
from .._future import Future, create_methods_config, Mole_to_task, to_cpu, load_remote_chkfile

def load_or_run_scf(mf):
    from .._future import create_methods_config, Mole_to_task
    if mf._task_id is None: # SCF not executed
        task_config = mf._build_task_config()
    else:
        # Important to ensure the early SCF done before processing to the next
        # task as the subsequent task relies on the SCF produced chkfile.
        mf.synchronize()
        task_config = create_methods_config(mf, with_return=False)
        task_config = [
            Mole_to_task(mf.mol),
            *task_config,
            # This method recovers SCF instance from the previous job
            {'method': 'load',
             'kwargs': {'key': 'scf', 'task_id': mf._task_id}}
        ]
    return task_config

class SCF(Future):
    _keys = {
        'conv_tol', 'conv_tol_grad', 'conv_tol_cpscf', 'max_cycle', 'init_guess',
        'level_shift', 'direct_scf_tol', 'disp',
    }

    _methods = []
    _return = {
        'scf.converged': 'converged',
        'scf.e_tot': 'e_tot',
        'scf.mo_energy': 'mo_energy',
        'scf.mo_occ': 'mo_occ',
    }

    def __init__(self, mol):
        Future.__init__(self)
        self.mol = mol

    def _build_task_config(self, with_return=True):
        task_config = create_methods_config(self, with_return)
        task_config = [
            Mole_to_task(self.mol),
            *task_config,
            {'method': 'dump', 'kwargs': {'key': 'scf'}},
        ]
        return task_config

    def kernel(self):
        self.run()
    scf = kernel

    def to_cpu(self):
        if self._task_id is None:
            return to_cpu(self)

        self.synchronize()
        self = load_remote_chkfile(self, 'scf')
        mf = to_cpu(self)
        if hasattr(mf, 'grids'):
            mf.grids.mol = mf.mol
        if hasattr(mf, 'nlcgrids'):
            mf.nlcgrids.mol = mf.mol
        return mf

    def density_fit(self, auxbasis=None):
        from volcengine_qcclient.pyscf.df import density_fit
        return density_fit(self, auxbasis)

    def newton(self):
        from volcengine_qcclient.pyscf.soscf import newton
        return newton(self)
    soscf = newton

    def x2c(self):
        raise NotImplementedError
        from volcengine_qcclient.pyscf.x2c import x2c
        return x2c(self)

    def Gradients(self):
        from volcengine_qcclient.pyscf.grad.rhf import Gradients
        return Gradients(self)

    def nuc_grad_method(self):
        return self.Gradients()

    def Hessian(self):
        from volcengine_qcclient.pyscf.hessian.rhf import Hessian
        return Hessian(self)

    def TDA(self):
        from volcengine_qcclient.pyscf.tdscf import TDA
        return TDA(self)

    def TDDFT(self):
        from volcengine_qcclient.pyscf.tdscf import TDDFT
        return TDDFT(self)

    def PCM(self):
        from volcengine_qcclient.pyscf.solvent.pcm import pcm_for_scf
        return pcm_for_scf(self)

    def SMD(self):
        from volcengine_qcclient.pyscf.solvent.smd import smd_for_scf
        return smd_for_scf(self)

    def as_scanner(self):
        raise NotImplementedError

    _load_or_run_scf = load_or_run_scf

class RHF(SCF):
    _methods = ['gpu4pyscf.scf.RHF']
