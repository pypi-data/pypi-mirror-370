import unittest
from unittest.mock import MagicMock

from parameterized import parameterized

from sagemaker_studio_analytics_extension.resource.emr.emr_client import (
    get_emr_endpoint_url,
)


class TestBotoSessionCreation(unittest.TestCase):
    @parameterized.expand(
        [
            [
                "PDXEmrVpcEndpoint",
                "us-west-2",
                "https://elasticmapreduce.us-west-2.amazonaws.com",
            ],
            [
                "BJSEmrVpcEndpoint",
                "cn-north-1",
                "https://elasticmapreduce.cn-north-1.amazonaws.com.cn",
            ],
            [
                "PDTEmrVpcEndpoint",
                "us-gov-west-1",
                "https://elasticmapreduce.us-gov-west-1.amazonaws.com",
            ],
        ]
    )
    def test_sequence(self, param_name, region_name, emr_endpoint_url):
        mock_boto_session = MagicMock()
        mock_boto_session.configure_mock(region_name=region_name)
        self.assertEqual(get_emr_endpoint_url(mock_boto_session), emr_endpoint_url)
