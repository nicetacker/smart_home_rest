# coding:utf-8

import pytest

from falcon import testing
from rest.app import create_app


def test_ifttt_key_post(client):
    # Responce should be initial data.
    resp = client.simulate_get('/ifttt')
    expect_resp = {
        "webhook_key": "",
    }
    assert(resp.status_code == 200)
    #assert(resp.json == expect_resp)

    # Put IFTTT  key
    key = "abcd1234ABCD5678"
    post_data = {
        "webhook_key":  key
    }
    resp = client.simulate_post('/ifttt', json=post_data)
    assert(resp.status_code == 200)

    # Responce should be updated
    resp = client.simulate_get('/ifttt')
    assert(resp.status_code == 200)
    expect_resp = {
            "webhook_key": key,
    }
    assert(resp.json == expect_resp)


def test_ifttt_invalid_key(client):
    # Put should be failed
    post_data = {
        "invalid": "json_data"
    }
    resp = client.simulate_post('/ifttt', json=post_data)
    assert(resp.status_code == 400)


def test_post_webhooks(client):
    post_data1 = {
        "device": "tv",
        "action": "off",
        "param": {
            "event": "tv_off",
            "values": {
                "value1": "one",
                "value2": "two",
                "value3": "three"
            }
        }
    }
    resp = client.simulate_post("/ifttt/webhooks", json=post_data1)
    assert(resp.status_code == 201)
    assert(resp.headers["location"] == "/commands/1")

    post_data2 = {
        "device": "tv",
        "action": "on",
        "param": {
            "event": "tv_on",
            "values": {
                "value1": "ein",
                "value2": "twei",
                "value3": "san"
            }
        }
    }
    resp = client.simulate_post("/ifttt/webhooks", json=post_data2)
    assert(resp.status_code == 201)
    assert(resp.headers["location"] == "/commands/2")

    # Responce should be updated
    resp = client.simulate_get("/commands")
    assert(resp.status_code == 200)
    expect_resp = [
        {
            "id": 1,
            "device": "tv",
            "action": "off",
            "type": "ifttt_webhook",
            "param": {
                "event": "tv_off",
                "values": {
                    "value1": "one",
                    "value2": "two",
                    "value3": "three"
                }
            }
        },
        {
            "id": 2,
            "device": "tv",
            "action": "on",
            "type": "ifttt_webhook",
            "param": {
                "event": "tv_on",
                "values": {
                    "value1": "ein",
                    "value2": "twei",
                    "value3": "san"
                }
            }
        }
    ]
    assert(resp.json == expect_resp)

