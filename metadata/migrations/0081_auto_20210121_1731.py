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
# Generated by Django 1.11.23 on 2021-01-21 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("metadata", "0080_merge_20210120_2133"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventgroup",
            name="max_rate",
            field=models.IntegerField(default=-1, verbose_name="上报速率限制"),
        ),
        migrations.AddField(
            model_name="timeseriesgroup",
            name="max_rate",
            field=models.IntegerField(default=-1, verbose_name="上报速率限制"),
        ),
    ]
