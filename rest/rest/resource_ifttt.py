
# coding: utf-8

import json

import falcon
import requests
from falcon.media.validators import jsonschema

from .data_store import StoreItemFactory
from .resource_command import PATH_COMMADS, Command

# TBD: define scemas in text file
ifff_command_scema = {
  "required": [
    "device",
    "action",
    "param"
  ],
  "properties": {
    "device": {
      "$id": "#/properties/device",
      "type": "string"
    },
    "action": {
      "$id": "#/properties/action",
      "type": "string"
    },
    "param": {
      "$id": "#/properties/param",
      "type": "object",
      "required": [
        "event"
      ],
      "properties": {
        "event": {
          "$id": "#/properties/param/properties/event",
          "type": "string"
        },
        "values": {
          "$id": "#/properties/param/properties/values",
          "type": "object",
          "properties": {
            "value1": {
              "$id": "#/properties/param/properties/values/properties/value1",
              "type": "string"
            },
            "value2": {
              "$id": "#/properties/param/properties/values/properties/value2",
              "type": "string",
            },
            "value3": {
              "$id": "#/properties/param/properties/values/properties/value3",
              "type": "string",
            }
          }
        }
      }
    }
  }
}


class WebhookCommandFactory(StoreItemFactory):
    def __init__(self):
        self._scema = ifff_command_scema

    def create(self, data):
        data["type"] = "ifttt_webhook"
        return Command(data)

    def path(self):
        return PATH_COMMADS


key_schema = {
    "required": ["webhook_key"],
    "properties": {"webhook_key": {"type": "string"}}
}


class Resource(object):
    def __init__(self, store):
        self._store = store

    def on_get(self, req, resp):
        key = self._store.get_item("IFTTT_KEY") or ""
        resp.media = {"webhook_key": key}

    @jsonschema.validate(key_schema)
    def on_post(self, req, resp):
        key = req.media.get("webhook_key")
        self._store.set_item("IFTTT_KEY", key)


class Handle(object):
    def __init__(self, store):
        self._store = store

    def run(self, command):
        key = self._store.item("IFTTT_KEY"),
        if not key:
            raise falcon.HTTPBadRequest()
        param = command["param"]
        url = "https://maker.ifttt.com/trigger/{event}/with/key/{key}".format(
            event=param["event"], key=key)

        if "values" in param:
            requests.post(url, json=param["values"])
        else:
            requests.post(url)
