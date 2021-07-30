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


from django.db import connections, migrations


class RemoveFieldEX(migrations.RemoveField):
    def allow_migrate_model(self, db, model):
        if not super(RemoveFieldEX, self).allow_migrate_model(db, model):
            return False
        connection = connections[db]
        with connection.cursor() as cursor:
            cursor.execute(
                """
            SELECT *
            FROM information_schema.COLUMNS
            WHERE
                TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}'
            AND COLUMN_NAME = '{column_name}'
            LIMIT 1
            """.format(
                    table_name=model._meta.db_table, column_name=self.name
                )
            )
            return bool(cursor.fetchall())
