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

from .._future import SubOptions, InputError

class Mole(SubOptions):
    _keys = {
        'verbose', 'unit', 'max_memory', 'cart', 'charge', 'spin',
        'atom', 'basis', 'nucmod', 'ecp', 'pseudo', 'a', 'mesh'
    }

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def _build_task_config(self):
        attrs = self.__dict__
        input_keys = self._keys.intersection(attrs)
        if len(attrs) != len(input_keys):
            unknown = set(attrs).difference(self._keys)
            raise ValueError(f'Unsupported attributes {unknown}')

        kwargs = {k: attrs[k] for k in input_keys}
        if 'atom' not in kwargs:
            raise InputError('Molecule geometry not specified')
        return {
            'method': 'pyscf.M',
            'kwargs': kwargs
        }

    def build(self):
        return self

    def RHF(self):
        from volcengine_qcclient.pyscf.scf import RHF
        return RHF(self)

    def ROHF(self):
        raise NotImplementedError

    def UHF(self):
        from volcengine_qcclient.pyscf.scf import UHF
        return UHF(self)

    def RKS(self, **kwargs):
        from volcengine_qcclient.pyscf.dft import RKS
        return RKS(self, **kwargs)

    def ROKS(self):
        raise NotImplementedError

    def UKS(self, **kwargs):
        from volcengine_qcclient.pyscf.dft import UKS
        return UKS(self, **kwargs)

    def to_cpu(self):
        from pyscf import gto
        mol = gto.Mole()
        attrs = self.__dict__
        input_keys = self._keys.intersection(attrs)
        attrs = {k: attrs[k] for k in input_keys}
        mol.build(False, False, **attrs)
        return mol
