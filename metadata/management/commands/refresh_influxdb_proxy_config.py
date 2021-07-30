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
from __future__ import absolute_import, print_function, unicode_literals

import logging
from django.core.management.base import BaseCommand
from metadata.task.config_refresh import refresh_influxdb_route, clean_influxdb_route

logger = logging.getLogger("metadata")


class Command(BaseCommand):
    """
    根据mysql的配置，刷新influxdb-proxy相关的consul信息
    """

    def handle(self, *args, **options):
        refresh_influxdb_route()
        clean_influxdb_route()
