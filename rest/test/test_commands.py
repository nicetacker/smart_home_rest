# coding:utf-8

import pytest

from falcon import testing
from rest.app import create_app


def test_initial_requests_is_empty(client):
    # Responce should be initial data.
    resp = client.simulate_get('/commands')
    expect_resp = []
    assert(resp.status_code == 200)
    assert(resp.json == expect_resp)

    resp = client.simulate_get('/commands/1')
    assert(resp.status_code == 404)

    resp = client.simulate_put('/commands/1/run')
    assert(resp.status_code == 404)


def test_run_command(client, mock_handle):
    # Prepare data
    post_data = {
        "device": "tv",
        "action": "off",
        "param": {
            "event": "tv_off",
            "values" : {
                "value1": "one",
                "value2": "two",
                "value3": "three"
            }
        }
    }
    client.simulate_post("/ifttt/webhooks", json=post_data)

    # Run command
    resp = client.simulate_put("/commands/1/run", json=post_data)
    assert(resp.status_code == 200)
    expect_data = {
        "id": 1,
        "device": "tv",
        "action": "off",
        "type": "ifttt_webhook",
        "param": {
            "event": "tv_off",
            "values" : {
                "value1": "one",
                "value2": "two",
                "value3": "three"
            }
        }
    }
    mock_handle.run.assert_called_with(expect_data)

    # Invalid id
    resp = client.simulate_get('/commands/2')
    assert(resp.status_code == 404)
    resp = client.simulate_get('/commands/2/run')

def test_post_same_command_will_updated(client, mock_handle):
    # Prepare data
    post_data = {
        "device": "tv",
        "action": "off",
        "param": {
            "event": "tv_off",
            "values" : {
                "value1": "one",
                "value2": "two",
                "value3": "three"
            }
        }
    }
    client.simulate_post("/ifttt/webhooks", json=post_data)

    # Update command
    post_data = {
        "device": "tv",
        "action": "off",
        "param": {
            "event": "new_event",
            "values" : {
                "value1": "val1",
                "value2": "foo",
                "value3": "bar"
            }
        }
    }
    client.simulate_post("/ifttt/webhooks", json=post_data)

    # Run command
    resp = client.simulate_put("/commands/1/run", json=post_data)
    assert(resp.status_code == 200)
    expect_data = {
        "id": 1,
        "device": "tv",
        "action": "off",
        "type": "ifttt_webhook",
        "param": {
            "event": "new_event",
            "values" : {
                "value1": "val1",
                "value2": "foo",
                "value3": "bar"
            }
        }
    }
    mock_handle.run.assert_called_with(expect_data)


