# coding: utf-8

import json

from redis import StrictRedis, RedisError
import jsonschema


class StoreItemFactory(object):
    def __init__(self, required_key):
        self._scema = None

    def validate(self, dic):
        if self._scema:
            try:
                jsonschema.validate(
                    dic, self._scema,
                    format_checker=jsonschema.FormatChecker()
                )
            except jsonschema.ValidationError as e:
                raise falcon.HTTPBadRequest(
                    'Request data failed validation',
                    description=e.message
                )

    def create(self, data):
        return data

    def path(self):
        return "item"


class StoreItem(object):
    def __init__(self):
        self._path = None
        self._data = {}

    def path(self):
        return self._path

    def serialize(self):
        return json.dumps(self._data)

    def equal(self, data):
        return NotImplementedError()

    def set_id(self, id):
        self._data["id"] = id


class Store:
    def __init__(self):
        self.redis = StrictRedis(host="localhost", db=0,
                                 socket_connect_timeout=2, socket_timeout=2)

    def get(self, name, id):
        if int(id) == 0:
            return None
        item = self.redis.lindex(name, int(id) - 1)
        if item:
            return json.loads(item)

    def get_all(self, name):
        return [json.loads(item) for item in self.redis.lrange(name, 0, -1)]

    def add(self, value):
        new_id = self.redis.llen(value.path()) + 1
        value.set_id(new_id)
        self.redis.rpush(value.path(), value.serialize())
        return new_id

    def update(self, value):
        items = self.get_all(value.path())

        for idx, item in enumerate(items):
            if value.equal(item):
                value.set_id(idx + 1)
                self.redis.lset(value.path(), idx, value.serialize())
                return idx + 1

        return self.add(value)

    def set_item(self, key, value):
        self.redis.set(key, json.dumps(value))

    def get_item(self, key):
        item = self.redis.get(key)
        if item:
            return json.loads(item)

    def clear(self):
        self.redis.flushdb()
