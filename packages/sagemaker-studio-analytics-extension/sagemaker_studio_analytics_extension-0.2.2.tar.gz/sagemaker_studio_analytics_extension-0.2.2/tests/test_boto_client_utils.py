import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from sagemaker_studio_analytics_extension.utils.boto_client_utils import (
    get_boto3_session,
    CUSTOM_MODEL_DIRECTORY,
)


ASSUME_ROLE_RESPONSE = {
    "Credentials": {
        "AccessKeyId": "id",
        "SecretAccessKey": "key",
        "SessionToken": "token",
        "Expiration": "2021-11-15T21:52:45Z",
    },
    "PackedPolicySize": 15,
}


class TestBotoSessionCreation(unittest.TestCase):
    def test_get_boto3_session_without_role_arn(self):
        assert get_boto3_session(role_arn=None)

    @patch("sagemaker_studio_analytics_extension.utils.client_factory.boto3")
    @patch("sagemaker_studio_analytics_extension.utils.boto_client_utils.boto3")
    def test_get_boto3_session_with_role_arn(
        self, mock_boto_client_utils_boto, mock_client_factory_boto
    ):
        expected_mock_session = MagicMock()
        mock_boto_client_utils_boto.Session.return_value = expected_mock_session

        mock_sts_client = MagicMock()
        mock_sts_client.assume_role.return_value = ASSUME_ROLE_RESPONSE
        mock_client_factory_boto.client.return_value = mock_sts_client

        dummy_role_arn = "role_arn"
        actual_session = get_boto3_session(role_arn=dummy_role_arn)
        # check assume role call
        mock_sts_client.assume_role.assert_called_with(
            RoleArn=dummy_role_arn, RoleSessionName="SageMakerStudioUser"
        )

        # check session
        assert actual_session == expected_mock_session
        mock_boto_client_utils_boto.Session.assert_called_with(
            aws_access_key_id="id",
            aws_secret_access_key="key",
            aws_session_token="token",
        )

    @patch("os.path")
    @patch("boto3.session")
    def test_get_boto3_session_with_custom_model_directory(
        self, mock_boto3_session, mock_os_path
    ):
        expected_mock_session = MagicMock()
        mock_boto3_session.Session.return_value = expected_mock_session

        mock_loader = MagicMock()
        expected_mock_session.configure_mock(_loader=mock_loader)

        mock_search_paths = ["/some/path"]
        mock_loader.configure_mock(search_paths=mock_search_paths)

        mock_os_path.exists.return_value = True

        actual_session = get_boto3_session()

        assert actual_session == expected_mock_session
        assert CUSTOM_MODEL_DIRECTORY in mock_search_paths
        mock_os_path.exists.assert_called_with(CUSTOM_MODEL_DIRECTORY)

    @patch("os.path")
    @patch("boto3.session")
    def test_get_boto3_session_without_custom_model_directory(
        self, mock_boto3_session, mock_os_path
    ):
        expected_mock_session = MagicMock()
        mock_boto3_session.Session.return_value = expected_mock_session

        mock_loader = MagicMock()
        expected_mock_session.configure_mock(_loader=mock_loader)

        mock_search_paths = ["/some/path"]
        mock_loader.configure_mock(search_paths=mock_search_paths)

        mock_os_path.exists.return_value = False

        actual_session = get_boto3_session()

        assert actual_session == expected_mock_session
        assert CUSTOM_MODEL_DIRECTORY not in mock_search_paths
        mock_os_path.exists.assert_called_with(CUSTOM_MODEL_DIRECTORY)
