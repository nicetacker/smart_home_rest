# coding: utf-8

import falcon

from . import data_store
from . import resource_broadlink
from . import resource_ifttt
from . import resource_command

from .resource_broadlink import BaseDeviceFactory
from .resource_ifttt import WebhookCommandFactory


class Collection(object):
    def __init__(self, factory, store):
        self._store = store
        self._factory = factory

    def on_get(self, req, resp):
        resp.media = self._store.get_all(self._factory.path())

    def on_post(self, req, resp):
        self._factory.validate(req.media)

        new_id = self._store.update(
            self._factory.create(req.media))

        resp.status = falcon.HTTP_201
        resp.location = "/{path}/{id}".format(
            path=self._factory.path(), id=new_id)


class Item(object):
    def __init__(self, factory, store):
        self._store = store
        self._factory = factory

    def on_get(self, req, resp,  id):
        ret = self._store.get(self._factory.path(), id)
        if not ret:
            raise falcon.HTTPNotFound()
        resp.media = ret


def create_app(store, handle, broadlink_api):
    api = falcon.API()

    # Commands
    api.add_route('/commands',
                  Collection(resource_command.CommandFactory(), store))
    api.add_route('/commands/{id}',
                  Item(resource_command.CommandFactory(), store))
    api.add_route('/commands/{id}/run', resource_command.Runner(store, handle))

    # Broadlink
    api.add_route('/broadlink/discover',
                  resource_broadlink.Discover(broadlink_api))
    api.add_route('/broadlink/base_devices',
                  Collection(BaseDeviceFactory(), store))
    api.add_route('/broadlink/base_devices/{id}',
                  Item(BaseDeviceFactory(), store))
    api.add_route('/broadlink/base_devices/{id}/learn',
                  resource_broadlink.Learner(broadlink_api, store))

    # Ifttt webhook
    api.add_route('/ifttt', resource_ifttt.Resource(store))
    api.add_route('/ifttt/webhooks',
                  Collection(WebhookCommandFactory(), store))

    return api


def get_app():
    # Create resources
    store = data_store.Store()
    broadlink_api = resource_broadlink.API()

    # Create Handle
    handle = resource_command.Handle()
    handle.add("ifttt_webhook", resource_ifttt.Handle(store))
    handle.add("broadlink", resource_broadlink.Handle(store, broadlink_api))

    return create_app(store, handle, broadlink_api)
