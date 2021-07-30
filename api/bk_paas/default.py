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


import abc

import six
from django.conf import settings
from django.utils.translation import ugettext_lazy as _lazy
from rest_framework import serializers

from core.drf_resource import APIResource


class BkPaaSAPIGWResource(six.with_metaclass(abc.ABCMeta, APIResource)):
    base_url = "%s/api/c/compapi/v2/bk_paas/" % settings.BK_PAAS_INNER_HOST

    # 模块名
    module_name = "bk_paas"

    @property
    def label(self):
        return self.__doc__


class GetAppInfoResource(BkPaaSAPIGWResource):
    """
    获取用户信息
    """

    action = "/get_app_info/"
    method = "GET"

    class RequestSerializer(serializers.Serializer):
        target_app_code = serializers.CharField(required=False, label=_lazy("目标应用"))
        fields = serializers.CharField(required=False, label=_lazy("目标字段"))
