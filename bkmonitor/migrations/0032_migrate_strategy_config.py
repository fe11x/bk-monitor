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
# Generated by Django 1.11.23 on 2021-03-31 09:49
from __future__ import unicode_literals

import json
import logging
from collections import defaultdict

from django.db import migrations
from rest_framework.exceptions import ValidationError

from bkmonitor.strategy.serializers import (
    BkMonitorTimeSeriesSerializer,
    BkMonitorLogSerializer,
    BkMonitorEventSerializer,
    BkLogSearchTimeSeriesSerializer,
    BkLogSearchLogSerializer,
    CustomTimeSeriesSerializer,
    CustomEventSerializer,
    BkDataTimeSeriesSerializer,
)
from constants.data_source import DataTypeLabel, DataSourceLabel
from constants.strategy import SYSTEM_EVENT_RT_TABLE_ID

logger = logging.getLogger(__name__)


def strategy_migrate(apps, *args, **kwargs):
    """
    策略数据模型迁移
    """
    Strategy = apps.get_model("bkmonitor", "Strategy")
    Item = apps.get_model("bkmonitor", "Item")
    DetectAlgorithm = apps.get_model("bkmonitor", "DetectAlgorithm")
    ResultTableDSLConfig = apps.get_model("bkmonitor", "ResultTableDSLConfig")
    CustomEventQueryConfig = apps.get_model("bkmonitor", "CustomEventQueryConfig")
    ResultTableSQLConfig = apps.get_model("bkmonitor", "ResultTableSQLConfig")
    BaseAlarmQueryConfig = apps.get_model("bkmonitor", "BaseAlarmQueryConfig")

    StrategyModel = apps.get_model("bkmonitor", "StrategyModel")
    ItemModel = apps.get_model("bkmonitor", "ItemModel")
    DetectModel = apps.get_model("bkmonitor", "DetectModel")
    AlgorithmModel = apps.get_model("bkmonitor", "AlgorithmModel")
    QueryConfigModel = apps.get_model("bkmonitor", "QueryConfigModel")

    def get_query_config_model(data_source_label, data_type_label):
        if data_type_label == DataTypeLabel.TIME_SERIES:
            return ResultTableSQLConfig
        elif data_type_label == DataTypeLabel.LOG:
            return ResultTableDSLConfig
        elif data_type_label == DataTypeLabel.EVENT and data_source_label == DataSourceLabel.CUSTOM:
            return CustomEventQueryConfig
        elif data_type_label == DataTypeLabel.EVENT and data_source_label == DataSourceLabel.BK_MONITOR_COLLECTOR:
            return BaseAlarmQueryConfig

    old_strategies = Strategy.objects.filter(is_deleted=False)

    strategies = []
    strategy_ids = set()
    for strategy in old_strategies:
        strategy_ids.add(strategy.id)
        strategies.append(
            StrategyModel(
                bk_biz_id=strategy.bk_biz_id,
                id=strategy.id,
                name=strategy.name,
                source=strategy.source,
                scenario=strategy.scenario,
                type="monitor",
                is_enabled=strategy.is_enabled,
                create_user=strategy.create_user,
                create_time=strategy.create_time,
                update_user=strategy.update_user,
                update_time=strategy.update_time,
            )
        )
    StrategyModel.objects.bulk_create(strategies, batch_size=200)

    old_query_configs = defaultdict(dict)
    for query_config in CustomEventQueryConfig.objects.filter(is_deleted=False).values():
        old_query_configs[CustomEventQueryConfig][query_config["id"]] = query_config
    for query_config in BaseAlarmQueryConfig.objects.filter(is_deleted=False).values():
        old_query_configs[BaseAlarmQueryConfig][query_config["id"]] = query_config
    for query_config in ResultTableSQLConfig.objects.filter(is_deleted=False).values():
        old_query_configs[ResultTableSQLConfig][query_config["id"]] = query_config
    for query_config in ResultTableDSLConfig.objects.filter(is_deleted=False).values():
        old_query_configs[ResultTableDSLConfig][query_config["id"]] = query_config

    items = []
    query_configs = []
    old_items = Item.objects.filter(is_deleted=False)
    for item in old_items:
        query_config_model = get_query_config_model(item.data_source_label, item.data_type_label)
        old_query_config = old_query_configs[query_config_model].get(item.rt_query_config_id)

        if not old_query_config:
            if query_config_model != BaseAlarmQueryConfig:
                print(f"item({item.id}) lose query_config({item.rt_query_config_id})")
                continue
            else:
                old_query_config = {
                    "result_table_id": SYSTEM_EVENT_RT_TABLE_ID,
                    "metric_field": item.metric_id.split(".")[1],
                    "agg_condition": [],
                }
        else:
            old_query_config = dict(old_query_config)
            if query_config_model == BaseAlarmQueryConfig:
                old_query_config["result_table_id"] = SYSTEM_EVENT_RT_TABLE_ID
                old_query_config["metric_field"] = item.metric_id.split(".")[1]
        extend_fields = old_query_config.pop("extend_fields", {})
        old_query_config.update(extend_fields)

        serializer_mapping = {
            (DataSourceLabel.BK_MONITOR_COLLECTOR, DataTypeLabel.TIME_SERIES): BkMonitorTimeSeriesSerializer,
            (DataSourceLabel.BK_MONITOR_COLLECTOR, DataTypeLabel.LOG): BkMonitorLogSerializer,
            (DataSourceLabel.BK_MONITOR_COLLECTOR, DataTypeLabel.EVENT): BkMonitorEventSerializer,
            (DataSourceLabel.BK_LOG_SEARCH, DataTypeLabel.TIME_SERIES): BkLogSearchTimeSeriesSerializer,
            (DataSourceLabel.BK_LOG_SEARCH, DataTypeLabel.LOG): BkLogSearchLogSerializer,
            (DataSourceLabel.CUSTOM, DataTypeLabel.TIME_SERIES): CustomTimeSeriesSerializer,
            (DataSourceLabel.CUSTOM, DataTypeLabel.EVENT): CustomEventSerializer,
            (DataSourceLabel.BK_DATA, DataTypeLabel.TIME_SERIES): BkDataTimeSeriesSerializer,
        }
        # 日志查询查询字符串转换
        if "keywords_query_string" in old_query_config:
            old_query_config["query_string"] = old_query_config["keywords_query_string"]

        # 兼容agg_condition为字符串
        if not isinstance(old_query_config.get("agg_condition", []), list):
            old_query_config["agg_condition"] = []

        serializer = serializer_mapping[item.data_source_label, item.data_type_label](data=old_query_config)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(f"convert item({item.id}) config error: {json.dumps(old_query_config, ensure_ascii=False)}")
            raise e
        query_configs.append(
            QueryConfigModel(
                strategy_id=item.strategy_id,
                item_id=item.id,
                alias="a",
                data_source_label=item.data_source_label,
                data_type_label=item.data_type_label,
                metric_id=item.metric_id,
                config=serializer.validated_data,
            )
        )

        items.append(
            ItemModel(
                id=item.id,
                name=item.name,
                strategy_id=item.strategy_id,
                expression="",
                origin_sql="",
                no_data_config=item.no_data_config,
                target=item.target,
                meta={},
            )
        )

    ItemModel.objects.bulk_create(items, batch_size=200)
    QueryConfigModel.objects.bulk_create(query_configs, batch_size=200)

    old_algorithms = DetectAlgorithm.objects.filter(is_deleted=False)
    strategy_levels = defaultdict(set)

    detects = []
    algorithms = []
    for algorithm in old_algorithms:
        algorithms.append(
            AlgorithmModel(
                strategy_id=algorithm.strategy_id,
                item_id=algorithm.item_id,
                level=algorithm.level,
                unit_prefix=algorithm.algorithm_unit,
                type=algorithm.algorithm_type,
                config=algorithm.algorithm_config,
            )
        )

        if algorithm.level in strategy_levels[algorithm.strategy_id]:
            continue

        strategy_levels[algorithm.strategy_id].add(algorithm.strategy_id)
        detects.append(
            DetectModel(
                strategy_id=algorithm.strategy_id,
                level=algorithm.level,
                expression="",
                trigger_config=algorithm.trigger_config,
                recovery_config=algorithm.recovery_config,
            )
        )

    AlgorithmModel.objects.bulk_create(algorithms, batch_size=200)
    DetectModel.objects.bulk_create(detects, batch_size=200)


def reverse_strategy_migrate(apps, *args, **kwargs):
    """
    回滚数据模型
    """
    StrategyModel = apps.get_model("bkmonitor", "StrategyModel")
    ItemModel = apps.get_model("bkmonitor", "ItemModel")
    DetectModel = apps.get_model("bkmonitor", "DetectModel")
    AlgorithmModel = apps.get_model("bkmonitor", "AlgorithmModel")
    QueryConfigModel = apps.get_model("bkmonitor", "QueryConfigModel")

    StrategyModel.objects.all().delete()
    ItemModel.objects.all().delete()
    DetectModel.objects.all().delete()
    AlgorithmModel.objects.all().delete()
    QueryConfigModel.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("bkmonitor", "0031_auto_20210402_1803"),
    ]

    operations = [
        migrations.RunPython(code=strategy_migrate, reverse_code=reverse_strategy_migrate),
    ]
