
# coding: utf-8

import json
import falcon

from .data_store import StoreItem

PATH_COMMADS = "commands"


class CommandFactory(object):
    def create(self, stream):
        raise falcon.HTTPBadRequest("Resource creation not allowed")

    def path(self):
        return PATH_COMMADS


class Command(StoreItem):
    def __init__(self, data):
        self._data = data
        self._path = "commands"

    def equal(self, data):
        return self._data["device"] == data["device"] and self._data["action"] == data["action"]


class Runner(object):
    def __init__(self, store, handle):
        self._store = store
        self._handle = handle

    def on_put(self, req, resp, id):
        command = self._store.get(PATH_COMMADS, id)
        if not command:
            raise falcon.HTTPNotFound()
        command["id"] = int(id)
        self._handle.run(command)


class Handle(object):
    def __init__(self):
        self._handles = {}

    def add(self, cmd_type, handle):
        self._handles[cmd_type] = handle

    def run(self, cmd):
        cmd_type = cmd["type"]
        if not cmd_type in self._handles:
            return False

        return self._handles[cmd_type].run(cmd)
