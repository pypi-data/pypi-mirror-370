import unittest
from unittest.mock import MagicMock

from sagemaker_studio_analytics_extension.resource.emr.auth import (
    ClusterSessionCredentialsProvider,
)


class TestClusterSessionCredentialsProvider(unittest.TestCase):
    def get_emr_token_api_response(self):
        EMR_TOKEN_API_RESPONSE = {
            "Credentials": {
                "UsernamePassword": {
                    "Username": "user1",
                    "Password": "pwd1",
                }
            },
            "ExpiresAt": 1637821901.071,
        }
        return EMR_TOKEN_API_RESPONSE

    def test_get_cluster_session_credential(self):
        mock_emr_client = MagicMock()
        mock_emr_client.get_cluster_session_credentials.return_value = (
            self.get_emr_token_api_response()
        )
        under_test = ClusterSessionCredentialsProvider()

        dummy_execution_role_arn = "role_arn"
        dummy_cluster_id = "cluster_id"

        actual_credentials = under_test.get_cluster_session_credentials(
            emr_client=mock_emr_client,
            cluster_id=dummy_cluster_id,
            emr_execution_role_arn=dummy_execution_role_arn,
        )

        assert actual_credentials.username == "user1"
        assert actual_credentials.password == "pwd1"
        mock_emr_client.get_cluster_session_credentials.assert_called_with(
            ClusterId=dummy_cluster_id,
            ExecutionRoleArn=dummy_execution_role_arn,
        )

    def test_error_propagation_from_token_api_call(self):
        mock_emr_client = MagicMock()
        mock_emr_client.get_cluster_session_credentials.side_effect = OSError(
            "Runtime error"
        )
        under_test = ClusterSessionCredentialsProvider()

        dummy_execution_role_arn = "role_arn"
        dummy_cluster_id = "cluster_id"

        with self.assertRaises(OSError):
            actual_credentials = under_test.get_cluster_session_credentials(
                emr_client=mock_emr_client,
                cluster_id=dummy_cluster_id,
                emr_execution_role_arn=dummy_execution_role_arn,
            )
