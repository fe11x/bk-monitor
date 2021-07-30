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
from enum import Enum
from typing import Tuple

from .settings import grafana_settings


class GrafanaPermission(Enum):
    View = 1
    Edit = 2
    Admin = 4


class GrafanaRole(Enum):
    Viewer = 1
    Editor = 2
    Admin = 3

    def __str__(self):
        return self.name

    def __gt__(self, role: "GrafanaRole") -> bool:
        return self.value > role.value

    def __eq__(self, role: "GrafanaRole") -> bool:
        if not isinstance(role, self.__class__):
            return False
        return self.value == role.value


class BasePermission:
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        raise NotImplementedError(".has_permission() must be overridden.")


class AllowAny(BasePermission):
    """ """

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        return True, GrafanaRole[grafana_settings.DEFAULT_ROLE]


class IsAuthenticated(BasePermission):
    """ """

    def has_permission(self, request, view, org_name: str) -> Tuple[bool, GrafanaRole]:
        return bool(request.user and request.user.is_authenticated), GrafanaRole[grafana_settings.DEFAULT_ROLE]
