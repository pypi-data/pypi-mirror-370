import time

from django.test import override_settings

from security.backends.elasticsearch.tests import store_elasticsearch_log
from security.backends.elasticsearch.models import Log, PartitionedLog
from security.backends.testing import capture_security_logs
from .base import BaseTestCase


class TestNonPartitionedLog(Log):
    class Index:
        name = "test-log"


class TestPartitionedLog(PartitionedLog):
    class Index:
        name = "test-log*"


@override_settings(SECURITY_BACKEND_WRITERS={})
class PartitionedLogTestCase(BaseTestCase):

    @store_elasticsearch_log()
    def test_save_and_retrieve_from_semi_partitioned_index(self):
        with capture_security_logs():
            TestNonPartitionedLog.init()
            doc_nonpartitioned = TestNonPartitionedLog(slug="test")
            doc_nonpartitioned.save()
            time.sleep(1)  # Wait for reindex

            TestPartitionedLog.init()
            doc_partitioned = TestPartitionedLog(slug="test_2")
            doc_partitioned.save()

            time.sleep(1)

            # Check that we are able to retrieve document before and after partitioning
            retrieved_doc = TestPartitionedLog.get(id=doc_nonpartitioned.pk)
            assert retrieved_doc
            retrieved_doc = TestPartitionedLog.get(id=doc_partitioned.pk)
            assert retrieved_doc
