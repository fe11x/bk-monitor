# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
import os
import posixpath
import requests

from django.conf import settings

from bkmonitor.utils.thread_backend import ThreadPool


class custom_report_tool:
    """
    此类用于监控后台自身的自定义上报
    """

    def __init__(self, dataid):
        self.dataid = dataid

    def batch_cmd(self, cmds):
        """
        批量请求命令
        :param cmds: 命令集合
        :return: 命令执行结果
        """
        pool = ThreadPool()
        futures = []
        for cmd in cmds:
            futures.append(pool.apply_async(os.popen, args=(cmd,)))
        pool.close()
        pool.join()
        data = []
        for future in futures:
            data.extend(future.get())
        return data

    def send_data(self, all_data):
        """
        上报数据
        :param all_data: list, 待发送数据
        如：
        [{
            # 指标，必需项
            "metrics": {
                f"{stat['namespace']}_{metric.metric_name}": metric.metric_value
            },
            # 来源标识
            "target": settings.BK_PAAS_INNER_HOST,
            # 数据时间，精确到毫秒，非必需项
            "timestamp": arrow.now().timestamp * 1000
        }]
        """

        send_list = [[]]
        chunk_index = 0
        cmds = []
        # 避免每次发送的数据太长，分批进行上报
        for data in all_data:
            send_list[chunk_index].append(data)
            if len(send_list[chunk_index]) > 20:
                chunk_index += 1
                send_list.append([])
        send_data = {"data_id": self.dataid, "data": []}
        for data in send_list:
            send_data["data"] = data
            cmds.append(
                f"{posixpath.join(settings.LINUX_GSE_AGENT_PATH, 'plugins', 'bin', 'gsecmdline')} -d {self.dataid} -J "
                f"'{json.dumps(send_data)}' -S {settings.LINUX_GSE_AGENT_IPC_PATH}"
            )

        self.batch_cmd(cmds)

    def send_data_by_http(self, all_data, access_token):
        """
        上报数据
        :param all_data: list, 待发送数据
        如：
        [{
            # 指标，必需项
            "metrics": {
                f"{stat['namespace']}_{metric.metric_name}": metric.metric_value
            },
            # 来源标识
            "target": settings.BK_PAAS_INNER_HOST,
            # 数据时间，精确到毫秒，非必需项
            "timestamp": arrow.now().timestamp * 1000
        }]
        """

        send_list = [[]]
        chunk_index = 0
        # 避免每次发送的数据太长，分批进行上报
        for data in all_data:
            send_list[chunk_index].append(data)
            if len(send_list[chunk_index]) > 20:
                chunk_index += 1
                send_list.append([])
        send_data = {"data_id": self.dataid, "access_token": access_token, "data": []}
        for data in send_list:
            send_data["data"] = data
            requests.post(
                f"http://{settings.CUSTOM_REPORT_DEFAULT_PROXY_IP[0]}:10205/v2/push/", data=json.dumps(send_data)
            )
