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


from django.utils.translation import ugettext as _
from rest_framework.decorators import detail_route, list_route

from core.drf_resource.viewsets import ResourceRoute, ResourceViewSet
from kernel_api.resource.collecting import CollectConfigInfoResource
from monitor_api.views import *  # noqa
from monitor_api.views import Response, viewsets
from monitor_web.uptime_check.views import UptimeCheckNodeViewSet as _UptimeCheckNodeModelViewSet
from monitor_web.uptime_check.views import UptimeCheckTaskViewSet as _UptimeCheckTaskModelViewSet


class ModelMixin(viewsets.ModelViewSet):
    @detail_route(methods=["POST"])
    def delete(self, request, *args, **kwargs):
        obj_id = self.get_object().id
        super(ModelMixin, self).destroy(request, *args, **kwargs)
        return Response({"id": obj_id, "result": _("删除成功")})

    @detail_route(methods=["POST"])
    def edit(self, request, *args, **kwargs):
        kwargs.update({"partial": True})
        return super(ModelMixin, self).update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = super(ModelMixin, self).create(request, *args, **kwargs).data
        # 使状态码返回为200，而不是201
        return Response(data)


class UptimeCheckNodeViewSet(_UptimeCheckNodeModelViewSet):
    @list_route(methods=["POST"])
    def delete(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.data.get("node_id")
        super(UptimeCheckNodeViewSet, self).destroy(request, *args, **kwargs)
        return Response({"id": self.kwargs["pk"], "result": _("删除成功")})

    @list_route(methods=["POST"])
    def edit(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.data.get("node_id")
        self.kwargs.update({"partial": True})
        return super(UptimeCheckNodeViewSet, self).update(request, *args, **kwargs)

    @list_route(methods=["POST"])
    def add(self, request, *args, **kwargs):
        return super(UptimeCheckNodeViewSet, self).create(request, *args, **kwargs)


class UptimeCheckTaskViewSet(_UptimeCheckTaskModelViewSet):
    @list_route(methods=["POST"])
    def delete(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.data.get("task_id")
        super(UptimeCheckTaskViewSet, self).destroy(request, *args, **kwargs)
        return Response({"id": self.kwargs["pk"], "result": _("删除成功")})

    @list_route(methods=["POST"])
    def edit(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.data.get("task_id")
        self.kwargs.update({"partial": True})
        return super(UptimeCheckTaskViewSet, self).update(request, *args, **kwargs)

    @list_route(methods=["POST"])
    def add(self, request, *args, **kwargs):
        return super(UptimeCheckTaskViewSet, self).create(request, *args, **kwargs)

    @list_route(methods=["POST"])
    def deploy(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.data.get("task_id")
        return super(UptimeCheckTaskViewSet, self).deploy(request, *args, **kwargs)

    @list_route(methods=["POST"])
    def change_status(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.data.get("task_id")
        self.kwargs["status"] = request.data.get("status", "")
        return super(UptimeCheckTaskViewSet, self).change_status(request, *args, **kwargs)


class CollectConfigViewSet(ResourceViewSet):
    resource_routes = [ResourceRoute("GET", CollectConfigInfoResource)]
