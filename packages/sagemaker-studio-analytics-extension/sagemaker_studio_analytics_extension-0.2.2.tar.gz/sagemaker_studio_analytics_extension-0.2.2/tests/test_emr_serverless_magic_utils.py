import unittest
from unittest.mock import patch, MagicMock, call
import pytest
import sparkmagic.utils.configuration as conf

from sparkmagic.livyclientlib.exceptions import BadUserDataException
from sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils import (
    EMRServerlessMagicUtils,
)

from sagemaker_studio_analytics_extension.utils.exceptions import (
    SparkSessionStartFailedFault,
    SparkSessionStartFailedError,
    EMRServerlessError,
)


@pytest.fixture(scope="session", autouse=True)
def set_config():
    conf.override(conf.authenticators.__name__, {})
    conf.override(conf.session_configs.__name__, {})


class TestEMRServerlessMagicUtils(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.utils.boto_client_utils.get_boto3_session"
    )
    def test_setup_spark_configuration(self, boto_session):
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = None
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"
        mock_args.assumable_role_arn = None
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )
        emr_serverless_magic_utils._setup_spark_configuration()
        self.assertEqual(
            conf.session_configs()["conf"],
            {
                "emr-serverless.session.executionRoleArn": "test_emr_execution_role_arn",
                "sagemaker.session.assumableRoleArn": None,
            },
        )
        self.assertEqual(
            conf.authenticators(),
            {
                "Sagemaker_EMR_Serverless_Auth": "sagemaker_studio_analytics_extension.external_dependencies"
                ".emr_serverless_auth.EMRServerlessCustomSigV4Signer"
            },
        )

    @patch("IPython.utils.capture.capture_output")
    def test_initiate_spark_session_in_ipython_kernel(self, mock_capture):
        """Test successful spark session initialization in IPython kernel"""
        # Setup
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = "python"
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"

        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        mock_ipy = MagicMock()
        # Create mock captured output
        mock_captured = MagicMock()
        mock_captured.stderr = None
        mock_captured.outputs = ["Session successfully created"]

        # Mock the _print_spark_session_info method
        emr_serverless_magic_utils._print_spark_session_info = MagicMock()

        # Mock the capture_output context manager
        with patch(
            "sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils.capture_output"
        ) as mock_capture:
            mock_capture.return_value.__enter__.return_value = mock_captured

            # Call the method
            emr_serverless_magic_utils._initiate_spark_session_in_ipython_kernel(
                livy_endpoint="test_livy_endpoint", ipy=mock_ipy
            )

            # Verify the calls
            calls = [
                call("load_ext", "sparkmagic.magics", 2),
                call(
                    "spark",
                    "add -s test_session_name -l python -t Sagemaker_EMR_Serverless_Auth -u test_livy_endpoint",
                ),
            ]
            mock_ipy.run_line_magic.assert_has_calls(calls)

            # Verify that _print_spark_session_info was called
            emr_serverless_magic_utils._print_spark_session_info.assert_called_once()

    @patch(
        "sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils.EMRServerlessMagicUtils._handle_spark_session_failures"
    )
    def test_initiate_spark_session_in_ipython_kernel_with_failure(
        self, mock_handle_failures
    ):
        # Setup
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = "python"
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"

        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        mock_ipy = MagicMock()

        # Create mock captured output with error
        mock_captured = MagicMock()
        mock_captured.stderr = "Error creating session"
        mock_captured.outputs = None

        # Mock the capture_output context manager
        with patch(
            "sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils.capture_output"
        ) as mock_capture:
            mock_capture.return_value.__enter__.return_value = mock_captured

            # Call the method
            emr_serverless_magic_utils._initiate_spark_session_in_ipython_kernel(
                livy_endpoint="test_livy_endpoint", ipy=mock_ipy
            )

            # Verify that _handle_spark_session_failures was called with the error message
            mock_handle_failures.assert_called_once_with("Error creating session")

    def test_initiate_spark_session_in_magic_kernel(self):
        # Setup
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = None
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"

        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        mock_ipy = MagicMock()

        # Mock the _print_spark_session_info method
        emr_serverless_magic_utils._print_spark_session_info = MagicMock()

        # Create mock captured output
        mock_captured = MagicMock()
        mock_captured.stderr = None
        mock_captured.outputs = ["Session successfully created"]

        # Test successful session creation
        with patch(
            "sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils.capture_output"
        ) as mock_capture:
            mock_capture.return_value.__enter__.return_value = mock_captured

            emr_serverless_magic_utils._initiate_spark_session_in_magic_kernel(
                livy_endpoint="test_livy_endpoint", ipy=mock_ipy
            )

            mock_ipy.find_line_magic.assert_has_calls(
                [
                    call("_do_not_call_change_endpoint"),
                    call()("-s test_livy_endpoint -t Sagemaker_EMR_Serverless_Auth"),
                ]
            )

            mock_ipy.find_cell_magic.assert_has_calls(
                [call("_do_not_call_start_session")]
            )
            # Verify that _print_spark_session_info was called
            emr_serverless_magic_utils._print_spark_session_info.assert_called_once()

    def test_initiate_spark_session_in_magic_kernel_session_start_failure(self):
        # Setup
        mock_args = MagicMock()
        mock_args.application_id = "test_application_id"
        mock_args.language = None
        mock_args.emr_execution_role_arn = "test_emr_execution_role_arn"

        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        mock_ipy = MagicMock()
        mock_change_endpoint_magic = MagicMock()
        mock_start_session_magic = MagicMock()

        mock_ipy.find_line_magic.return_value = mock_change_endpoint_magic
        mock_ipy.find_cell_magic.return_value = mock_start_session_magic
        mock_start_session_magic.return_value = False  # Session failed to start

        # Mock the _handle_spark_session_failures method
        emr_serverless_magic_utils._handle_spark_session_failures = MagicMock()

        # Create mock captured output with error
        mock_captured = MagicMock()
        mock_captured.stderr = "Session start failed"
        mock_captured.outputs = None

        # Test session start failure
        with patch(
            "sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils.capture_output"
        ) as mock_capture:
            mock_capture.return_value.__enter__.return_value = mock_captured

            emr_serverless_magic_utils._initiate_spark_session_in_magic_kernel(
                livy_endpoint="test_livy_endpoint", ipy=mock_ipy
            )

            # Verify calls
            mock_ipy.find_line_magic.assert_has_calls(
                [
                    call("_do_not_call_change_endpoint"),
                    call()("-s test_livy_endpoint -t Sagemaker_EMR_Serverless_Auth"),
                ]
            )

            mock_ipy.find_cell_magic.assert_has_calls(
                [call("_do_not_call_start_session")]
            )

            emr_serverless_magic_utils._handle_spark_session_failures.assert_called_once()

    def test_handle_spark_session_failures(self):
        # Setup
        mock_args = MagicMock()
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        # Test case 1: 403 error message
        error_msg_403 = """An error was encountered:
            Invalid status code '403' from https://endpoint.com with error payload: 
            {"Message":"User is not authorized to perform: iam:PassRole"}"""
        with self.assertRaises(SparkSessionStartFailedError) as context:
            emr_serverless_magic_utils._handle_spark_session_failures(error_msg_403)
        self.assertEqual(str(context.exception), error_msg_403)

        # Test case 2: Other error message
        other_error_msg = "Some other error occurred"
        with self.assertRaises(SparkSessionStartFailedFault) as context:
            emr_serverless_magic_utils._handle_spark_session_failures(other_error_msg)
        self.assertEqual(str(context.exception), other_error_msg)

    @patch(
        "sagemaker_studio_analytics_extension.utils.emr_serverless_magic_utils.display"
    )
    def test_print_spark_session_info(self, mock_display):
        # Setup
        mock_args = MagicMock()
        emr_serverless_magic_utils = EMRServerlessMagicUtils(
            args=mock_args,
            session_name="test_session_name",
            kernel_name="test_kernel_name",
        )

        # Test case 1: Valid list with elements
        outputs = ["Session Info"]
        emr_serverless_magic_utils._print_spark_session_info(outputs)
        mock_display.assert_called_once_with("Session Info")

        # Reset mock
        mock_display.reset_mock()

        # Test case 2: Empty list
        empty_outputs = []
        emr_serverless_magic_utils._print_spark_session_info(empty_outputs)
        mock_display.assert_called_once_with(
            empty_outputs
        )  # Changed: empty list is displayed

        # Reset mock
        mock_display.reset_mock()

        # Test case 3: None input
        none_input = None
        emr_serverless_magic_utils._print_spark_session_info(none_input)
        mock_display.assert_called_once_with(none_input)  # Changed: None is displayed

        # Reset mock
        mock_display.reset_mock()

        # Test case 4: Non-list input
        non_list_output = "Not a list"
        emr_serverless_magic_utils._print_spark_session_info(non_list_output)
        mock_display.assert_called_once_with(
            non_list_output
        )  # Changed: string is displayed
