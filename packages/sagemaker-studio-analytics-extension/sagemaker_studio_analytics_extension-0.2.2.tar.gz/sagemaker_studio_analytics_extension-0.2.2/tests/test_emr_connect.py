import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest import mock
import base64


from sagemaker_studio_analytics_extension.magics.sagemaker_analytics import (
    _initiate_emr_connect,
)

from sagemaker_studio_analytics_extension.magics.sagemaker_analytics import (
    _get_secret,
)

from sagemaker_studio_analytics_extension.utils.emr_constants import (
    AUTH_TYPE_BASIC_ACCESS,
)

from sagemaker_studio_analytics_extension.utils.constants import (
    USE_DUALSTACK_ENDPOINT,
)


class TestEMRConnect(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.BotocoreConfig"
    )
    @patch(
        "sagemaker_studio_analytics_extension.resource.emr.auth.ClusterSessionCredentialsProvider.get_cluster_session_credentials"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._initiate_connect_based_on_kernel"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._validate_cluster_auth_with_auth_type_provided"
    )
    @patch("sagemaker_studio_analytics_extension.magics.sagemaker_analytics.EMRCluster")
    def test_connect_emr_with_runtime_role(
        self,
        patched_emr_cluster,
        patched_validate_cluster_auth_with_auth_type_provided,
        patched_initiate_connect_based_on_kernel,
        patched_get_cluster_session_credentials,
        patched_botocore_config,
    ):
        mock_context = MagicMock()
        mock_args = MagicMock()
        mock_boto_session = MagicMock()
        mock_boto_session.configure_mock(region_name="us-west-2")
        kernel_name = "kernel_name"
        mock_args.auth_type = AUTH_TYPE_BASIC_ACCESS

        # mock emr client
        mock_emr_client = MagicMock()
        mock_boto_session.client.return_value = mock_emr_client

        # mock emr boto config
        mock_emr_boto_config_user_agent_extra = "sagemaker-analytics"
        mock_emr_iam_pass_service = "emr"
        mock_emr_boto_config = MagicMock()
        patched_botocore_config.return_value = mock_emr_boto_config

        # mock EMR cluster
        mock_emr_cluster = MagicMock()
        patched_emr_cluster.return_value = mock_emr_cluster

        # emr credential
        mock_emr_credentials = MagicMock()
        patched_get_cluster_session_credentials.return_value = mock_emr_credentials

        # test
        _initiate_emr_connect(
            mock_context,
            mock_args,
            mock_emr_cluster,
            mock_emr_client,
            mock_boto_session,
            kernel_name,
        )

        # verify
        patched_validate_cluster_auth_with_auth_type_provided.assert_called_with(
            args=mock_args, emr_cluster=mock_emr_cluster
        )
        patched_botocore_config.assert_called_with(
            user_agent_extra=mock_emr_boto_config_user_agent_extra,
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT,
        )
        mock_boto_session.client.assert_called_with(
            mock_emr_iam_pass_service, config=mock_emr_boto_config
        )
        patched_get_cluster_session_credentials.assert_called_with(
            mock_emr_client, mock_args.cluster_id, mock_args.emr_execution_role_arn
        )
        patched_initiate_connect_based_on_kernel.assert_called_with(
            context=mock_context,
            emr_client=mock_emr_client,
            args=mock_args,
            emr_cluster=mock_emr_cluster,
            username=mock_emr_credentials.username,
            password=mock_emr_credentials.password,
            kernel_name=kernel_name,
        )

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._get_secret"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.BotocoreConfig"
    )
    @patch(
        "sagemaker_studio_analytics_extension.resource.emr.auth.ClusterSessionCredentialsProvider.get_cluster_session_credentials"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._initiate_connect_based_on_kernel"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._validate_cluster_auth_with_auth_type_provided"
    )
    @patch("sagemaker_studio_analytics_extension.magics.sagemaker_analytics.EMRCluster")
    def test_connect_emr_with_secret(
        self,
        patched_emr_cluster,
        patched_validate_cluster_auth_with_auth_type_provided,
        patched_initiate_connect_based_on_kernel,
        patched_get_cluster_session_credentials,
        patched_botocore_config,
        patched_get_secret,
    ):
        mock_context = MagicMock()
        mock_args = MagicMock()
        mock_boto_session = MagicMock()
        mock_boto_session.configure_mock(region_name="us-west-2")
        kernel_name = "kernel_name"
        mock_args.auth_type = AUTH_TYPE_BASIC_ACCESS
        mock_args.secret = "secret_id"
        mock_args.emr_execution_role_arn = None
        # mock emr client
        mock_emr_client = MagicMock()
        mock_boto_session.client.return_value = mock_emr_client

        # mock EMR cluster
        mock_emr_cluster = MagicMock()
        patched_emr_cluster.return_value = mock_emr_cluster

        # test
        _initiate_emr_connect(
            mock_context,
            mock_args,
            mock_emr_cluster,
            mock_emr_client,
            mock_boto_session,
            kernel_name,
        )

        # verify
        patched_get_secret.assert_called_with(mock_args.secret)

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.get_boto3_session"
    )
    def test_get_secret_SecretString(self, patched_get_boto3_session):
        patched_session = MagicMock()
        patched_get_boto3_session.return_value = patched_session
        patched_client = MagicMock()
        patched_session.client.return_value = patched_client
        patched_client.get_secret_value.return_value = {
            "SecretString": '{"username":"user1","password":"pwd1"}'
        }
        secret_id = "secret_id"

        # test
        response = _get_secret(secret_id)

        # verify
        self.assertEqual(response["username"], "user1")
        self.assertEqual(response["password"], "pwd1")
        patched_client.get_secret_value.assert_called_with(SecretId=secret_id)

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.get_boto3_session"
    )
    def test_get_secret_SecretBinary(self, patched_get_boto3_session):
        patched_session = MagicMock()
        patched_get_boto3_session.return_value = patched_session
        patched_client = MagicMock()
        patched_session.client.return_value = patched_client
        base_64_secret = base64.b64encode(b'{"username":"user1","password":"pwd1"}')
        patched_client.get_secret_value.return_value = {"SecretBinary": base_64_secret}
        secret_id = "secret_id"

        # test
        response = _get_secret(secret_id)

        # verify
        self.assertEqual(response["username"], "user1")
        self.assertEqual(response["password"], "pwd1")
        patched_client.get_secret_value.assert_called_with(SecretId=secret_id)
