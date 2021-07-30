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

from __future__ import absolute_import, unicode_literals

import pytest

from core.drf_resource import resource
from monitor_web.models.uptime_check import UptimeCheckTask


def get_mock_uptime_check_task_params_test():
    return {
        "bk_biz_id": 2,
        "protocol": "HTTP",
        "test": True,
        "node_id_list": [10002],
        "config": {
            "timeout": 3000,
            "period": 1,
            "response": "304",
            "response_format": "nin",
            "method": "GET",
            "urls": "http://www.baidu.com",
            "request": None,
            "headers": [{"name": "Accept-Language", "value": "sdsa"}],
            "response_code": "200",
            "insecure_skip_verify": True,
        },
    }


def get_mock_uptime_check_task_result_test():
    return [
        {
            "available_duration": "3000ms",
            "bk_biz_id": 0,
            "disable_keep_alives": False,
            "insecure_skip_verify": False,
            "period": "1m",
            "proxy": "",
            "steps": [
                {
                    "available_duration": "3000ms",
                    "headers": {"Accept-Language": "sdsa"},
                    "method": "GET",
                    "request": None,
                    "response": '"304"',
                    "response_code": "200",
                    "response_format": "nin",
                    "url": "http://www.baidu.com",
                }
            ],
            "task_id": 0,
            "timeout": "15000ms",
        }
    ]


def get_mock_uptime_check_task_result_deploy():
    return [
        {
            "available_duration": "3000ms",
            "bk_biz_id": 2,
            "disable_keep_alives": False,
            "insecure_skip_verify": False,
            "period": "1m",
            "proxy": "",
            "steps": [
                {
                    "available_duration": "3000ms",
                    "headers": {"Cache-Control": "vvvv", "Cookie": "rere"},
                    "method": "GET",
                    "request": None,
                    "response": '"304"',
                    "response_code": "200",
                    "response_format": "nin",
                    "url": "http://mail.qq.com",
                }
            ],
            "task_id": 10065,
            "timeout": "15000ms",
        }
    ]


def mock_uptime_check_task_model(mocker):
    task = UptimeCheckTask(
        bk_biz_id=2,
        protocol="HTTP",
        config={
            "headers": [{"name": "Cookie", "value": "rere"}, {"name": "Cache-Control", "value": "vvvv"}],
            "insecure_skip_verify": True,
            "method": "GET",
            "period": 1,
            "request": None,
            "response": "304",
            "response_code": "200",
            "response_format": "nin",
            "timeout": 3000,
            "urls": "http://mail.qq.com",
        },
    )
    mocked_func = mocker.patch("monitor_web.models.uptime_check.UptimeCheckTask.objects.get", return_value=task)
    return mocked_func


@pytest.mark.django_db
class TestGenerateSubConfig(object):
    def test_perform_request_test(self, mocker):
        params = get_mock_uptime_check_task_params_test()
        result = resource.uptime_check.generate_sub_config(params)
        result_expect = get_mock_uptime_check_task_result_test()
        assert result == result_expect

    def test_perform_request_deploy(self, mocker):
        mocked_func = mock_uptime_check_task_model(mocker)
        mocked_func.start()
        params = {
            "task_id": 10065,
        }
        result = resource.uptime_check.generate_sub_config(params)
        result_expect = get_mock_uptime_check_task_result_deploy()
        assert result == result_expect
        mocked_func.assert_called_once()
        mocked_func.stop()
