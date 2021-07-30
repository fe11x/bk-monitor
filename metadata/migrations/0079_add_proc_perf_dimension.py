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
# Generated by Django 1.11.23 on 2020-12-28 12:40
from __future__ import unicode_literals

from django.db import migrations


def add_port_dimension_into_proc(apps, schema_editor):
    ResultTableField = apps.get_model("metadata", "ResultTableField")
    ResultTableField.objects.create(
        table_id="system.proc",
        field_name="port",
        field_type="string",
        description="进程监听端口",
        tag="dimension",
        is_config_by_user=True,
        creator="system",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("metadata", "0078_auto_20201214_1753"),
    ]

    operations = [migrations.RunPython(add_port_dimension_into_proc)]
