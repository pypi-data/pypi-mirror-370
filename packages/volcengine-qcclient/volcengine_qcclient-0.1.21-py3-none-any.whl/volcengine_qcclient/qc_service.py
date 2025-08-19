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

# coding:utf-8
import json
import os
import threading
from urllib.parse import urlparse

from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from volcengine.base.Service import Service


class QcService(Service):
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(QcService, '_instance'):
            with QcService._instance_lock:
                if not hasattr(QcService, '_instance'):
                    QcService._instance = object.__new__(cls)
        return QcService._instance

    def __init__(self, endpoint='https://open.volcengineapi.com', region='cn-beijing'):
        self.service_info = QcService.get_service_info(endpoint, region)
        self.api_info = QcService.get_api_info()
        super(QcService, self).__init__(self.service_info, self.api_info)

    @staticmethod
    def get_service_info(endpoint, region):
        parsed = urlparse(endpoint)
        scheme, hostname = parsed.scheme, parsed.hostname
        if not scheme or not hostname:
            raise Exception(f'invalid endpoint format: {endpoint}')
        service_code = os.getenv('QC_SERVICE_CODE', 'mlp_ai4s')
        service_info = ServiceInfo(hostname, {'Accept': 'application/json'},
                                   Credentials('', '', service_code, region), 10, 30, scheme=scheme)
        return service_info

    @staticmethod
    def get_api_info():
        api_info = {
            'CreateQcService':
                ApiInfo('POST', '/', {'Action': 'CreateQcService', 'Version': '2024-11-15'}, {}, {}),
            'ListQcServices':
                ApiInfo('POST', '/', {'Action': 'ListQcServices', 'Version': '2024-11-15'}, {}, {}),
            'UpdateQcService':
                ApiInfo('POST', '/', {'Action': 'UpdateQcService', 'Version': '2024-11-15'}, {}, {}),
            'StopQcService':
                ApiInfo('POST', '/', {'Action': 'StopQcService', 'Version': '2024-11-15'}, {}, {}),
            'DeleteQcService':
                ApiInfo('POST', '/', {'Action': 'DeleteQcService', 'Version': '2024-11-15'}, {}, {}),
            'SubmitQcTasks':
                ApiInfo('POST', '/', {'Action': 'SubmitQcTasks', 'Version': '2024-11-15'}, {}, {}),
            'ListQcTasks':
                ApiInfo('POST', '/', {'Action': 'ListQcTasks', 'Version': '2024-11-15'}, {}, {}),
            'GetQcTasksSummary':
                ApiInfo('POST', '/', {'Action': 'GetQcTasksSummary', 'Version': '2024-11-15'}, {}, {}),
            'StopQcTasks':
                ApiInfo('POST', '/', {'Action': 'StopQcTasks', 'Version': '2024-11-15'}, {}, {}),
            'RetryQcTasks':
                ApiInfo('POST', '/', {'Action': 'RetryQcTasks', 'Version': '2024-11-15'}, {}, {}),
            'ListQcBatchJobs':
                ApiInfo('POST', '/', {'Action': 'ListQcBatchJobs', 'Version': '2024-11-15'}, {}, {}),
        }
        return api_info

    def create_qc_service(self, params):
        """ 创建量化计算任务

        Args:
            params (Dict):

                `Name (str)`: 必选, 量化计算服务名称
                    示例值: qcservice-test

                `Description (str)`: 选填, 量化计算服务描述
                    示例值: description

                `ServiceType (str)`: 必选, 量化计算服务类型
                    示例值: GPU4PySCF:1.1.0

                `Min (int)`: 选填, 最小容器数
                    示例值: 0
                `Max (int)`: 选填, 最大容器数
                    示例值: 10

        Returns:
            Dict:

                `Id (str)`: 量化计算服务 ID
                    示例值: qcsvc-xxxxx

        """
        return self.__request('CreateQcService', params)

    def list_qc_services(self, params):
        """ 列举量化计算任务
        Args:
            params (Dict):
                `Ids (List[str])`: 选填, 量化计算服务ID列表。若设置,则忽略`NameContains`和`Status`
                    示例值: [qcsvc-xxxx]
                `NameContains (str)`: 选填, 量化计算服务名称。支持模糊匹配。
                    示例值: xxx
                `Status`: 选填, 量化计算服务状态, 取值有Enabled Disabled
                    示例值: Enabled
                `SortBy (str)`: 选填, 按字段排序 取值有Name CreateTime UpdateTime
                    示例值: CreateTime
                `SortOrder (str)`: 选填, 指定排序顺序 取值有Asc Desc
                    示例值: Desc
                `PageNumber (int)`: 选填, 页码, 从 1 开始
                    示例值: 1
                `PageSize (int)`: 选填, 每页的数量
                    示例值: 10
        Returns:
            Dict:

                `Items (List[Dict])`: 量化计算服务列表

                    `Id (str)`: 量化计算服务ID
                        示例值: qcsvc-xxxx

                    `Name (str)`: 量化计算服务名称
                        示例值: name

                    `Status (str)`: 量化计算服务状态
                        示例值: Enabled

                    `Description (str)`: 量化计算服务描述
                        示例值: description

                    `CreatorUserId` (int)`: 创建者ID
                        示例值: 123456

                    `ServiceType (str)`: 服务类型
                        示例值: GPU4PySCF:1.1.0

                    `Min (int)`: 最小容器数
                        示例值: 0

                    `Max (int)`: 最大容器数
                        示例值: 0

                    `Desire (int)`: 期望容器数
                        示例值: 0

                    `Current (int)`: 当前容器数
                        示例值: 0

                    `CreateTime (str)`: 量化计算服务创建时间
                        示例值: 2024-07-01T00:00:00Z

                    `UpdateTime (str)`: 量化计算服务更新时间
                        示例值: 2024-07-01T00:00:00Z

                `PageNumber (int)`: 页码
                    示例值: 1

                `PageSize (int)`: 页长
                    示例值: 10

                `TotalCount (int)`: 总数量
                    示例值: 10

        """
        return self.__request('ListQcServices', params)

    def update_qc_service(self, params):
        """ 更新量化计算任务
        Args:
            params (Dict):
                `Id (str)`: 必选, 量化计算服务 ID
                    示例值: qcsvc-xxxx

                `Name (str)`: 选填, 量化计算服务名称
                    示例值: name

                `Description (str)`: 选填, 量化计算服务描述
                    示例值: description

                `Min (int)`: 选填, 最小容器数
                    示例值: 0

                `Max (int)`: 选填, 最大容器数
                    示例值: 0

        Returns:
            Dict:
                `ID (str)`: 量化计算服务 ID
                    示例值: qcsvc-xxxxxxx
        """
        return self.__request('UpdateQcService', params)

    def stop_qc_service(self, params):
        """ 停止量化计算任务
        Args:
            params (Dict):
                `Id (str)`: 必选, 量化计算服务 Id
                    示例值: qcsvc-xxxxx

        Returns:
            Dict:
                `Id (str)`: 量化计算服务 Id
                    示例值: qcsvc-xxxxx
        """
        return self.__request('StopQcService', params)

    def delete_qc_service(self, params):
        """ 删除量化计算任务
        Args:
            params (Dict):
                `Id (str)`: 必选, 量化计算服务 Id
                    示例值: qcsvc-xxxxx

        Returns:
            Dict:
                `Id (str)`: 量化计算服务 Id
                    示例值: qcsvc-xxxxx
        """
        return self.__request('DeleteQcService', params)

    def submit_qc_tasks(self, params):
        """ 提交量化计算任务
        Args:
            params (Dict):
                `QcServiceId (str)`: 必选, 量化计算服务 ID
                    示例值: qcsvc-xxxxx

                `TaskType (str)`: 必选, 任务类型。 取值有: opt, sp
                    示例值: opt

                `Label` (str): 选填, 任务标签。若不填则自动生成。
                    示例值: xxxxx

                `QcTasks (List[Dict])`: 必选, 任务列表

                    `MoleculeName` (str): 选填, 分子名称

                    `MoleculeUrl` (str): 选填, 已上传的 xyz 分子文件的 tos 地址。
                        示例值: molecule.xyz

                    `MoleculeXyzData` (str): 选填, base64编码后的xyz分子内容。
                        示例值: xxx

                    `QcTaskConfig` (Dict): 选填, 任务配置。
                        `timeout`(int): 选填, 超时时间 单位为秒 默认值为604800 (7天)
                            示例值: 3600
                        `spin`(int): 选填,
                            示例值: 0
                        `charge(int)`: 选填,
                            示例值: -1
                        `basis`(str): 选填,
                            示例值: def2-tzvpp
                        `xc`(str): 选填,
                            示例值: [b3lyp, pbe, tpss, hf, b3lyp-d3bj]
                        ...

        Returns:
            Dict:
                `Ids (List[str])`: 量化计算任务 ID
                    示例值: ["qctask-xxxxx", "qctask-xxxxx", "qctask-xxxxx"]
        """
        return self.__request('SubmitQcTasks', params)

    def list_qc_tasks(self, params):
        """ 列举量化计算任务
        Args:
            params (Dict):
                `QcServiceId (str)`: 必选, 量化计算服务 ID
                    示例值: qcsvc-xxxxxx

                `Ids (List[str])`: 选填, 任务 ID 列表。若配置则 `Status` 和 `Label` 不再生效。

                `Status (str)`: 选填, 任务状态。 取值有: Pending Running Succeeded Failed Stopped
                    示例值: Pending

                `Label (str)`: 选填, 任务标签
                    示例值: xxxxxx

                `SortBy (str)`: 选填, 按字段排序 取值有Name CreateTime UpdateTime
                    示例值: CreateTime

                `SortOrder (str)`: 选填, 指定排序顺序 取值有Asc Desc
                    示例值: Desc

                `PageNumber (int)`: 选填, 页码, 从 1 开始
                    示例值: 1

                `PageSize (int)`: 选填, 每页的数量
                    示例值: 10

        Returns:
            Dict:

                `Items (List[Dict])`: 量化计算服务列表

                    `Id (str)`: 量化计算任务Id
                        示例值: qctask-xxxxx

                    `QcServiceId (str)`: 量化计算服务Id
                        示例值: qcsvc-xxxxxx

                    `TaskType (str)`: 任务类型
                        示例值: opt

                    `TaskConfig` (Dict): 任务配置
                        示例值: {spin: 0, charge: 1}

                    `Status` (str): 任务状态
                        示例值: Pending

                    `Label` (str): 任务标签
                        示例值: xxxxx

                    `MoleculeName` (str): 分子名称

                    `MoleculeUrl` (str): xyz分子文件的下载地址。有效期 10 min。

                    `OutputUrl` (str): 任务输出文件的下载地址。默认有效期 10 min。

                    `LogUrl` (str): 任务 stdout 输出内容的下载地址。有效期 10 min。

                    `CreateTime (str)`: 量化计算服务创建时间
                        示例值: 2024-07-01T00:00:00Z

                    `UpdateTime (str)`: 量化计算服务更新时间
                        示例值: 2024-07-01T00:00:00Z

                `PageNumber (int)`: 页码
                    示例值: 1

                `PageSize (int)`: 页长
                    示例值: 10

                `TotalCount (int)`: 总数量
                    示例值: 10
        """
        return self.__request('ListQcTasks', params)

    # todo.
    def get_qc_tasks_summary(self, params):
        """ 获取量化计算任务汇总信息
        Args:
            params (Dict):
                `QcServiceId (str)`: 必选, 量化计算服务 Id
                    示例值: qcsvc-xxxx

                `Label (str)`: 选填, 任务标签
                    示例值: xxxxx

        Returns:
            Dict[str, int]:
                str: 任务状态
                    示例值: [Pending, Running, Succeeded, Failed, Stopped, Killed]
                int: 任务数量
                    示例值: 100
        """
        return self.__request('GetQcTasksSummary', params)

    def stop_qc_tasks(self, params):
        """ 停止量化计算任务
        Args:
            params (Dict):
                `QcServiceId (str)`: 必选, 量化计算服务 ID
                    示例值: qcsvc-xxxx

                `Label (str)`: 选填, 任务标签
                    示例值: xxxxx

                `Ids (List[str])`: 选填, 任务 ID 列表
                    示例值: ["qctask-xxxx", "qctask-xxxxxx"]

        Returns:
            Dict:
                `ID (str)`: 量化计算服务 ID
                    示例值: qcsvc-xxxxx
        """
        return self.__request('StopQcTasks', params)

    def retry_qc_tasks(self, params):
        """ 重试量化计算任务
        Args:
            params (Dict):
                `QcServiceId (str)`: 必选, 量化计算服务 ID
                    示例值: qcsvc-xxxx

                `Label (str)`: 选填, 任务标签
                    示例值: xxxxx

                `Ids (List[str])`: 选填, 任务 ID 列表
                    示例值: ["qctask-xxxx", "qctask-xxxxxx"]

        Returns:
            Dict:
                `ID (str)`: 量化计算服务 ID
                    示例值: qcsvc-xxxx
        """
        return self.__request('RetryQcTasks', params)

    def list_qc_batch_jobs(self, params):
        """ 列举量化计算批量任务
        Args:
            params (Dict):
                `QcServiceId (str)`: 必选, 量化计算服务 ID
                    示例值: qcsvc-xxxxxx
                `NameContains (str)`: 可选, 按批量任务名称模糊匹配
                    示例值: qcbatchjob-xxxxxx
                `SortBy (str)`: 选填, 按字段排序 取值有 Name, CreateTime
                    示例值: CreateTime
                `SortOrder (str)`: 选填, 指定排序顺序 取值有Asc Desc
                    示例值: Desc
                `PageNumber (int)`: 选填, 页码, 从 1 开始
                    示例值: 1
                `PageSize (int)`: 选填, 每页的数量
                    示例值: 10
        Returns:
            Dict:
                `Items (List[Dict])`: 量化计算服务批量任务
                    `Name (str)`: 任务标签
                        示例值: qcbatchjob-xxxxx
                    `TaskSummary` (Dict): 任务汇总信息
                        `Status (str)`: 任务状态
                            示例值: [Pending, Running, Succeeded, Failed, Stopped, Killed]
                        `Count (int)`: 任务数
                            示例值: 100
                `PageNumber (int)`: 页码
                    示例值: 1
                `PageSize (int)`: 页长
                    示例值: 10
                `TotalCount (int)`: 总数量
                    示例值: 10
        """
        return self.__request('ListQcBatchJobs', params)

    def __request(self, action, params):
        try:
            res = self.json(action, dict(), json.dumps(params))
        except Exception as e:
            raise ServiceError(*e.args) from e
        if res == '':
            raise Exception('empty response')
        res_json = json.loads(res)
        if 'Result' not in res_json.keys():
            return res_json
        return res_json['Result']

class ServiceError(RuntimeError):
    pass
