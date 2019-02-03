# coding:utf-8

import pytest

from falcon import testing
from rest.app import create_app


def test_initial_base_device_is_none(client):
    resp = client.simulate_get("/broadlink/base_devices")
    expect_body = []
    assert(resp.status_code == 200)
    assert(resp.json == expect_body)


def test_post_base_device(client):
    post_data = {
        "type": "0x2737",
        "host": "192.168.100.100",
        "mac": "1234abcd5678"
    }
    resp = client.simulate_post("/broadlink/base_devices", json=post_data)
    assert(resp.status_code == 201)
    assert(resp.headers["location"] == "/broadlink/base_devices/1")

    post_data = {
        "type": "0x2737",
        "host": "192.168.100.101",
        "mac": "1234ffffdddd"
    }
    resp = client.simulate_post("/broadlink/base_devices", json=post_data)
    assert(resp.status_code == 201)
    assert(resp.headers["location"] == "/broadlink/base_devices/2")

    resp = client.simulate_get("/broadlink/base_devices")
    expect_body = [
        {
            "id": 1,
            "type": "0x2737",
            "host": "192.168.100.100",
            "mac": "1234abcd5678"
        },
        {
            "id": 2,
            "type": "0x2737",
            "host": "192.168.100.101",
            "mac": "1234ffffdddd"
        }
    ]
    assert(resp.status_code == 200)
    assert(resp.json == expect_body)

    resp = client.simulate_get("/broadlink/base_devices/1")
    expect_body = {
        "id": 1,
        "type": "0x2737",
        "host": "192.168.100.100",
        "mac": "1234abcd5678"
    }
    assert(resp.status_code == 200)
    assert(resp.json == expect_body)

    resp = client.simulate_get("/broadlink/base_devices/2")
    expect_body = {
        "id": 2,
        "type": "0x2737",
        "host": "192.168.100.101",
        "mac": "1234ffffdddd"
    }
    assert(resp.status_code == 200)
    assert(resp.json == expect_body)

    resp = client.simulate_get("/broadlink/base_devices/3")
    assert(resp.status_code == 404)


def test_update_base_device(client):
    # Post two datas
    post_data = {
        "type": "0x2737",
        "host": "192.168.100.100",
        "mac": "1234abcd5678"
    }
    client.simulate_post("/broadlink/base_devices", json=post_data)
    post_data = {
        "type": "0x2737",
        "host": "192.168.100.101",
        "mac": "1234ffffdddd"
    }
    resp = client.simulate_post("/broadlink/base_devices", json=post_data)

    # Update One
    post_data = {
        "type": "0x1234",
        "host": "192.168.100.111",
        "mac": "1234abcd5678"
    }
    resp = client.simulate_post("/broadlink/base_devices", json=post_data)

    resp = client.simulate_get("/broadlink/base_devices")
    expect_body = [
        {
            "id": 1,
            "type": "0x1234",
            "host": "192.168.100.111",
            "mac": "1234abcd5678"
        },
        {
            "id": 2,
            "type": "0x2737",
            "host": "192.168.100.101",
            "mac": "1234ffffdddd"
        }
    ]
    assert(resp.status_code == 200)
    assert(resp.json == expect_body)


def test_learn_base_device(client, mock_broadlink_api):
    # prepare
    datas = [
        {"type": "0x2737",
            "host": "192.168.100.100", "mac": "1234abcd5678"},
        {"type": "0x2737",
            "host": "192.168.100.101", "mac": "1234ffffdddd"}
    ]
    for data in datas:
        resp = client.simulate_post("/broadlink/base_devices", json=data)
        assert(resp.status_code == 201)

    data = {"device": "tv", "action":  "off"}
    resp = client.simulate_put("/broadlink/base_devices/4/learn", json=data)
    assert(resp.status_code == 404)

    mock_broadlink_api.learn.return_value = "abcde"
    resp = client.simulate_put("/broadlink/base_devices/1/learn", json=data)
    assert(resp.status_code == 200)

    mock_broadlink_api.learn.return_value = "hijkw"
    resp = client.simulate_put("/broadlink/base_devices/2/learn", json=data)
    assert(resp.status_code == 200)

    resp = client.simulate_get("/commands")
    assert(resp.status_code == 200)


def test_discover(client, mock_broadlink_api):
    mock_broadlink_api.discover.return_value = []
    resp = client.simulate_get('/broadlink/discover')
    assert(resp.status_code == 200)
