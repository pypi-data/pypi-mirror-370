import contextlib
import io
import json
import os

import sparkmagic.utils.configuration as conf
from IPython.display import display
from sparkmagic.livyclientlib.exceptions import BadUserDataException
from IPython import get_ipython
from sagemaker_studio_analytics_extension.resource.emr_serverless.emr_s_client import (
    EMRServerlessApplication,
)
from sagemaker_studio_analytics_extension.utils.boto_client_utils import (
    get_boto3_session,
)
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    MAGIC_KERNELS,
    SPARK_SESSION_NAME_PREFIX,
)
from sagemaker_studio_analytics_extension.utils.exceptions import (
    SparkSessionStartFailedFault,
    EMRServerlessError,
    SparkSessionStartFailedError,
)

from sagemaker_studio_analytics_extension.utils.service_metrics import (
    records_service_metrics,
)

from sagemaker_studio_analytics_extension.utils.common_utils import (
    _run_preset_cell_magics,
)

from sagemaker_studio_analytics_extension.utils.sparkmagic_output_interceptor import (
    SparkMagicOutputInterceptor,
)

from IPython.utils.capture import capture_output

EMR_SERVERLESS_APPLICATION_STARTED_STATE = "STARTED"
EMR_SERVERLESS_APPLICATION_STARTING_STATE = "STARTING"

EMR_SERVERLESS_AUTH_TYPE = "Sagemaker_EMR_Serverless_Auth"

DEFAULT_EXECUTION_ROLE_ENV = "EMR_SERVERLESS_EXECUTION_ROLE_ARN"
DEFAULT_ASSUMABLE_ROLE_ENV = "EMR_SERVERLESS_ASSUMABLE_ROLE_ARN"


