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

from alarm_backends.core.cache.cmdb import TopoManager
from alarm_backends.service.event.generator.translator.base import BaseTranslator
from constants.data_source import DataSourceLabel


class TopoNodeTranslator(BaseTranslator):
    """
    拓扑层级翻译
    """

    def is_enabled(self):
        return self.data_source_label == DataSourceLabel.BK_MONITOR_COLLECTOR

    def translate(self, data):
        data = self.translate_inst_id(data)
        data = self.translate_topo_node(data)
        data = self.translate_host_fields(data)
        return data

    def translate_host_fields(self, data):
        if "bk_target_ip" in data:
            field = data["bk_target_ip"]
            if field.display_name == field.name:
                field.display_name = _("目标IP")

        if "bk_target_cloud_id" in data:
            field = data["bk_target_cloud_id"]
            if field.display_name == field.name:
                field.display_name = _("云区域ID")

        if "bk_cloud_id" in data:
            field = data["bk_cloud_id"]
            if field.display_name == field.name:
                field.display_name = _("云区域ID")

        return data

    def translate_topo_node(self, data):
        try:
            field = data["bk_topo_node"]
        except KeyError:
            return data

        nodes = field.value

        translated_nodes = []

        # 拼接 key，然后进行批量查询
        keys = []
        for node in nodes:
            bk_obj_id, bk_inst_id = node.split("|")
            keys.append(TopoManager.key_to_internal_value(bk_obj_id, bk_inst_id))

        if not keys:
            field.display_value = []
            return data

        node_infos = TopoManager.multi_get(keys)

        for index, node in enumerate(nodes):
            node_info = node_infos[index]
            bk_obj_id, bk_inst_id = node.split("|")
            # 如果在缓存中获取不到节点信息，则直接使用ID
            if not node_info:
                bk_obj_name = bk_obj_id
                bk_inst_name = bk_inst_id
            else:
                bk_obj_name = node_info.bk_obj_name
                bk_inst_name = node_info.bk_inst_name
            translated_nodes.append(
                {
                    "bk_obj_name": bk_obj_name,
                    "bk_inst_name": bk_inst_name,
                }
            )
        field.display_value = translated_nodes
        return data

    def translate_inst_id(self, data):
        if "bk_obj_id" not in data or "bk_inst_id" not in data:
            return data

        bk_obj_id = data["bk_obj_id"]
        bk_inst_id = data["bk_inst_id"]

        node = TopoManager.get(bk_obj_id.value, bk_inst_id.value)

        bk_obj_id.display_name = _("模型名称")
        bk_inst_id.display_name = _("模型实例名称")

        if node:
            bk_obj_id.display_value = node.bk_obj_name
            bk_inst_id.display_value = node.bk_inst_name

        return data
