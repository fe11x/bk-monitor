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


import logging

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.compat import set_rollback
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from bkmonitor.utils.common_utils import failed
from core.errors import Error
from core.errors.common import CustomError, DrfApiError, HTTP404Error

logger = logging.getLogger(__name__)


class CustomException(APIException):
    # todo  和core.errors 结合
    status_code = 500
    default_detail = "A custom exception occurred."
    default_code = "custom_exception"

    def __init__(self, message=None, data=None, code=None):
        """
        :param message: 错误信息
        :param data: 错误数据
        :param code: 错误码
        """
        if message is None:
            message = self.default_detail

        self.detail = message
        self.message = message
        self.data = data
        self.code = code


def custom_exception_handler(exc, context):
    """
    针对CustomException返回的错误进行特殊处理，增加了传递数据的特性
    """
    response = None
    if isinstance(exc, CustomException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        result = failed(exc.message)
        result["code"] = CustomError.code
        result["name"] = CustomError.name
        logger.exception(exc)
        response = Response(result, status=exc.status_code, headers=headers)
    elif isinstance(exc, Error):
        result = {"result": False, "code": exc.code, "name": exc.name, "message": exc.message, "data": exc.data}
        result.update(getattr(exc, "extra", {}))
        response = Response(result, status=exc.status_code)
    elif isinstance(exc, APIException):
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        result = {
            "result": False,
            "code": DrfApiError.code,
            "name": DrfApiError.name,
            "message": DrfApiError.drf_error_processor(exc.detail),
            "data": exc.detail,
        }

        set_rollback()
        response = Response(result, status=exc.status_code, headers=headers)
    elif isinstance(exc, Http404):
        msg = _("Not found.")
        result = {
            "result": False,
            "code": HTTP404Error.code,
            "name": HTTP404Error.name,
            "message": msg,
            "data": HTTP404Error,
        }

        set_rollback()
        response = Response(result, status=status.HTTP_404_NOT_FOUND)

    if response is not None:
        setattr(response, "exception_instance", exc)

    return response
