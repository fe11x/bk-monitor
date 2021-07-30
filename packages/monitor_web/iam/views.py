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

from core.drf_resource.viewsets import ResourceRoute, ResourceViewSet
from core.drf_resource import resource


class IAMViewSet(ResourceViewSet):

    permission_classes = []

    resource_routes = [
        ResourceRoute("GET", resource.iam.get_authority_meta, endpoint="get_authority_meta"),
        ResourceRoute("POST", resource.iam.check_allowed_by_action_ids, endpoint="check_allowed_by_action_ids"),
        ResourceRoute("POST", resource.iam.get_authority_detail, endpoint="get_authority_detail"),
        ResourceRoute("GET", resource.iam.test, endpoint="test"),
    ]
