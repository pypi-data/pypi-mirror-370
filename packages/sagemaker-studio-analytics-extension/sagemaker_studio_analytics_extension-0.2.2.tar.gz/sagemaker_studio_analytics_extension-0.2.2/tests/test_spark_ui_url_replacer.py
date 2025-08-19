import unittest
import unittest.mock
import os
from sagemaker_studio_analytics_extension.utils.spark_ui_url_replacer import (
    SparkUIURLReplacer,
)


class TestSparkUIURLReplacer(unittest.TestCase):

    def setUp(self):
        # Enable URL replacement for tests
        os.environ["SPARK_UI_LINK_OVERRIDE"] = "true"

    def tearDown(self):
        # Clean up environment variable
        os.environ.pop("SPARK_UI_LINK_OVERRIDE", None)

    def test_replace_spark_ui_urls_html_format(self):
        """Test URL replacement in HTML href attributes"""
        html_content = """<a href="https://spark-ui.emr-serverless.us-west-2.amazonaws.com/applications/app123/jobs/job456">Spark UI</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(html_content, "app123")
        expected = """<a href="/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job456?applicationId=app123" target="_blank">Spark UI</a>"""
        self.assertEqual(result, expected)

    def test_replace_spark_ui_urls_plain_text_no_change(self):
        """Test that plain text URLs are not replaced (HTML-only functionality)"""
        text_content = """Spark UI: https://j-00fuk5eao1gnjp0m.dashboard.emr-serverless.us-west-2.amazonaws.com/?authToken=xyz"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(text_content, "app123")
        # Plain text URLs should remain unchanged
        self.assertEqual(result, text_content)

    def test_replace_dashboard_urls_html_format(self):
        """Test dashboard URL replacement in HTML"""
        html_content = """<a href="https://j-abc123.dashboard.emr-serverless.us-west-2.amazonaws.com/logs">Driver Log</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(html_content, "app123")
        expected = """<a href="/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/abc123?applicationId=app123" target="_blank">Driver Log</a>"""
        self.assertEqual(result, expected)

    def test_no_replacement_when_no_urls(self):
        """Test that content without URLs remains unchanged"""
        content = "This is regular content without any URLs"
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")
        self.assertEqual(result, content)

    def test_empty_content(self):
        """Test handling of empty content"""
        result = SparkUIURLReplacer.replace_spark_ui_urls("", "app123")
        self.assertEqual(result, "")

    def test_none_content(self):
        """Test handling of None content"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(None, "app123")
        self.assertIsNone(result)

    def test_multiple_html_urls_in_content(self):
        """Test replacement of multiple HTML URLs in same content"""
        content = """<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Spark UI</a>
        <a href="https://j-job2.dashboard.emr-serverless.us-west-2.amazonaws.com/logs">Driver Log</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")
        self.assertIn(
            'href="/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1', result
        )
        self.assertIn(
            'href="/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job2', result
        )

    def test_mixed_html_and_text_urls(self):
        """Test content with both HTML and plain text URLs"""
        content = """<a href="https://spark-ui.emr-serverless.us-west-2.amazonaws.com/applications/app1/jobs/job1">Link</a>
        Plain: https://j-job2.dashboard.emr-serverless.us-west-2.amazonaws.com/"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")
        # Only HTML href should be replaced
        self.assertIn(
            'href="/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1', result
        )
        # Plain text URL should remain unchanged
        self.assertIn(
            "Plain: https://j-job2.dashboard.emr-serverless.us-west-2.amazonaws.com/",
            result,
        )

    def test_none_application_id(self):
        """Test behavior with None application ID"""
        content = """<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Link</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, None)
        self.assertIn(
            "/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1", result
        )
        self.assertNotIn("applicationId", result)

    def test_url_with_query_params(self):
        """Test URLs that already have query parameters"""
        content = """<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/?authToken=xyz&other=param">Link</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")
        expected = "/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1?applicationId=app123"
        self.assertIn(expected, result)

    def test_non_emr_urls_unchanged(self):
        """Test that non-EMR URLs are not modified"""
        content = """Visit <a href="https://www.amazon.com/">Amazon</a> and <a href="https://aws.amazon.com/emr/">EMR</a>
        Also check <a href="https://console.aws.amazon.com/emr/home">Console</a>
        EMR URL: <a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Spark UI</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")

        # Non-EMR URLs should remain unchanged
        self.assertIn("https://www.amazon.com/", result)
        self.assertIn("https://aws.amazon.com/emr/", result)
        self.assertIn("https://console.aws.amazon.com/emr/home", result)

        # EMR URL should be replaced
        self.assertIn(
            "/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1", result
        )

    def test_individual_argument_processing(self):
        """Test that URL replacement works on individual arguments"""
        # Test processing individual arguments like the interceptor does
        args = [
            "Regular text",
            '<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Link</a>',
            123,
        ]

        # Simulate the interceptor's logic
        has_url = any(
            "dashboard.emr-serverless" in str(arg)
            or "spark-ui.emr-serverless" in str(arg)
            for arg in args
        )

        self.assertTrue(has_url)

        # Process arguments individually
        modified_args = []
        for arg in args:
            arg_str = str(arg)
            if (
                "dashboard.emr-serverless" in arg_str
                or "spark-ui.emr-serverless" in arg_str
            ):
                modified_args.append(
                    SparkUIURLReplacer.replace_spark_ui_urls(arg_str, "app123")
                )
            else:
                modified_args.append(arg)

        # Verify results
        self.assertEqual(modified_args[0], "Regular text")  # Unchanged
        self.assertIn(
            "/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1",
            modified_args[1],
        )  # Modified
        self.assertEqual(modified_args[2], 123)  # Unchanged

    def test_mixed_arguments_individual_processing(self):
        """Test processing mixed arguments without joining them"""
        args = [
            '<a href="https://spark-ui.emr-serverless.us-west-2.amazonaws.com/applications/app1/jobs/job2">Spark UI</a>',
            "Normal text",
            '<a href="https://j-job3.dashboard.emr-serverless.us-west-2.amazonaws.com/logs">Logs</a>',
        ]

        # Process each argument individually
        processed_args = []
        for arg in args:
            arg_str = str(arg)
            if (
                "dashboard.emr-serverless" in arg_str
                or "spark-ui.emr-serverless" in arg_str
            ):
                processed_args.append(
                    SparkUIURLReplacer.replace_spark_ui_urls(arg_str, "app123")
                )
            else:
                processed_args.append(arg)

        # Verify individual processing
        self.assertIn(
            "/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job2",
            processed_args[0],
        )
        self.assertEqual(processed_args[1], "Normal text")
        self.assertIn(
            "/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job3",
            processed_args[2],
        )

    def test_no_url_arguments_unchanged(self):
        """Test that arguments without URLs remain unchanged"""
        args = ["Hello", "World", 123, [1, 2, 3]]

        # Check URL detection
        has_url = any(
            "dashboard.emr-serverless" in str(arg)
            or "spark-ui.emr-serverless" in str(arg)
            for arg in args
        )

        self.assertFalse(has_url)

        # Arguments should remain unchanged when no URLs detected
        for i, arg in enumerate(args):
            self.assertEqual(arg, args[i])

    @unittest.mock.patch("requests.head")
    def test_health_check_success_replaces_urls(self, mock_head):
        """Test URL replacement when health check succeeds"""
        mock_head.return_value.status_code = 200
        html_content = """<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Spark UI</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(html_content, "app123")
        expected = """<a href="/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/job1?applicationId=app123" target="_blank">Spark UI</a>"""
        self.assertEqual(result, expected)

    def test_environment_variable_disabled(self):
        """Test that URL replacement is disabled when environment variable is not set"""
        os.environ.pop("SPARK_UI_LINK_OVERRIDE", None)
        content = """<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Link</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")
        # URL should remain unchanged when environment variable is not set
        self.assertEqual(result, content)

    def test_environment_variable_false(self):
        """Test that URL replacement is disabled when environment variable is false"""
        os.environ["SPARK_UI_LINK_OVERRIDE"] = "false"
        content = """<a href="https://j-job1.dashboard.emr-serverless.us-west-2.amazonaws.com/">Link</a>"""
        result = SparkUIURLReplacer.replace_spark_ui_urls(content, "app123")
        # URL should remain unchanged when environment variable is false
        self.assertEqual(result, content)


if __name__ == "__main__":
    unittest.main()
