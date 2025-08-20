import json
from io import StringIO

from django.contrib.auth.models import User

from germanium.decorators import data_provider
from germanium.test_cases.client import ClientTestCase
from germanium.tools import assert_equal

from security.backends.elasticsearch.models import PartitionedLog
from security.management import call_command


TRUNCATION_CHAR = '…'


class BaseTestCase(ClientTestCase):
    databases = ['default', 'security']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PartitionedLog.INSTANT_REFRESH = True

    @data_provider
    def create_user(self, username='test', email='test@localhost'):
        return User.objects._create_user(username, email, 'test', is_staff=True, is_superuser=True)


def test_call_command(*args, **kwargs):
    call_command(*args, **kwargs, stdout=StringIO(), stderr=StringIO())


def assert_equal_vector(logstash_output, expected_index, expected_version, expected_logger_id, expected_data):
    log_level, logger, data = logstash_output.split(':', 2)
    assert_equal(log_level, "INFO")
    assert_equal(logger, "security.vector")
    result_data = json.loads(data)
    assert_equal(result_data["version"], expected_version)
    assert_equal(result_data["index_name"], expected_index)
    assert_equal(result_data["logger_id"], str(expected_logger_id))
    for k, v in expected_data.items():
        assert_equal(result_data.get(k), v, f'Invalid data "{k}" ({result_data.get(k)} != {v})')


def assert_equal_logstash(logstash_output, expected_index, expected_version, expected_logger_id, expected_data):
    prefix_and_index, version, logger_id, data = logstash_output.split(' ', 3)
    assert_equal(prefix_and_index, f'INFO:security.logstash:{expected_index}')
    assert_equal(version, str(expected_version))
    assert_equal(logger_id, str(expected_logger_id))
    parsed_data = json.loads(data)
    for k, v in expected_data.items():
        assert_equal(parsed_data.get(k), v, f'Invalid data "{k}" ({parsed_data.get(k)} != {v})')


def assert_equal_log_data(captured_log, expected_data):
    for k, v in expected_data.items():
        assert_equal(getattr(captured_log, k), v)
