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
from itertools import chain

import arrow
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from alarm_backends.constants import LATEST_NO_DATA_CHECK_POINT, NO_DATA_LEVEL, NO_DATA_TAG_DIMENSION, NO_DATA_VALUE
from alarm_backends.core.cache import key
from alarm_backends.core.detect_result import ANOMALY_LABEL, CheckResult
from bkmonitor.models import Event, EventAction
from bkmonitor.utils.common_utils import count_md5

logger = logging.getLogger("core.control")


class CheckMixin(object):
    def check(self, data_points, check_timestamp):
        scenario_cls = import_string("alarm_backends.service.nodata.scenarios.base.SCENARIO_CLS")
        scenario_checker = scenario_cls[self.strategy.scenario](self)
        # 1. 获取无数据告警目标维度
        no_data_dimensions = scenario_checker.get_no_data_dimensions()
        # 2. 将 access 获取的上报数据按无数据维度和监控目标降维，并加入无数据维度标记
        result = self._process_dimensions(no_data_dimensions, data_points)
        data_dimensions = result["data_dimensions"]
        dimensions_md5_timestamp = result["dimensions_md5_timestamp"]
        data_dimensions_mds = result["data_dimensions_mds"]
        # 3. 获取历史维度集合
        target_instance_dimensions = scenario_checker.get_target_instances_dimensions()

        # 4.1 如果检测历史维度范围为空，并且当前无上报数据，则以整体维度告警
        total_no_data_dimensions = [{NO_DATA_TAG_DIMENSION: True}]
        total_no_data_md5 = [count_md5(total_no_data_dimensions[0])]
        if not (target_instance_dimensions or data_dimensions):
            logger.warning(
                "[nodata] strategy({strategy_id}) item({item_id}) target_instance_dimensions is empty".format(
                    strategy_id=self.strategy.id, item_id=self.id
                )
            )
            target_instance_dimensions = total_no_data_dimensions
            target_dimensions_md5 = total_no_data_md5
            anomaly_data = [
                self._produce_anomaly_info(check_timestamp, target_instance_dimensions[0], target_dimensions_md5[0])
            ]
            logger.warning(
                (
                    "[nodata] strategy({strategy_id}) item({item_id}) produce anomaly info, "
                    "target_inst_dms({target_inst_dms}), target_dms_md5({target_dms_md5}), "
                    "check_timestamp({check_timestamp}), last_point({last_point})"
                ).format(
                    strategy_id=self.strategy.id,
                    item_id=self.id,
                    target_inst_dms=target_instance_dimensions[0],
                    target_dms_md5=target_dimensions_md5[0],
                    check_timestamp=check_timestamp,
                    last_point=None,
                )
            )

        else:
            # 4.2 有历史维度范围 或者 当前上报数据不为空，尝试恢复整体维度告警（有则恢复）
            self.recover(total_no_data_md5)

            # 5. 生成异常记录，生成规则：1）当前监测点无数据 or 2）当前监测点有数据，但是数据上报时间晚于 last_check_point
            anomaly_data = []
            target_dimensions_md5 = []
            for target_inst_dms in target_instance_dimensions:
                target_dms_md5 = count_md5(target_inst_dms)
                target_dimensions_md5.append(target_dms_md5)
                # 之前检测的数据最后上报点
                last_checkpoint_cache_field = key.LAST_CHECKPOINTS_CACHE_KEY.get_field(
                    strategy_id=self.strategy.id, item_id=self.id, dimensions_md5=target_dms_md5, level=NO_DATA_LEVEL
                )
                last_point = key.LAST_CHECKPOINTS_CACHE_KEY.client.hget(
                    key.LAST_CHECKPOINTS_CACHE_KEY.get_key(), last_checkpoint_cache_field
                )
                if target_dms_md5 not in dimensions_md5_timestamp or (
                    last_point and dimensions_md5_timestamp[target_dms_md5] < int(last_point)
                ):
                    anomaly_data.append(self._produce_anomaly_info(check_timestamp, target_inst_dms, target_dms_md5))
                    logger.warning(
                        (
                            "[nodata] strategy({strategy_id}) item({item_id}) produce anomaly info, "
                            "target_inst_dms({target_inst_dms}), target_dms_md5({target_dms_md5}), "
                            "check_timestamp({check_timestamp}), last_point({last_point})"
                        ).format(
                            strategy_id=self.strategy.id,
                            item_id=self.id,
                            target_inst_dms=target_inst_dms,
                            target_dms_md5=target_dms_md5,
                            check_timestamp=check_timestamp,
                            last_point=last_point,
                        )
                    )
                else:
                    # recovery 历史告警事件
                    self.recover(target_dms_md5)

        # 5. 将当前维度数据和历史维度数据的并集缓存
        self._update_dimensions_checkpoint(
            check_timestamp,
            target_instance_dimensions,
            target_dimensions_md5,
            data_dimensions,
            data_dimensions_mds,
            dimensions_md5_timestamp,
        )
        return anomaly_data

    @staticmethod
    def _process_dimensions(no_data_dimensions, data_points):
        # 上报数据维度
        data_dimensions = []
        # 上报数据维度对应的最新上报时间
        dimensions_md5_timestamp = {}
        # 数据维度 md5 缓存
        data_dimensions_mds = []
        invalid_data = []
        for point in data_points:
            dimensions = point.dimensions
            # 目标维度比数据中的维度范围大，说明数据无效
            if set(no_data_dimensions) - set(dimensions.keys()):
                invalid_data.append(point)
                continue
            # 按目标维度降维
            for k in list(dimensions.keys()):
                if k not in no_data_dimensions:
                    dimensions.pop(k)

            dimensions.update({NO_DATA_TAG_DIMENSION: True})
            dimensions_md5 = count_md5(dimensions)
            if dimensions_md5 not in dimensions_md5_timestamp:
                data_dimensions.append(dimensions)
                data_dimensions_mds.append(dimensions_md5)
                dimensions_md5_timestamp[dimensions_md5] = point.timestamp
            elif point.timestamp > dimensions_md5_timestamp[dimensions_md5]:
                dimensions_md5_timestamp[dimensions_md5] = point.timestamp

        if invalid_data:
            logger.warning(
                (
                    "[nodata] checker got invalid data_points[{invalid_data}] "
                    "where no_data_dimensions is [{no_data_dimensions}]"
                ).format(invalid_data=invalid_data, no_data_dimensions=no_data_dimensions)
            )

        return {
            "data_dimensions": data_dimensions,
            "dimensions_md5_timestamp": dimensions_md5_timestamp,
            "data_dimensions_mds": data_dimensions_mds,
        }

    def _produce_anomaly_id(self, check_timestamp, dimensions_md5):
        return "{dimensions_md5}.{timestamp}.{strategy_id}.{item_id}.{level}".format(
            dimensions_md5=dimensions_md5,
            timestamp=check_timestamp,
            strategy_id=self.strategy.id,
            item_id=self.id,
            level=NO_DATA_LEVEL,
        )

    def _count_anomaly_period(self, check_timestamp, dimensions_md5):
        """
        :summary: 获取无数据检测异常周期
        :return:
        """
        last_anomaly_point = key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.client.hget(
            key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.get_key(),
            key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.get_field(
                strategy_id=self.strategy.id, item_id=self.id, dimensions_md5=dimensions_md5
            ),
        )
        if last_anomaly_point:
            agg_interval = int(self.rt_query_config["agg_interval"])
            anomaly_period = (check_timestamp - int(float(last_anomaly_point))) // agg_interval + 1
        else:
            anomaly_period = 1
            # 记录首次出现无数据告警时的检测点
            key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.client.hset(
                key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.get_key(),
                key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.get_field(
                    strategy_id=self.strategy.id, item_id=self.id, dimensions_md5=dimensions_md5
                ),
                check_timestamp,
            )
            key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.expire()
        return anomaly_period

    def _count_no_data_period(self, check_timestamp, dimensions_md5):
        """
        :summary: 获取无数据上报丢失周期
        :return:
        """
        last_check_point = key.LAST_CHECKPOINTS_CACHE_KEY.client.hget(
            key.LAST_CHECKPOINTS_CACHE_KEY.get_key(),
            key.LAST_CHECKPOINTS_CACHE_KEY.get_field(
                strategy_id=self.strategy.id, item_id=self.id, dimensions_md5=dimensions_md5, level=NO_DATA_LEVEL
            ),
        )
        if last_check_point:
            agg_interval = int(self.rt_query_config["agg_interval"])
            no_data_period = (check_timestamp - int(float(last_check_point))) // agg_interval
            return no_data_period
        else:
            return 0

    def _produce_anomaly_info(self, check_timestamp, target_dimension, target_dms_md5):
        no_data_period = self._count_no_data_period(check_timestamp, target_dms_md5)
        anomaly_period = self._count_anomaly_period(check_timestamp, target_dms_md5)
        if no_data_period > 0:
            anomaly_message = _("当前指标({})已经有{}个周期无数据上报").format(self.data_source.name, no_data_period)
            if anomaly_period < no_data_period:
                anomaly_message += _("，并且数据上报延时{}个周期").format(no_data_period - anomaly_period)
        else:
            anomaly_message = _("当前指标({})已经有{}个周期无数据上报").format(self.data_source.name, anomaly_period)
        anomaly_info = {
            "data": {
                "record_id": "{dimensions_md5}.{timestamp}".format(
                    dimensions_md5=target_dms_md5, timestamp=check_timestamp
                ),
                "value": NO_DATA_VALUE,
                "values": {"timestamp": check_timestamp, "loads": NO_DATA_VALUE},
                "dimensions": target_dimension,
                "time": check_timestamp,
            },
            "anomaly": {
                str(NO_DATA_LEVEL): {
                    "anomaly_message": anomaly_message,
                    "anomaly_id": self._produce_anomaly_id(check_timestamp, target_dms_md5),
                    "anomaly_time": arrow.utcnow().format("YYYY-MM-DD HH:mm:ss"),
                }
            },
            "strategy_snapshot_key": self.strategy.gen_strategy_snapshot(),
        }
        return anomaly_info

    def _update_dimensions_checkpoint(
        self,
        check_timestamp,
        target_instance_dimensions,
        target_dimensions_md5,
        data_dimensions,
        data_dimensions_md5,
        dimensions_md5_timestamp,
    ):
        """
        :summary: 对比目标无数据维度和上报数据维度，将所有维度存缓存，并将目标维度不存在记为异常
        :param check_timestamp: 检测时刻
        :param target_instance_dimensions（list）: 无数据目标维度范围
        :param target_dimensions_md5（list）: 无数据目标维度 MD5 缓存
        :param data_dimensions（list）: 上报维度数据
        :param data_dimensions_md5（list）: 上报维度数据  MD5 缓存
        :param dimensions_md5_timestamp（dict）: 上报维度数据上报时刻
        :return:
        """
        redis_pipeline = None
        processed = set()
        all_dimensions_md5 = target_dimensions_md5 + data_dimensions_md5
        loop = 0
        for _dms in chain(target_instance_dimensions, data_dimensions):
            dimensions_md5 = all_dimensions_md5[loop]
            loop += 1
            if dimensions_md5 in processed:
                continue
            processed.add(dimensions_md5)

            check_result = CheckResult(
                strategy_id=self.strategy.id,
                item_id=self.id,
                dimensions_md5=dimensions_md5,
                level=NO_DATA_LEVEL,
                service_type="nodata",
            )
            if redis_pipeline is None:
                redis_pipeline = check_result.CHECK_RESULT
            if dimensions_md5 not in data_dimensions_md5:
                name = "{}|{}".format(check_timestamp, ANOMALY_LABEL)
            else:
                name = "{}|{}".format(check_timestamp, str(NO_DATA_VALUE))

            try:
                # 1. 缓存数据(检测结果缓存) type:SortedSet
                kwargs = {name: check_timestamp}
                check_result.add_check_result_cache(**kwargs)

                if self.no_data_config.get("is_enabled"):
                    # 2. 缓存数据(维度缓存) type:Hash
                    check_result.update_key_to_dimension(_dms)

            except Exception as e:
                msg = "set nodata check result cache error:%s" % e
                logger.exception(msg)

        if redis_pipeline:
            check_result.expire_key_to_dimension()
            redis_pipeline.execute()

        # 更新last_checkpoint，计算无数据
        for _dimensions_md5, point_timestamp in list(dimensions_md5_timestamp.items()):
            try:
                CheckResult.update_last_checkpoint_by_dimensions_md5(
                    self.strategy.id,
                    self.id,
                    _dimensions_md5,
                    point_timestamp,
                    NO_DATA_LEVEL,
                )
            except Exception as e:
                msg = "set nodata check result cache last_check_point error:%s" % e
                logger.exception(msg)
        # 记录每个策略监控项的最后无数据检测时间，避免同一时刻的数据被多次检测，否则会导致除了第一次能取到数据，其他检测都报无数据
        CheckResult.update_last_checkpoint_by_dimensions_md5(
            self.strategy.id, self.id, LATEST_NO_DATA_CHECK_POINT, check_timestamp, NO_DATA_LEVEL
        )
        CheckResult.expire_last_checkpoint_cache()

    def recover(self, dimensions_md5):
        key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.client.hdel(
            key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.get_key(),
            key.NO_DATA_LAST_ANOMALY_CHECKPOINTS_CACHE_KEY.get_field(
                strategy_id=self.strategy.id, item_id=self.id, dimensions_md5=dimensions_md5
            ),
        )
        event_cache_key = key.EVENT_ID_CACHE_KEY.get_key(
            strategy_id=self.strategy.id, item_id=self.id, dimensions_md5=dimensions_md5
        )
        event_id = key.EVENT_ID_CACHE_KEY.client.get(event_cache_key)
        if event_id:
            Event.objects.filter(event_id=event_id).update(status=Event.EventStatus.RECOVERED, end_time=timezone.now())
            EventAction.objects.create(
                operate=EventAction.Operate.RECOVER,
                status=EventAction.Status.SUCCESS,
                event_id=event_id,
                message=_("当前维度检测到新的上报数据，无数据告警已恢复"),
            )
            key.EVENT_ID_CACHE_KEY.client.delete(event_cache_key)
