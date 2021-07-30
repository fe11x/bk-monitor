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

import fakeredis
import mock
import pytest

from alarm_backends.core.cache import key
from alarm_backends.service.access.data import AccessDataProcess

from .config import RAW_DATA, RAW_DATA_NONE, RAW_DATA_ZERO, STANDARD_DATA, STRATEGY_CONFIG

query_record = [RAW_DATA, RAW_DATA_ZERO, RAW_DATA_NONE]


pytestmark = pytest.mark.django_db


class MockRecord(object):
    def __init__(self, attrs):
        self.data = attrs
        self.__dict__.update(attrs)


class TestAccessDataProcess(object):
    def setup_method(self):
        redis = fakeredis.FakeRedis(decode_responses=True)
        redis.flushall()

    def teardown_method(self):
        pass

    @mock.patch(
        "alarm_backends.core.cache.strategy.StrategyCacheManager.get_strategy_by_id", return_value=STRATEGY_CONFIG
    )
    @mock.patch(
        "alarm_backends.core.cache.strategy.StrategyCacheManager.get_strategy_group_detail", return_value={"1": [1]}
    )
    @mock.patch("alarm_backends.core.control.item.Item.query_record", return_value=query_record)
    def test_pull(self, mock_strategy, mock_strategy_group, mock_records):
        strategy_group_key = "123456789"
        acc_data = AccessDataProcess(strategy_group_key)
        acc_data.pull()
        assert len(acc_data.record_list) == 2
        assert acc_data.record_list
        assert acc_data.record_list[0].raw_data == {
            "bk_target_ip": "127.0.0.2",
            "load5": 0,
            "bk_target_cloud_id": "0",
            "_time_": 1569246480000,
        }
        assert acc_data.record_list[1].raw_data == {
            "bk_target_ip": "127.0.0.1",
            "load5": 1.381234,
            "bk_target_cloud_id": "0",
            "_time_": 1569246480000,
        }
        assert mock_strategy.call_count == 1
        assert mock_records.call_count == 1
        assert mock_strategy_group.call_count == 1

    @mock.patch(
        "alarm_backends.core.cache.strategy.StrategyCacheManager.get_strategy_by_id", return_value=STRATEGY_CONFIG
    )
    @mock.patch(
        "alarm_backends.core.cache.strategy.StrategyCacheManager.get_strategy_group_detail", return_value={"1": [1]}
    )
    def test_push(self, mock_strategy, mock_strategy_group):
        strategy_id = 1
        item_id = 1
        strategy_group_key = "123456789"
        acc_data = AccessDataProcess(strategy_group_key)
        record = MockRecord(STANDARD_DATA)
        record.items = [acc_data.items[0]]
        record.is_retains = {item_id: True}
        acc_data.record_list = [
            record,
        ]
        acc_data.push()
        assert mock_strategy.call_count == 1

        client = key.DATA_SIGNAL_KEY.client
        assert str(strategy_id) == client.rpop(key.DATA_SIGNAL_KEY.get_key())

        client = key.DATA_LIST_KEY.client
        output_key = key.DATA_LIST_KEY.get_key(strategy_id=strategy_id, item_id=item_id)
        assert client.rpop(output_key) == json.dumps(STANDARD_DATA)
