"""
Utility to replace EMR Serverless Spark UI URLs with server-side refresh endpoints
"""

import re
import os
import logging


logger = logging.getLogger(__name__)


class SparkUIURLReplacer:
    """
    Replaces EMR Serverless Spark UI URLs with server-side refresh endpoints
    that call getDashboardForJobRun API on-demand when clicked
    """

    @staticmethod
    def _create_replacement_function(application_id, job_id_index):
        """Create replacement function for URL patterns"""

        def replace_url(match):
            job_id = match.group(job_id_index)

            if os.environ.get("SPARK_UI_LINK_OVERRIDE", "").lower() == "true":
                endpoint_url = (
                    f"/aws/sagemaker/redirect/emr-serverless/refresh-spark-ui/{job_id}"
                )
                if application_id:
                    endpoint_url += f"?applicationId={application_id}"
                logger.debug(f"Replacing Spark UI Link with endpoint: {endpoint_url}")
                return f'href="{endpoint_url}" target="_blank"'

            logger.debug("Spark UI Link replacement disabled, keeping original URL")
            return match.group(0)

        return replace_url

    @staticmethod
    def replace_spark_ui_urls(html_content, application_id):
        """
        Replace EMR Serverless Spark UI URLs in HTML content with server-side refresh endpoints

        Args:
            html_content (str): HTML content containing Spark UI links
            application_id (str): EMR Serverless application ID

        Returns:
            str: Modified HTML content with server endpoints
        """
        if html_content is None:
            return None

        logger.debug(
            f"Processing HTML content for URL replacement, application_id: {application_id}"
        )

        # Pattern for spark-ui URLs
        spark_ui_pattern = r'href="https://spark-ui\.emr-serverless\.([^/]+)\.amazonaws\.com/applications/([^/]+)/jobs/([^/">\s]+)"'

        # Pattern for dashboard URLs (j-xxxxx format)
        dashboard_pattern = r'href="https://j-([a-z0-9]+)\.dashboard\.emr-serverless\.[^/]+\.amazonaws\.com/[^"]*"'

        # Create replacement functions
        spark_ui_replacer = SparkUIURLReplacer._create_replacement_function(
            application_id, 3
        )
        dashboard_replacer = SparkUIURLReplacer._create_replacement_function(
            application_id, 1
        )

        # Replace URLs
        modified_content = re.sub(spark_ui_pattern, spark_ui_replacer, html_content)
        modified_content = re.sub(
            dashboard_pattern, dashboard_replacer, modified_content
        )

        return modified_content
