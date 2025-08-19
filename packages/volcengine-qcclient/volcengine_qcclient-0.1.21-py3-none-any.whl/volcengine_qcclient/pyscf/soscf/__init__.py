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

from .._future import create_methods_config, Mole_to_task

def newton(mf):
    mf_class = mf.__class__
    class SOSCF(mf_class):
        def _build_task_config(self, with_return=True):
            task_config = create_methods_config(self, with_return=False)
            task_config = [
                Mole_to_task(self.mol),
                *task_config,
                {'method': '.newton', 'return': self._return},
                {'method': 'dump', 'kwargs': {'key': 'scf'}},
            ]
            return task_config

        def to_cpu(self):
            print(f'Warn: the SOSCF decorator of {self} is removed')
            return self.view(mf_class).to_cpu()

    new_mf = object.__new__(SOSCF)
    new_mf.__dict__.update(mf.__dict__)
    return new_mf
