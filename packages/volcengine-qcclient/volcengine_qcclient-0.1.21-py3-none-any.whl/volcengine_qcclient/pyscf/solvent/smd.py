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

from .._future import SubOptions

def smd_for_scf(mf):
    mf_class = mf.__class__
    class SMD_SCF(mf_class):
        _keys = {'with_solvent'}
        _methods = mf_class._methods + ['gpu4pyscf.solvent.SMD']
        _return = {
            **mf_class._return,
            'solvent.e': 'with_solvent.e',
        }

        def to_cpu(self):
            mf = self.view(mf_class).to_cpu().SMD()
            mf.with_solvent.__dict__.update(self.with_solvent.__dict__)
            return mf

    new_mf = object.__new__(SMD_SCF)
    new_mf.__dict__.update(mf.__dict__)
    new_mf.with_solvent = SMD()
    return new_mf

class SMD(SubOptions):
    _keys = {
        'method', 'solvent', 'r_probe', 'sasa_ng'
    }
