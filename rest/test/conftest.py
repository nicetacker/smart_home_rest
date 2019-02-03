# coding: utf-8

import pytest

from unittest.mock import MagicMock
from falcon import testing

from rest.app import data_store

from rest.app import create_app


@pytest.fixture
def mock_store():
    return MagicMock()

@pytest.fixture
def mock_handle():
    return MagicMock()

@pytest.fixture
def mock_broadlink_api():
    return MagicMock()

@pytest.fixture
def client(mock_handle, mock_broadlink_api):
    store = data_store.Store()
    api = create_app(store, mock_handle, mock_broadlink_api)
    yield testing.TestClient(api)
    store.clear()
