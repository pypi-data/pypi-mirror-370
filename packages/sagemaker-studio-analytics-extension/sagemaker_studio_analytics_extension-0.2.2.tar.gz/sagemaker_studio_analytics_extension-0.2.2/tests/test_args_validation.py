import unittest
from unittest.mock import patch, MagicMock

from IPython.core.error import UsageError

from .resource_patch import *
from sagemaker_studio_analytics_extension.magics import (
    SagemakerAnalytics,
)

from sagemaker_studio_analytics_extension.utils.exceptions import (
    MissingParametersError,
    InvalidParameterError,
)
from sagemaker_studio_analytics_extension.utils.arg_validators.emr_validator import (
    EMRValidator,
)

from sagemaker_studio_analytics_extension.utils.constants import SM_ANALYTICS_USAGE

from sagemaker_studio_analytics_extension.utils.arg_validators.emr_serverless_validator import (
    EMRServerlessValidator,
)


class DummyMissingAuthTypeArgs:
    auth_type = None
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"
    assumable_role_arn = None


class DummyMissingClusterId:
    auth_type = "Basic_Access"
    cluster_id = None
    language = "python"
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyInvalidAuthType:
    auth_type = "Something"
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyValidPySpark:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyMissingLanguageIPython:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    language = None
    assumable_role_arn = None
    emr_execution_role_arn = None


class DummyEMRSMissingLanguageIPython:
    application_id = "j-3DD9ZR01DAU14"
    language = None
    emr_execution_role_arn = "arn:aws:iam::123456789:role/EMRSJobExecutionRole"
    assumable_role_arn = None


class DummyEMRSInvalidLanguageIPython:
    application_id = "j-3DD9ZR01DAU14"
    language = "java"
    emr_execution_role_arn = "arn:aws:iam::123456789:role/EMRSJobExecutionRole"
    assumable_role_arn = None


class DummyAssumableRoleArnValidation:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"

    def __init__(self, assumable_role_arn):
        self.assumable_role_arn = assumable_role_arn


class DummyEmrExecutionRoleArnValidation:
    auth_type = "Basic_Access"
    cluster_id = "j-3DD9ZR01DAU14"
    language = "python"
    assumable_role_arn = None

    def __init__(self, emr_execution_role_arn):
        self.emr_execution_role_arn = emr_execution_role_arn


