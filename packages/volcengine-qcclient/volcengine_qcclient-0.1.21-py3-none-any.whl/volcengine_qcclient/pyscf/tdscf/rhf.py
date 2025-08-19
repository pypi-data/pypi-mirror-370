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

from .._future import (
    Future, create_methods_config, from_pyscf_instance, to_cpu,
    load_remote_chkfile)

class TDA(Future):
    _keys = {'conv_tol', 'nstates', 'singlet', 'lindep', 'level_shift', 'max_cycle'}
    _methods = ['.TDA']
    _return = {
        'tdscf.converged': 'converged',
        'tdscf.e': 'e'
    }

    def __init__(self, mf):
        if not isinstance(mf, Future):
            mf = from_pyscf_instance(mf)
        self._scf = mf
        self._job_client = mf._job_client
        self._task_config = []

    def _build_task_config(self, with_return=True):
        task_config = self._scf._load_or_run_scf()
        task_config.extend(create_methods_config(self, with_return))
        task_config.append(
            {'method': 'dump', 'kwargs': {'key': 'tdscf', 'attrs': 'xy'}})
        return task_config

    def to_cpu(self):
        if self._task_id is None:
            return to_cpu(self)

        self.synchronize()
        self = load_remote_chkfile(self, 'tdscf')
        out = to_cpu(self)
        out.mol = out._scf.mol
        out.verbose = out.mol.verbose
        return out

    def Gradients(self):
        raise NotImplementedError

    def nuc_grad_method(self):
        return self.Gradients()

class TDDFT(Future):
    _keys = {'conv_tol', 'nstates', 'singlet', 'lindep', 'level_shift', 'max_cycle'}
    _methods = ['.TDDFT']
    _return = {
        'tdscf.converged': 'converged',
        'tdscf.e': 'e'
    }

    def __init__(self, mf):
        if not isinstance(mf, Future):
            mf = from_pyscf_instance(mf)
        self._scf = mf
        self._job_client = mf._job_client
        self._task_config = []

    def _build_task_config(self, with_return=True):
        task_config = self._scf._load_or_run_scf()
        task_config.extend(create_methods_config(self, with_return))
        task_config.append(
            {'method': 'dump', 'kwargs': {'key': 'tdscf', 'attrs': 'xy'}})
        return task_config

    to_cpu = TDA.to_cpu

    def Gradients(self):
        raise NotImplementedError

    def nuc_grad_method(self):
        return self.Gradients()

TDHF = TDDFT
