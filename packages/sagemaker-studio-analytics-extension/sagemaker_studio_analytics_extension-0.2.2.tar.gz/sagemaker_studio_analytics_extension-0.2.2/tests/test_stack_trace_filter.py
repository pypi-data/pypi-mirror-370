import unittest

from sagemaker_studio_analytics_extension.utils.stack_trace_filter import (
    StackTraceFilter,
)


class TestStackTraceFilter(unittest.TestCase):
    def setUp(self):
        self.filter = StackTraceFilter()

    def test_email_filtering(self):
        trace = "Error occurred while sending an email to john.doe@example.com"
        expected = "Error occurred while sending an email to <EMAIL>"
        self.assertEqual(self.filter.filter(trace), expected)

    def test_phone_filtering(self):
        trace_contains_usa_phone_number = "Error while sending SMS to 206-206-2060"
        trace_contains_uk_phone_number = "Error while sending SMS to +44 7911 123456"
        expected = "Error while sending SMS to <PHONE>"
        self.assertEqual(self.filter.filter(trace_contains_usa_phone_number), expected)
        self.assertEqual(self.filter.filter(trace_contains_uk_phone_number), expected)

    def test_password_filtering(self):
        trace_contains_equal_symbol = "Connection error with password=supersecret"
        trace_contains_colon_symbol = "Connection error with password: supersecret"
        expected = "Connection error with <SECRET>"
        self.assertEqual(self.filter.filter(trace_contains_equal_symbol), expected)
        self.assertEqual(self.filter.filter(trace_contains_colon_symbol), expected)

    def test_apikey_filtering(self):
        trace_contains_equal_symbol = "API failure with apikey=abcdef123456"
        trace_contains_colon_symbol = "API failure with apikey:abcdef123456"
        expected = "API failure with <SECRET>"
        self.assertEqual(self.filter.filter(trace_contains_equal_symbol), expected)
        self.assertEqual(self.filter.filter(trace_contains_colon_symbol), expected)

    def test_aws_secret_filtering(self):
        trace_contains_equal_symbol = (
            "AWS connection failed with aws_secret_access_key=y7g7v5b6"
        )
        trace_contains_colon_symbol = (
            "AWS connection failed with aws_secret_access_key:  y7g7v5b6"
        )
        expected = "AWS connection failed with <AWS_SECRET>"
        self.assertEqual(self.filter.filter(trace_contains_equal_symbol), expected)
        self.assertEqual(self.filter.filter(trace_contains_colon_symbol), expected)
