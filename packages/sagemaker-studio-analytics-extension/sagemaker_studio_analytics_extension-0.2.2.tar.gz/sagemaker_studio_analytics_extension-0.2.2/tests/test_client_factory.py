import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from parameterized import parameterized


from sagemaker_studio_analytics_extension.utils.client_factory import ClientFactory


class TestClientFactory(unittest.TestCase):
    @parameterized.expand(
        [
            [
                "us-west-2",
                "https://sts.us-west-2.amazonaws.com",
            ],
            [
                "cn-north-1",
                "https://sts.cn-north-1.amazonaws.com.cn",
            ],
            [
                "us-gov-west-1",
                "https://sts.us-gov-west-1.amazonaws.com",
            ],
            [
                "us-isof-east-1",
                "https://sts.us-isof-east-1.csp.hci.ic.gov",
            ],
        ]
    )
    @patch(
        "sagemaker_studio_analytics_extension.utils.client_factory.get_regional_service_endpoint_url"
    )
    @patch(
        "sagemaker_studio_analytics_extension.utils.client_factory.boto3.session.Session"
    )
    @patch("sagemaker_studio_analytics_extension.utils.client_factory.boto3.client")
    def test_get_regional_sts_client_default(
        self,
        region_name,
        sts_endpoint,
        mock_boto_client,
        mock_boto_session,
        mock_get_endpoint_url,
    ):
        mock_get_endpoint_url.return_value = sts_endpoint
        mock_boto_session.return_value = MagicMock(**{"region_name": region_name})
        mock_boto_client.return_value = MagicMock()
        _ = ClientFactory.get_regional_sts_client()
        mock_boto_client.assert_called_with(
            "sts",
            endpoint_url=sts_endpoint,
            region_name=region_name,
        )

    @patch("sagemaker_studio_analytics_extension.utils.client_factory.boto3.client")
    @patch(
        "sagemaker_studio_analytics_extension.utils.client_factory.RegionalClient.get_sts_client"
    )
    def test_get_global_sts_client(
        self, mock_regionalclient_getstsclient, mock_boto_client
    ):
        mock_regionalclient_getstsclient.side_effect = RuntimeError(
            "RuntimeError on initiating regional call"
        )
        mock_boto_client.return_value = MagicMock()
        _ = ClientFactory.get_regional_sts_client()
        mock_boto_client.assert_called_with("sts")