class EMRServerlessMagicUtils:
    def __init__(self, args, kernel_name, session_name):
        self.kernel_name = kernel_name
        self.application_id = args.application_id
        self.language = args.language
        self.emr_execution_role_arn = args.emr_execution_role_arn
        self.assumable_role_arn = args.assumable_role_arn
        self.session_name = session_name

    @records_service_metrics
    def connect_to_emr_serverless_application(
        self,
        args,
        session_name,
        kernel_name,
        service,
        operation,
        service_logger,
        context,
    ):
        """
        Connect to EMR Serverless application after starting the application
        """
        try:
            self._setup_spark_configuration()
            boto_session = get_boto3_session(self.assumable_role_arn)
            application = EMRServerlessApplication(
                application_id=self.application_id, session=boto_session
            )
            application.start_application()
            has_application_started = application.poll_until_required_application_state(
                required_state=EMR_SERVERLESS_APPLICATION_STARTED_STATE,
                retryable_states=[EMR_SERVERLESS_APPLICATION_STARTING_STATE],
            )
            livy_endpoint = application.get_livy_endpoint()

            if has_application_started:
                print("Initiating EMR Serverless connection..")

                # Set up Spark UI URL interception
                SparkMagicOutputInterceptor.setup_output_interception()

                ipy = get_ipython()
                if self.kernel_name in MAGIC_KERNELS:
                    self._initiate_spark_session_in_magic_kernel(
                        livy_endpoint=livy_endpoint, ipy=ipy
                    )
                else:
                    self._initiate_spark_session_in_ipython_kernel(
                        livy_endpoint=livy_endpoint, ipy=ipy
                    )
        except Exception as e:
            print(json.dumps(self._build_response(error_message=str(e))))
            raise e

    def _setup_spark_configuration(self):
        """
        Setting up spark configuration to allow connecting to EMR Serverless application
        """
        session_configs = conf.session_configs()
        if "conf" not in session_configs:
            session_configs["conf"] = {}
        session_configs["conf"][
            "emr-serverless.session.executionRoleArn"
        ] = self.emr_execution_role_arn
        session_configs["conf"][
            "sagemaker.session.assumableRoleArn"
        ] = self.assumable_role_arn

        # Preserving roles as default roles for other spark operations
        os.environ[DEFAULT_EXECUTION_ROLE_ENV] = self.emr_execution_role_arn
        if self.assumable_role_arn is not None:
            os.environ[DEFAULT_ASSUMABLE_ROLE_ENV] = self.assumable_role_arn

        # Store application ID for Spark UI URL replacement
        os.environ["EMR_SERVERLESS_APPLICATION_ID"] = self.application_id

        conf.override(conf.session_configs.__name__, session_configs)
        conf.override(conf.livy_session_startup_timeout_seconds.__name__, 180)

        authenticators = conf.authenticators()
        authenticators[EMR_SERVERLESS_AUTH_TYPE] = (
            "sagemaker_studio_analytics_extension.external_dependencies.emr_serverless_auth"
            ".EMRServerlessCustomSigV4Signer"
        )
        conf.override(conf.authenticators.__name__, authenticators)

    def _handle_spark_session_failures(self, error_message):
        # This function handles different spark session failures based on error_message details
        if (
            "Invalid status code '403'" in error_message
            and "not authorized" in error_message
        ):
            raise SparkSessionStartFailedError(error_message)
        elif (
            "Invalid status code '400'" in error_message
            and "doesn't exist or isn't setup with the required trust relationship"
            in error_message
        ):
            raise SparkSessionStartFailedError(error_message)
        else:
            raise SparkSessionStartFailedFault(error_message)

    def _print_spark_session_info(self, outputs):
        # Import here to avoid circular imports
        from sagemaker_studio_analytics_extension.utils.spark_ui_url_replacer import (
            SparkUIURLReplacer,
        )

        def process_rich_output(output):
            """Process RichOutput object to replace dashboard URLs"""
            if hasattr(output, "data") and hasattr(output.data, "get"):
                html_data = output.data.get("text/html", "")
                if html_data and (
                    "dashboard.emr-serverless" in html_data
                    or "spark-ui.emr-serverless" in html_data
                ):
                    application_id = os.environ.get("EMR_SERVERLESS_APPLICATION_ID")
                    if application_id:
                        modified_html = SparkUIURLReplacer.replace_spark_ui_urls(
                            html_data, application_id
                        )
                        output.data["text/html"] = modified_html
            return output

        if isinstance(outputs, list) and len(outputs) > 0:
            processed_output = process_rich_output(outputs[0])
            display(processed_output)
        else:
            processed_output = process_rich_output(outputs)
            display(processed_output)

    def _initiate_spark_session_in_ipython_kernel(self, livy_endpoint, ipy):
        # Depth should be 2 if run_line_magic is being called from within a magic
        ipy.run_line_magic("load_ext", "sparkmagic.magics", 2)

        endpoint_magic_line = "add -s {0} -l {1} -t {2} -u {3}".format(
            self.session_name, self.language, EMR_SERVERLESS_AUTH_TYPE, livy_endpoint
        )

        # Capture IPython magic command output (both display outputs and stderr)
        err_message, session_info = None, None
        with capture_output() as captured:
            ipy.run_line_magic("spark", endpoint_magic_line)
            if captured.stderr:
                err_message = captured.stderr
            elif captured.outputs:
                session_info = captured.outputs

        # Handles captured output - Either error or session info
        if err_message is not None:
            self._handle_spark_session_failures(err_message)
        else:
            self._print_spark_session_info(session_info)

    def _initiate_spark_session_in_magic_kernel(self, livy_endpoint, ipy):
        _run_preset_cell_magics(ipy)
        endpoint_magic_line = "-s {0} -t {1}".format(
            livy_endpoint, EMR_SERVERLESS_AUTH_TYPE
        )
        try:
            change_endpoint_magic = ipy.find_line_magic("_do_not_call_change_endpoint")
            change_endpoint_magic(endpoint_magic_line)
        except BadUserDataException as e:
            raise EMRServerlessError(
                "Session already exists, please restart kernel and rerun magic"
            )
        except Exception as e:
            self._handle_spark_session_failures(str(e))

        # Capture output from _do_not_call_start_session(both display outputs and stderr)
        session_info = None
        with capture_output() as captured:
            start_session_magic = ipy.find_cell_magic("_do_not_call_start_session")
            session_started = start_session_magic("")
            # Handles captured output - Either error or session info
            if not session_started:
                err_message = captured.stderr or ""
                self._handle_spark_session_failures(err_message)
            else:
                session_info = captured.outputs or [
                    "Spark Session Started Successfully"
                ]

        self._print_spark_session_info(session_info)

    def _build_response(self, error_message):
        return {
            "application_id": self.application_id,
            "error_message": error_message,
            "success": False,
            "service": "emr-serverless",
            "operation": "connect",
        }
