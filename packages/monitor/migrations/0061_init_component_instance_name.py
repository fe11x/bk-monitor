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


from django.db import migrations, models


def init_instance_name(apps, schema_editor):
    ComponentInstance = apps.get_model("monitor", "ComponentInstance")
    for instance in ComponentInstance.objects.filter(instance_name__exact=""):
        instance.instance_name = instance.ip
        instance.save()


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0060_auto_20190105_1524"),
    ]

    operations = [migrations.RunPython(init_instance_name)]
