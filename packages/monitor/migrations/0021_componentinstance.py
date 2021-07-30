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


class Migration(migrations.Migration):

    dependencies = [
        ("monitor", "0020_rolepermission"),
    ]

    operations = [
        migrations.CreateModel(
            name="ComponentInstance",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("create_time", models.DateTimeField(auto_now_add=True, verbose_name="\u521b\u5efa\u65f6\u95f4")),
                ("create_user", models.CharField(max_length=32, verbose_name="\u521b\u5efa\u4eba")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="\u4fee\u6539\u65f6\u95f4")),
                ("update_user", models.CharField(max_length=32, verbose_name="\u4fee\u6539\u4eba")),
                ("is_deleted", models.BooleanField(default=False, verbose_name="\u662f\u5426\u5220\u9664")),
                ("biz_id", models.IntegerField(verbose_name="\u4e1a\u52a1ID")),
                ("ip", models.GenericIPAddressField(verbose_name="\u5b9e\u4f8bIP")),
                ("component", models.CharField(max_length=128, verbose_name="\u7ec4\u4ef6\u540d\u79f0")),
                ("config", models.TextField(verbose_name="\u7ec4\u4ef6\u914d\u7f6e")),
            ],
            options={
                "verbose_name": "\u7ec4\u4ef6\u5b9e\u4f8b\u5173\u7cfb",
                "verbose_name_plural": "\u7ec4\u4ef6\u5b9e\u4f8b\u5173\u7cfb",
            },
        ),
    ]
