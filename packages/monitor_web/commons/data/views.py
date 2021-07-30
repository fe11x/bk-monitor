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


from core.drf_resource.viewsets import ResourceViewSet
from core.drf_resource.viewsets import ResourceRoute
from core.drf_resource import resource


class ListResultTableAccessInfoViewSet(ResourceViewSet):
    """
    获取结果表列表，包括是否需要接入的信息
    """

    resource_routes = [
        ResourceRoute("GET", resource.commons.list_result_table_access_info),
    ]


class GetResultTableViewSet(ResourceViewSet):
    """
    获取结果表列表，包括是否需要接入的信息
    """

    resource_routes = [
        ResourceRoute("GET", resource.commons.get_result_table_access_info),
    ]


class GetLabelViewSet(ResourceViewSet):
    """
    获取结果表标签
    """

    resource_routes = [
        ResourceRoute("GET", resource.commons.get_label),
    ]