class TestArgsValidation(unittest.TestCase):
    @patch("IPython.Application.instance")
    def test_invalid_service(self, mock_kernel):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                "something connect --cluster-id j-3KMA44GZ4KWEJ --auth-type None"
            )
        self.assertEqual(
            str(e.exception),
            f"Service 'something' not found. {SM_ANALYTICS_USAGE}",
        )

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.ServiceFileLogger"
    )
    @patch("IPython.Application.instance")
    def test_invalid_operation(self, mock_kernel, mock_logger):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                "emr disconnect --cluster-id j-3KMA44GZ4KWEJ --auth-type None"
            )
        self.assertEqual(
            str(e.exception),
            f"Operation 'disconnect' not found. {SM_ANALYTICS_USAGE}",
        )

    def test_missing_cluster_id(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr disconnect --cluster-id --auth-type None")
        self.assertEqual(
            str(e.exception),
            "argument --cluster-id: expected one argument",
        )

    @patch("IPython.Application.instance")
    def test_missing_application_id_argument(self, mock_kernel):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                "emr-serverless connect --emr-execution-role-arn "
                "arn:aws:iam::accid:role/roleId"
            )
            self.assertIsInstance(e, MissingParametersError)
        self.assertRegex(
            str(e.exception),
            "Missing required argument '--application-id'.*",
        )

    def test_missing_application_id(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                "emr-serverless connect --application-id --emr-execution-role-arn "
                "arn:aws:iam::accid:role/roleId"
            )
        self.assertEqual(
            str(e.exception),
            "argument --application-id: expected one argument",
        )

    @patch("IPython.Application.instance")
    def test_missing_emr_execution_role_arn_argument(self, mock_kernel):
        sm = SagemakerAnalytics()
        with self.assertRaises(MissingParametersError) as e:
            sm.sm_analytics("emr-serverless connect --application-id testApplicationId")
        self.assertRegex(
            str(e.exception),
            "Missing required argument '--emr-execution-role-arn'.*",
        )

    @patch("IPython.Application.instance")
    def test_invalid_argument_emr_serverless(self, mock_kernel):
        sm = SagemakerAnalytics()
        with self.assertRaises(InvalidParameterError) as e:
            sm.sm_analytics(
                "emr-serverless connect --application-id testApplicationId --emr-execution-role-arn "
                "arn:aws:iam::1234567:role/Admin --cluster-id someClusterId"
            )
        self.assertEqual(
            str(e.exception),
            "--cluster-id, --auth-type, --secret and --verify-certificate are not supported when connecting to EMR "
            "Serverless Applications",
        )

    def test_ipython_kernel_emr_serverless_language_missing(self):
        with self.assertRaises(MissingParametersError) as e:
            EMRServerlessValidator.validate_args_for_emr_serverless(
                DummyEMRSMissingLanguageIPython(), "testUsage", "IPythonKernel"
            )
        self.assertEqual(
            str(e.exception),
            "Missing required argument '--language' for IPython kernel. testUsage",
        )

    def test_ipython_kernel_emr_serverless_invalid_language(self):
        with self.assertRaises(InvalidParameterError) as e:
            EMRServerlessValidator.validate_args_for_emr_serverless(
                DummyEMRSInvalidLanguageIPython(), "testUsage", "IPythonKernel"
            )
        self.assertRegex(
            str(e.exception),
            "Invalid language, supported languages are *",
        )

    def test_missing_auth(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr disconnect --cluster-id j-3KMA44GZ4KWEJ --auth-type")
        self.assertEqual(
            str(e.exception),
            "argument --auth-type: expected one argument",
        )

    def test_unsupported_auth(self):
        with self.assertRaises(Exception) as e:
            EMRValidator.validate_emr_args(
                DummyInvalidAuthType(), "something", "IPython"
            )
        self.assertTrue(
            str(e.exception).__contains__("Invalid auth type, supported auth types are")
        )

    def test_empty_command(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("")
        self.assertEqual(
            str(e.exception),
            f"Please provide service name and operation to perform. {SM_ANALYTICS_USAGE}",
        )

    def test_blank_command(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(" ")
        self.assertEqual(
            str(e.exception),
            f"Please provide service name and operation to perform. {SM_ANALYTICS_USAGE}",
        )

    def test_more_than_needed(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr connect connect")
        self.assertEqual(
            str(e.exception),
            f"Please provide service name and operation to perform. {SM_ANALYTICS_USAGE}",
        )

    def test_unrecognized_argument_cluster_id_usage_error(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(UsageError) as e:
            sm.sm_analytics("emr connect --clusterid")
        self.assertEqual(
            str(e.exception),
            "unrecognized arguments: --clusterid",
        )

    def test_unrecognized_argument_auth_type_usage_error(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(UsageError) as e:
            sm.sm_analytics("emr connect --cluster-id xyz --authtype")
        self.assertEqual(
            str(e.exception),
            "unrecognized arguments: --authtype",
        )

    def test_unrecognized_argument_random_usage_error(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(UsageError) as e:
            sm.sm_analytics(
                "emr connect --cluster-id xyz --auth-type None --something_else"
            )
        self.assertEqual(
            str(e.exception),
            "unrecognized arguments: --something_else",
        )

    def test_invalid_language_none(self):
        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics("emr connect --cluster-id xyz --auth-type None --language")
        self.assertEqual(
            str(e.exception),
            "argument --language: expected one argument",
        )

    def test_language_not_required_for_pyspark_kernel(self):
        EMRValidator.validate_emr_args(DummyValidPySpark(), "something", "PySpark")

    def test_language_required_for_ipython_kernel(self):
        with self.assertRaises(MissingParametersError) as e:
            EMRValidator.validate_emr_args(
                DummyMissingLanguageIPython(),
                usage="something",
                kernel_name="IPythonKernel",
            )
        self.assertEqual(
            "Missing required argument '--language' for IPython kernel. something",
            str(e.exception),
        )

    def test_missing_cluster_id_argument(self):
        with self.assertRaises(MissingParametersError) as e:
            EMRValidator.validate_emr_args(
                DummyMissingClusterId(), usage="something", kernel_name="IPython"
            )
        self.assertEqual(
            "Missing required argument '--cluster-id'. something",
            str(e.exception),
        )

    def test_missing_auth_type(self):
        with self.assertRaises(MissingParametersError) as e:
            EMRValidator.validate_emr_args(
                DummyMissingAuthTypeArgs(), usage="something", kernel_name="IPython"
            )
        self.assertEqual(
            "Missing required argument '--auth-type'. something",
            str(e.exception),
        )

    _incorrect_iam_role_arn_list = [
        (
            "foobar",
            "ARNs must be of the form arn:partition:service:region:accountId:resource",
        ),
        ("x:aws:iam::accid:role/roleId", "ARNs must start with `arn`"),
        ("arn::iam::accid:role/roleId", "Partition must be non-empty."),
        ("arn:aws:::accid:role/roleId", "Service must be non-empty."),
        ("arn:aws:iam::accid:", "Resource must be non-empty."),
        (
            "arn:aws:abc::accid:role/roleId",
            "Incorrect Role ARN. Provided service abc does not match expected service `iam`",
        ),
        (
            "arn:aws:iam::accid:foo/roleId",
            "Incorrect Role ARN. Provided resource foo/roleId does not correspond to expected resource `role`",
        ),
        (
            "arn:pqr:iam::accid:role/roleId",
            "Invalid partition: pqr",
        ),
        (
            "arn:aws:iam::accid:" + "x" * 2048,
            "ARN size must not exceed 2048 character limit.",
        ),
    ]

    def test_incorrect_assumable_arn(self):
        for command, expected_exception_string in self._incorrect_iam_role_arn_list:
            with self.subTest():
                with self.assertRaises(Exception) as e:
                    EMRValidator.validate_emr_args(
                        DummyAssumableRoleArnValidation(command),
                        usage="something",
                        kernel_name="IPython",
                    )
                self.assertEqual(expected_exception_string, str(e.exception))

    def test_incorrect_emr_execution_arn(self):
        for command, expected_exception_string in self._incorrect_iam_role_arn_list:
            with self.subTest():
                with self.assertRaises(Exception) as e:
                    EMRValidator.validate_emr_args(
                        DummyEmrExecutionRoleArnValidation(command),
                        usage="something",
                        kernel_name="IPython",
                    )
                self.assertEqual(expected_exception_string, str(e.exception))
