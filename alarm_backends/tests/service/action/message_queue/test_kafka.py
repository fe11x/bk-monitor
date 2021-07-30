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


import json

import arrow
import pytest
from django.conf import settings

from alarm_backends.service.action.message_queue.processor import MessageQueueProcessor
from bkmonitor.models import AnomalyRecord, Event, EventAction

pytestmark = pytest.mark.django_db

strategy = {
    "bk_biz_id": 2,
    "is_enabled": True,
    "update_time": 1570072047,
    "update_user": "admin",
    "name": "CPU\u603b\u4f7f\u7528\u7387",
    "scenario": "os",
    "item_list": [
        {
            "rt_query_config": {
                "agg_method": "AVG",
                "agg_dimension": ["ip", "bk_cloud_id", "device_name"],
                "unit_conversion": 1.0,
                "agg_condition": [],
                "agg_interval": 60,
                "unit": "%",
                "metric_field": "usage",
                "extend_fields": "",
                "result_table_id": "system.cpu_summary",
            },
            "metric_id": "system.cpu_summary.usage",
            "name": "usage",
            "algorithm_list": [
                {
                    "algorithm_config": [{"threshold": 90, "method": "gte"}],
                    "level": 1,
                    "trigger_config": {"count": 3, "check_window": 5},
                    "algorithm_type": "Threshold",
                    "recovery_config": {"check_window": 5},
                    "algorithm_id": 6,
                    "id": 6,
                }
            ],
            "item_id": 6,
            "data_source_label": "bk_monitor",
            "id": 6,
            "no_data_config": {"is_enabled": False, "continuous": 5},
            "item_name": "usage",
            "data_type_label": "time_series",
        }
    ],
    "strategy_id": 6,
    "strategy_name": "CPU\u603b\u4f7f\u7528\u7387",
    "action_list": [
        {
            "notice_template": {"anomaly_template": "", "recovery_template": ""},
            "notice_group_list": [
                {
                    "notice_way": {"1": ["sms"], "3": ["weixin"], "2": ["mail"]},
                    "notice_receiver": ["group#bk_biz_maintainer", "user#layman"],
                    "id": 3,
                    "name": "\u84dd\u9cb8\u8fd0\u7ef4\u7ec4",
                }
            ],
            "action_type": "notice",
            "config": {
                "alarm_end_time": "23:59:59",
                "send_recovery_alarm": False,
                "alarm_start_time": "00:00:00",
                "alarm_interval": 120,
            },
            "id": 6,
            "action_id": 6,
        }
    ],
    "create_user": "admin",
    "source_type": "BKMONITOR",
    "create_time": 1570072047,
    "id": 6,
    "target": [
        {"ip": "10.0.1.10", "bk_supplier_id": 0, "bk_cloud_id": 0},
        {"ip": "10.0.1.11", "bk_supplier_id": 0, "bk_cloud_id": 0},
    ],
}

origin_alarm = {
    "anomaly": {
        "1": {
            "anomaly_message": "\u5f53\u524d\u6307\u6807\u503c(77.88%) >=(1.0%)",
            "anomaly_time": "2019-10-05 14:11:05",
            "anomaly_id": "11dd36c4e45b40da6a8f436a01c781cc.1570284540.6.6.1",
        }
    },
    "trigger": {
        "anomaly_ids": [
            "11dd36c4e45b40da6a8f436a01c781cc.1570284300.6.6.1",
            "11dd36c4e45b40da6a8f436a01c781cc.1570284360.6.6.1",
            "11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
        ],
        "level": "1",
    },
    "data": {
        "record_id": "11dd36c4e45b40da6a8f436a01c781cc.1570284540",
        "values": {"usage": 77.88, "time": 1570284540},
        "dimensions": {
            "ip": "10.0.1.11",
            "bk_cloud_id": "0",
            "bk_topo_node": [
                "set|3",
                "module|21",
                "set|5",
                "module|19",
                "module|16",
                "module|17",
                "module|28",
                "test|2",
                "module|13",
                "module|10",
                "module|5",
                "module|12",
                "biz|2",
                "module|9",
                "set|6",
            ],
            "device_name": "C",
        },
        "value": 77.88,
        "time": 1570284540,
    },
    "dimension_translation": {
        "ip": {"display_value": "10.0.1.11", "display_name": "内网IP地址"},
        "bk_topo_node": {
            "display_name": "bk_topo_node",
            "display_value": [
                {"bk_obj_name": "模块", "bk_inst_name": "gameserver"},
                {"bk_obj_name": "集群", "bk_inst_name": "paas"},
            ],
        },
        "device_name": {"display_name": "磁盘名称", "display_value": "C盘"},
    },
    "strategy_snapshot_key": "bk_monitor.ee[development].cache.strategy.snapshot.6.1570072047",
}


