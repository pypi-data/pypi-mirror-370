import contextlib
import io
import ssl
import unittest
from unittest.mock import patch

from sagemaker_studio_analytics_extension.utils import resource_check

VALID_HOSTNAME = "www.amazon.com"


class TestAlivePortChecking(unittest.TestCase):
    def test_check_alive_host_and_port(self):
        assert resource_check.check_host_and_port(VALID_HOSTNAME, 443)

    def test_check_invalid_host_name(self):
        invalid_host_name = "not_a_valid_host_name.org"
        invalid_port = 12345

        actual_result = io.StringIO()
        with contextlib.redirect_stdout(actual_result):
            assert not resource_check.check_host_and_port(
                invalid_host_name, invalid_port
            )

        # only check the error message controlled by check_host_and_port.
        expected_error_message = (
            "[Error] Failed to check host and port [{}:{}]. Error message:".format(
                invalid_host_name, invalid_port
            )
        )
        assert expected_error_message in actual_result.getvalue()

    def test_check_invalid_port(self):
        invalid_port = 45678

        actual_result = io.StringIO()
        with contextlib.redirect_stdout(actual_result):
            assert not resource_check.check_host_and_port(VALID_HOSTNAME, invalid_port)

        # invalid port does not result any exception and socket API return non 0 instead.
        # Error codes are system-dependent, so just check the general format
        output = actual_result.getvalue()
        assert (
            f"Host: {VALID_HOSTNAME} port: {invalid_port} is not connectible via socket with"
            in output
        )
        assert "returned." in output


class TestSSLChecking(unittest.TestCase):
    def test_ssl_enabled(self):
        assert resource_check.is_ssl_enabled(VALID_HOSTNAME, 443)

    @patch(
        "sagemaker_studio_analytics_extension.utils.resource_check.get_server_certificate"
    )
    def test_none_cert_is_returned(self, mock_get_server_certificate):
        mock_get_server_certificate.return_value = None
        assert not resource_check.is_ssl_enabled("abc", 80)

    @patch(
        "sagemaker_studio_analytics_extension.utils.resource_check.get_server_certificate"
    )
    def test_ssl_error_is_returned_while_getting_cert(
        self, mock_get_server_certificate
    ):
        mock_get_server_certificate.side_effect = ssl.SSLError("SSL error")
        assert not resource_check.is_ssl_enabled("abc", 80)

    @patch(
        "sagemaker_studio_analytics_extension.utils.resource_check.get_server_certificate"
    )
    def test_error_propagation_for_non_ssl_error(self, mock_get_server_certificate):
        mock_get_server_certificate.side_effect = OSError("Runtime non-SSL error")
        with self.assertRaises(OSError):
            resource_check.is_ssl_enabled("abc", 80)

    def test_check_ssl_for_invalid_host(self):
        with self.assertRaises(OSError):
            resource_check.is_ssl_enabled("not_a_valid_host_name.org", 443)
