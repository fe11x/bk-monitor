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


from django.utils.translation import ugettext_lazy as _lazy
from rest_framework import serializers

from core.drf_resource import Resource
from core.drf_resource.tasks import query_task_result


class QueryAsyncTaskResultResource(Resource):
    """
    查询Resource异步任务状态
    """

    class RequestSerializer(serializers.Serializer):
        bk_biz_id = serializers.IntegerField(required=True, label=_lazy("业务ID"))
        task_id = serializers.CharField(required=True, label=_lazy("任务ID"))

    # class ResponseSerializer(serializers.Serializer):
    #     task_id = serializers.CharField(required=True, label=_lazy("任务ID"))
    #     is_completed = serializers.BooleanField(required=True, label=_lazy("任务是否完成"))
    #     state = serializers.CharField(required=True, label=_lazy("任务状态"))
    #     data = serializers.JSONField(required=True, allow_null=True)
    #     message = serializers.CharField(required=True, label=_lazy("任务信息"), allow_null=True, allow_blank=True)

    def perform_request(self, validated_request_data):
        task_id = validated_request_data["task_id"]
        return query_task_result(task_id)
