import pytest
import json

@pytest.fixture
def api_data():
    with open('test/data/patreon_data.json', 'r') as data_file:
        api = json.load(data_file)
    return api

@pytest.fixture
def media_data():
    with open('test/data/media_data.json', 'r') as data_file:
        api = json.load(data_file)
    return api

@pytest.fixture
def api_multipost_data():
    with open('test/data/patreon_multiimage_data.json', 'r') as data_file:
        api = json.load(data_file)
    return api
