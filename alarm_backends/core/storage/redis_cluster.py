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

from bkmonitor.models import CacheRouter
from alarm_backends.core.storage.redis import Cache, CACHE_BACKEND_CONF_MAP


__doc__ = """

"""


class RedisNode(object):

    redis_type = "RedisCache"

    def __init__(self, host, port, password=None):
        self.host = host
        self.port = port
        self.password = password
        self._connection_kwargs = {"db": 0, "host": self.host, "port": self.port, "password": password}
        self._connection_kwargs.update({"decode_responses": True, "encoding": "utf-8"})
        self._instance_pool = {}

    @property
    def connection_kwargs(self):
        return self._connection_kwargs

    @property
    def node_id(self):
        return f"{self.redis_type}-{self.host}:{self.port}"

    def gen_connection_conf(self, cache_backend):
        conf = self.connection_kwargs.copy()
        conf["db"] = CACHE_BACKEND_CONF_MAP.get(cache_backend, {}).get("db", 0)
        return conf

    def instance(self, cache_backend):
        backend = f"{self.node_id}:{cache_backend}"
        conf = self.gen_connection_conf(cache_backend)
        conf["_cache_type"] = self.redis_type
        return Cache(backend, conf)


class SentinelRedisNode(RedisNode):

    redis_type = "SentinelRedisCache"

    def __init__(self, host, port, master_name, password=None, sentinel_password=None):
        super().__init__(host, port, password)
        self.master_name = master_name
        self._connection_kwargs.update({"master_name": master_name})
        self.sentinel_kwargs = {}
        if sentinel_password:
            self.sentinel_kwargs["password"] = sentinel_password

    @property
    def node_id(self):
        return f"{self.redis_type}-{self.host}:{self.port} {self.master_name}"


def setup_client(node, backend):
    client = None
    if node.cache_type == RedisNode.redis_type:
        client = setup_redis_client(node, backend)
    if node.cache_type == SentinelRedisNode.redis_type:
        client = setup_sentinel_client(node, backend)
    if client is None:
        raise Exception(f"nonsupport cache type: {node.cache_type}")
    return client


def setup_redis_client(node, backend):
    redis_node = RedisNode(node.host, node.port, node.password)
    return redis_node.instance(backend)


def setup_sentinel_client(node, backend):
    master_name = node.connection_kwargs["master_name"]
    sentinel_password = node.connection_kwargs.get("sentinel_password")
    sentinel_node = SentinelRedisNode(
        node.host, node.port, master_name, password=node.password, sentinel_password=sentinel_password
    )
    return sentinel_node.instance(backend)


class KeyRouterMixin(object):
    def strategy_id_from_command(self, *args, **kwargs):
        key = self.key_from_command(*args, **kwargs)
        return self.strategy_id_from_key(key)

    def strategy_id_from_key(self, key):
        return getattr(key, "strategy_id", 0) if key else 0

    def key_from_command(self, *args, **kwargs):
        key = kwargs.get("name", None)
        if key is None and args:
            key = args[0]
        return key


class RedisProxy(KeyRouterMixin):
    def __init__(self, backend):
        self.backend = backend
        self._pipeline = None
        self._client_pool = {}

    def pipeline(self, *args, **kwargs):
        if self._pipeline is None:
            self._pipeline = PipelineProxy(self, *args, **kwargs)
        return self._pipeline

    def get_client(self, node):
        if node.id not in self._client_pool:
            self._client_pool[node.id] = setup_client(node, self.backend)

        return self._client_pool[node.id]

    def __getattr__(self, name):
        def handle(*args, **kwargs):
            exception = None
            strategy_id = self.strategy_id_from_command(*args, **kwargs)
            cache_node = get_node_by_strategy_id(strategy_id)
            client = self.get_client(cache_node)
            command = getattr(client, name)

            for _ in range(3):
                try:
                    return command(*args, **kwargs)
                except ConnectionError as err:
                    exception = err
                    client.refresh_instance()
            if exception:
                raise exception

        return handle


class PipelineProxy(KeyRouterMixin):

    ALLOWED_METHOD = ["execute"]

    def __init__(self, node_proxy, *args, **kwargs):
        self.node_proxy = node_proxy
        self._pipeline_pool = {}
        self.init_params = (args, kwargs)
        self.command_stack = []

    def pipeline_instance(self, node):
        if node.id not in self._pipeline_pool:
            self._pipeline_pool[node.id] = self.node_proxy.get_client(node).pipeline(
                *self.init_params[0], **self.init_params[1]
            )

        return self._pipeline_pool[node.id]

    def execute(self):
        p_result = {}
        result = []
        for node_id, pipeline_instance in self._pipeline_pool.items():
            p_result[node_id] = list(reversed(getattr(pipeline_instance, "execute")()))
        for cmd in self.command_stack:
            result.append(p_result[cmd].pop())
        self.command_stack = []
        return result

    def __getattr__(self, name):
        def handle(*args, **kwargs):
            key = self.key_from_command(*args, **kwargs)
            if key is None:
                if name not in self.ALLOWED_METHOD:
                    return self.execute()
            strategy_id = self.strategy_id_from_key(key)
            cache_node = get_node_by_strategy_id(strategy_id)

            pipeline = self.pipeline_instance(cache_node)
            command = getattr(pipeline, name)
            self.command_stack.append(cache_node.id)
            return command(*args, **kwargs)

        return handle


STRATEGY_ROUTER_CACHE = {}


def get_node_by_strategy_id(strategy_id: int):
    global STRATEGY_ROUTER_CACHE
    try:
        return STRATEGY_ROUTER_CACHE[strategy_id]
    except KeyError:
        node = CacheRouter.get_node_by_strategy_id(strategy_id)
        STRATEGY_ROUTER_CACHE[strategy_id] = node
        return node
