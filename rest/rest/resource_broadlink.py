# coding: utf-8

import json
import time

import broadlink
import falcon
from falcon.media.validators import jsonschema

from .data_store import StoreItem, StoreItemFactory
from .resource_command import Command

PATH_BASE_DEVICE = "broadlink/base_devices"

learn_schema = {
    "required": ["device", "action"],
    "properties": {
        "device": {"type": "string"},
        "action": {"type": "string"},
    }
}


class BroadlinkCommandFactory(StoreItemFactory):
    def __init__(self, api, store):
        self._store = store
        self._api = api

    def create(self, data):
        device_data = self._store.get(PATH_BASE_DEVICE, id)

        data["type"] = "broadlink"
        data["param"] = {
            "ir_code": ir_data,
            "base_device_id": device_data["id"]
        }
        return Command(data)

    def path(self):
        return PATH_COMMADS


class Learner(object):
    def __init__(self, api, store):
        self._store = store
        self._api = api

    @jsonschema.validate(learn_schema)
    def on_put(self, req, resp, id):
        device_data = self._store.get(PATH_BASE_DEVICE, id)
        if not device_data:
            raise falcon.HTTPNotFound()
        device_data["id"] = int(id)

        ir_data = self._api.learn(device_data)

        req.media["type"] = "broadlink"
        req.media["param"] = {
            "ir_code": ir_data,
            "base_device_id": device_data["id"]
        }
        self._store.update(Command(req.media))


class Discover(object):
    def __init__(self, api):
        self._api = api

    def on_get(self, req, resp):
        resp.media = self._api.discover()


class BaseDevice(StoreItem):
    def __init__(self, data):
        self._data = data
        self._path = "broadlink/base_devices"

    def equal(self, data):
        return self._data["mac"] == data["mac"]


class BaseDeviceFactory(StoreItemFactory):
    def __init__(self):
        self._scema = {"required": ["type", "host", "mac"]}

    def path(self):
        return PATH_BASE_DEVICE

    def create(self, data):
        return BaseDevice(data)


class API(object):
    def discover(self):
        def get_data(device):
            return {
                "type": hex(device.devtype),
                "host": device.host[0],
                "mac":  ''.join(format(x, '02x') for x in device.mac)
            }
        devices = broadlink.discover(timeout=5)
        return [get_data(d) for d in devices if d.auth()]

    def send(self, dev_data, command):
        dev = self.gen_device(dev_data)
        dev.send_data(
            bytearray.fromhex(''.join(command["param"]["ir_code"])))

    def learn(self, dev_data):
        dev = self.gen_device(dev_data)

        data = None
        timeout = 30
        dev.enter_learning()
        while (timeout > 0):
            time.sleep(2)
            timeout -= 2
            data = dev.check_data()
            if data:
                return ''.join(format(x, '02x') for x in bytearray(data))

        raise falcon.HTTPBadRequest("Command not received")

    def gen_device(self, dev_data):
        dev_type, host, mac = dev_data["type"], dev_data["host"], bytearray.fromhex(
            dev_data["mac"])
        dev = broadlink.gendevice(int(dev_type, 0), (host, 80), mac)
        if not dev.auth():
            raise falcon.HTTPBadRequest("device auth failed.")
        return dev


class Handle(object):
    def __init__(self, store, api):
        self._store = store
        self._api = api

    def run(self, command):
        devices = self._store.get_all(PATH_BASE_DEVICE)
        dev_data = next(
            (d for d in devices if d["id"] == command["param"]["base_device_id"]), None)
        if not dev_data:
            raise falcon.HTTPBadRequest("Device not found")

        self._api.send(dev_data, command)
