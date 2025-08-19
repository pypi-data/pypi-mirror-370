"""
Intercepts SparkMagic output to replace Spark UI URLs with refresh endpoints
"""

import json
import os
from IPython.core.display import HTML
from IPython.display import display
from .spark_ui_url_replacer import SparkUIURLReplacer


class SparkMagicOutputInterceptor:
    """
    Intercepts and modifies SparkMagic output to replace Spark UI URLs
    """

    @staticmethod
    def setup_output_interception():
        """
        Set up output interception for SparkMagic commands
        """

        try:
            from IPython import get_ipython

            ipy = get_ipython()

            if ipy is None:
                return

            # Hook into print function since SparkMagic uses print for output
            import builtins

            original_print = builtins.print

            def intercepted_print(*args, **kwargs):
                # Check if any argument contains URLs without modifying them
                has_url = any(
                    "dashboard.emr-serverless" in str(arg)
                    or "spark-ui.emr-serverless" in str(arg)
                    for arg in args
                )

                if has_url:
                    # Only modify arguments that contain URLs
                    application_id = os.environ.get("EMR_SERVERLESS_APPLICATION_ID")
                    if application_id:
                        modified_args = []
                        for arg in args:
                            arg_str = str(arg)
                            if (
                                "dashboard.emr-serverless" in arg_str
                                or "spark-ui.emr-serverless" in arg_str
                            ):
                                modified_args.append(
                                    SparkUIURLReplacer.replace_spark_ui_urls(
                                        arg_str, application_id
                                    )
                                )
                            else:
                                modified_args.append(arg)
                        return original_print(*modified_args, **kwargs)

                return original_print(*args, **kwargs)

            # Replace the print function
            builtins.print = intercepted_print

            # Also intercept IPython display function
            from IPython.display import display as original_display

            def intercepted_display(*args, **kwargs):
                for i, arg in enumerate(args):
                    if hasattr(arg, "data") and hasattr(arg.data, "get"):
                        html_data = arg.data.get("text/html", "")
                        if html_data and (
                            "dashboard.emr-serverless" in html_data
                            or "spark-ui.emr-serverless" in html_data
                        ):
                            application_id = os.environ.get(
                                "EMR_SERVERLESS_APPLICATION_ID"
                            )
                            if application_id:
                                modified_html = (
                                    SparkUIURLReplacer.replace_spark_ui_urls(
                                        html_data, application_id
                                    )
                                )
                                arg.data["text/html"] = modified_html
                return original_display(*args, **kwargs)

            # Replace display function in IPython.display module
            import IPython.display

            IPython.display.display = intercepted_display

        except Exception as e:
            print(
                json.dumps(
                    {
                        "application_id": os.environ.get(
                            "EMR_SERVERLESS_APPLICATION_ID"
                        ),
                        "error_message": e,
                        "success": False,
                        "service": "emr-serverless",
                        "operation": "spark-url-refresh",
                    }
                )
            )
