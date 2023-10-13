import pytest
import json

@pytest.fixture
def api_data():
    with open('test/data/patreon_data.json', 'r') as data_file:
        api = json.load(data_file)
    return api
