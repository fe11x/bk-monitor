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

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from bkmonitor.iam import Permission
from bkmonitor.iam.action import get_action_by_id
from bkmonitor.utils.request import get_request
from core.drf_resource import Resource
from bkmonitor.views import serializers


logger = logging.getLogger(__name__)


class BusinessListByActions(Resource):
    class RequestSerializer(serializers.Serializer):
        """
        actions_id 参考
        >>>from bkmonitor.iam.action import ActionEnum
        """

        action_ids = serializers.ListField(required=False, label=_("权限id列表"), default=["view_business"])
        username = serializers.CharField(required=False, label=_("用户名"), allow_null=True, default="")

    def validate_username(self, username):
        if not username:
            try:
                request = get_request()
                return request.user
            except Exception:
                raise ValidationError("can't get username in request")

    def perform_request(self, validated_request_data):
        biz_dict = {}
        perm_client = Permission(validated_request_data["username"])
        perm_client.skip_check = False
        for action_id in validated_request_data["action_ids"]:
            action = get_action_by_id(action_id)
            # 根据权限中心的【业务访问】权限，对业务列表进行过滤
            business_list = perm_client.filter_business_list_by_action(action)
            for business in business_list:
                biz_dict.setdefault(business.bk_biz_id, {"id": business.id, "text": business.display_name})
        return list(biz_dict.values())