@pytest.fixture()
def kafka_mocked(mock):
    kafka = mock.patch("alarm_backends.service.action.message_queue.client.KafkaProducer")
    kafka_mocker = mock.MagicMock()
    kafka.return_value = kafka_mocker
    return kafka_mocker


@pytest.fixture()
def setup(mock):
    EventAction.objects.all().delete()
    Event.objects.all().delete()
    AnomalyRecord.objects.all().delete()

    Event.objects.create(
        event_id="11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
        begin_time=arrow.now().datetime,
        bk_biz_id=2,
        strategy_id=6,
        origin_alarm=origin_alarm,
        origin_config=strategy,
        level=1,
        status=Event.EventStatus.ABNORMAL,
    )

    AnomalyRecord.objects.create(
        anomaly_id="11dd36c4e45b40da6a8f436a01c781cc.1570284300.6.6.1",
        event_id="11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
        origin_alarm=origin_alarm,
        source_time=arrow.now().datetime,
        strategy_id=6,
    )
    AnomalyRecord.objects.create(
        anomaly_id="11dd36c4e45b40da6a8f436a01c781cc.1570284360.6.6.1",
        event_id="11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
        origin_alarm=origin_alarm,
        source_time=arrow.now().datetime,
        strategy_id=6,
    )
    AnomalyRecord.objects.create(
        anomaly_id="11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
        event_id="11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
        origin_alarm=origin_alarm,
        source_time=arrow.now().datetime,
        strategy_id=6,
    )

    yield EventAction.objects.create(
        create_time=arrow.now().datetime,
        operate=EventAction.Operate.ANOMALY_NOTICE,
        extend_info={
            "action": {
                "notice_template": {
                    "anomaly_template": "",
                    "recovery_template": "",
                }
            }
        },
        status=EventAction.Status.RUNNING,
        event_id="11dd36c4e45b40da6a8f436a01c781cc.1570284420.6.6.1",
    )

    EventAction.objects.all().delete()
    Event.objects.all().delete()
    AnomalyRecord.objects.all().delete()


class TestKafKaClient(object):
    """
    测试KafKaClient
    """

    def test_send(self, setup, kafka_mocked):
        settings.ENABLE_MESSAGE_QUEUE = True
        settings.MESSAGE_QUEUE_DSN = "kafka://root:123456@locahost:3307/actions"
        processor = MessageQueueProcessor(setup.id)
        processor.execute()

        event = Event.objects.get(event_id=setup.event_id)
        assert kafka_mocked.send.call_count == 1
        assert kafka_mocked.send.call_args[0][0] == "actions"
        result = json.loads(kafka_mocked.send.call_args[0][1])
        assert result["event"]["id"] == event.id

        AnomalyRecord.objects.all().delete()
        processor = MessageQueueProcessor(setup.id)
        processor.execute()
        assert kafka_mocked.send.call_count == 2

    def test_no_password(self, setup, kafka_mocked):
        settings.ENABLE_MESSAGE_QUEUE = True
        settings.MESSAGE_QUEUE_DSN = "kafka://localhost:3307/actions"
        processor = MessageQueueProcessor(setup.id)
        processor.execute()

    def test_error(self):
        settings.ENABLE_MESSAGE_QUEUE = True
        settings.MESSAGE_QUEUE_DSN = "kafka://root:123456@localhost:3307/"
        try:
            MessageQueueProcessor(123)
        except Exception as e:
            print(e)
        else:
            assert False

    def test_disable(self):
        settings.ENABLE_MESSAGE_QUEUE = False
        settings.MESSAGE_QUEUE_DSN = "kafka://root:123456@locahost:3307/"

        p = MessageQueueProcessor(123)
        p.execute()
        assert not getattr(p, "event", None)
        assert not getattr(p, "event_action", None)
