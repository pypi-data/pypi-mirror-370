import json
import unittest

from sagemaker_studio_analytics_extension.magics import (
    _build_response,
)


class TestWebSocketResponse(unittest.TestCase):
    def test_response_serialization(self):
        self.assertEqual(
            json.dumps(_build_response("id", "error", True, "emr", "connect")),
            '{"namespace": "sagemaker-analytics", "cluster_id": "id", "error_message": "error", '
            '"success": true, "service": "emr", "operation": "connect"}',
        )

    def test_response_deserialization(self):
        deserialized_object = json.loads(
            json.dumps(_build_response("id", "error", True, "emr", "connect"))
        )
        self.assertEqual(deserialized_object["namespace"], "sagemaker-analytics")
        self.assertEqual(deserialized_object["cluster_id"], "id")
        self.assertEqual(deserialized_object["error_message"], "error")
        self.assertEqual(deserialized_object["success"], True)
        self.assertEqual(deserialized_object["service"], "emr")
        self.assertEqual(deserialized_object["operation"], "connect")

    def test_response_serialization_none_error(self):
        self.assertEqual(
            json.dumps(_build_response("id", None, False, "emr", "connect")),
            '{"namespace": "sagemaker-analytics", "cluster_id": "id", "error_message": null, "success": '
            'false, "service": "emr", "operation": "connect"}',
        )

    def test_response_deserialization_none_error(self):
        deserialized_object = json.loads(
            json.dumps(_build_response("id", None, False, "emr", "connect"))
        )
        self.assertEqual(deserialized_object["namespace"], "sagemaker-analytics")
        self.assertEqual(deserialized_object["cluster_id"], "id")
        self.assertEqual(deserialized_object["error_message"], None)
        self.assertEqual(deserialized_object["success"], False)
        self.assertEqual(deserialized_object["service"], "emr")
        self.assertEqual(deserialized_object["operation"], "connect")
