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

from django.db.models.sql import AND, OR


class Lookup(object):
    lookup_name = None

    def __init__(self, lhs, rhs):
        self.lhs, self.rhs = lhs, rhs

    def process_lhs(self, compiler, connection, lhs=None):
        return lhs or self.lhs, []

    def process_rhs(self, compiler, connection):
        return "%s", [self.rhs]

    def get_rhs_op(self, connection, rhs):
        return connection.operators[self.lookup_name] % rhs

    def as_sql(self, compiler, connection):
        lhs_sql, params = self.process_lhs(compiler, connection, self.lhs)
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        params.extend(rhs_params)
        rhs_sql = self.get_rhs_op(connection, rhs_sql)
        return "{} {}".format(lhs_sql, rhs_sql), params


def is_list_type(value):
    return isinstance(value, (list, tuple))


class Exact(Lookup):
    lookup_name = "exact"


class Equal(Lookup):
    lookup_name = "eq"
    list_connector = " {} ".format(OR)

    def as_sql(self, compiler, connection):
        lhs_sql, params = self.process_lhs(compiler, connection, self.lhs)
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        rhs_sql = self.get_rhs_op(connection, rhs_sql)
        if rhs_params and is_list_type(rhs_params[0]):
            params.extend(rhs_params[0])
            result = [
                "{} {}".format(lhs_sql, rhs_sql),
            ] * len(rhs_params[0])
            sql_string = self.list_connector.join(result)
            if len(result) > 1:
                sql_string = "(%s)" % sql_string
        else:
            params.extend(rhs_params)
            sql_string = "{} {}".format(lhs_sql, rhs_sql)
        return sql_string, params


class NotEqual(Equal):
    lookup_name = "neq"
    list_connector = " {} ".format(AND)


class GreaterThan(Lookup):
    lookup_name = "gt"

    def process_rhs(self, compiler, connection):
        rhs, params = super(GreaterThan, self).process_rhs(compiler, connection)
        if params and is_list_type(params[0]):
            params[0] = max(params[0])
        return rhs, params


class GreaterThanOrEqual(GreaterThan):
    lookup_name = "gte"


class LessThan(Lookup):
    lookup_name = "lt"

    def process_rhs(self, compiler, connection):
        rhs, params = super(LessThan, self).process_rhs(compiler, connection)
        if params and is_list_type(params[0]):
            params[0] = min(params[0])
        return rhs, params


class LessThanOrEqual(LessThan):
    lookup_name = "lte"


class Contains(Lookup):
    lookup_name = "contains"

    def process_rhs(self, qn, connection):
        rhs, params = super(Contains, self).process_rhs(qn, connection)
        if params:
            params[0] = "%%%s%%" % connection.ops.prep_for_like_query(params[0])
        return rhs, params


default_lookups = {}
default_lookups["exact"] = Exact
default_lookups["eq"] = Equal
default_lookups["neq"] = NotEqual
default_lookups["!="] = NotEqual
default_lookups["gt"] = GreaterThan
default_lookups["gte"] = GreaterThanOrEqual
default_lookups["lt"] = LessThan
default_lookups["lte"] = LessThanOrEqual
default_lookups["contains"] = Contains


def get_lookup_class(lookup_name):
    lookup_class = default_lookups.get(lookup_name)
    if lookup_class is None:
        raise Exception("Unsupported lookup '%s'" % lookup_name)
    return lookup_class
