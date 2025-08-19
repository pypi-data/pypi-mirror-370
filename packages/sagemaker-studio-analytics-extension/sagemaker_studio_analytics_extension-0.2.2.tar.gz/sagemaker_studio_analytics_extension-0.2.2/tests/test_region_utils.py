import unittest
import botocore
import botocore.session

from unittest.mock import patch
from parameterized import parameterized

from sagemaker_studio_analytics_extension.utils.region_utils import (
    get_regional_dns_suffix,
    get_regional_service_endpoint_url,
)


class TestRegionUtils(unittest.TestCase):
    @parameterized.expand(
        [
            [
                "us-west-2",
                "amazonaws.com",
            ],
            [
                "cn-north-1",
                "amazonaws.com.cn",
            ],
            [
                "us-gov-west-1",
                "amazonaws.com",
            ],
            [
                "us-isof-east-1",
                "csp.hci.ic.gov",
            ],
        ]
    )
    def test_get_regional_dns_suffix(self, region, dns_suffix):
        botocore_session = botocore.session.Session()
        assert get_regional_dns_suffix(botocore_session, region) == dns_suffix

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
    def test_get_regional_service_endpoint_url(self, region, endpoint_url):
        botocore_session = botocore.session.Session()
        assert (
            get_regional_service_endpoint_url(botocore_session, "sts", region)
            == endpoint_url
        )

        with patch(
            "botocore.regions.EndpointResolver.construct_endpoint"
        ) as mock_construct_endpoint:
            mock_construct_endpoint.return_value = None
            assert (
                get_regional_service_endpoint_url(botocore_session, "sts", region)
                == endpoint_url
            )
