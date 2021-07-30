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


from ..base import ComponentAPI


class CollectionsITSM(object):
    """Collections of ITSM APIS"""

    def __init__(self, client):
        self.client = client

        self.create_ticket = ComponentAPI(
            client=self.client, method="POST", path="/api/c/compapi{bk_api_ver}/itsm/create_ticket/", description="创建单据"
        )
        self.get_service_catalogs = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/itsm/get_service_catalogs/",
            description="服务目录查询",
        )
        self.get_service_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/itsm/get_service_detail/",
            description="服务详情查询",
        )
        self.get_services = ComponentAPI(
            client=self.client, method="GET", path="/api/c/compapi{bk_api_ver}/itsm/get_services/", description="服务列表查询"
        )
        self.get_ticket_info = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/itsm/get_ticket_info/",
            description="单据详情查询",
        )
        self.get_ticket_logs = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/itsm/get_ticket_logs/",
            description="单据日志查询",
        )
        self.get_ticket_status = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/itsm/get_ticket_status/",
            description="单据状态查询",
        )
        self.get_tickets = ComponentAPI(
            client=self.client, method="POST", path="/api/c/compapi{bk_api_ver}/itsm/get_tickets/", description="获取单据列表"
        )
        self.operate_node = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/itsm/operate_node/",
            description="处理单据节点",
        )
        self.operate_ticket = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/itsm/operate_ticket/",
            description="处理单据",
        )
