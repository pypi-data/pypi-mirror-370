import json
import os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from botocore.stub import Stubber

from .resource_patch import *
from sagemaker_studio_analytics_extension.utils.service_metrics import (
    EmrConnectionServiceMetric,
    MetricDimension,
)
from sagemaker_studio_analytics_extension.resource.emr.auth import ClusterAuthUtils
from sagemaker_studio_analytics_extension.magics import (
    SagemakerAnalytics,
)
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    AUTH_TYPE_BASIC_ACCESS,
)
from sagemaker_studio_analytics_extension.utils.magic_execution_context import (
    MagicExecutionContext,
)
from sagemaker_studio_analytics_extension.utils.constants import (
    AUTH_TYPE_RBAC_FOR_LOGGING,
    AUTH_TYPE_KERBEROS_FOR_LOGGING,
    AUTH_TYPE_NO_AUTH_FOR_LOGGING,
    AUTH_TYPE_LDAP_FOR_LOGGING,
    AUTH_TYPE_HTTP_BASIC_FOR_LOGGING,
)

from .test_magic_line_override import (
    get_dummy_public_cluster_describe_cluster_response,
    get_dummy_list_instances_response,
)
from sagemaker_studio_analytics_extension.utils.exceptions import LivyConnectionError

DUMMY_CLUSTER_ID = "cluster_id"


@patch(
    "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.MagicExecutionContext",
    return_value=MagicExecutionContext(connection_protocol="http"),
)
@patch("sagemaker_studio_analytics_extension.magics.sagemaker_analytics.EMRCluster")
@patch("sagemaker_studio_analytics_extension.magics.sagemaker_analytics.get_emr_client")
@patch(
    "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.get_boto3_session"
)
@patch(
    "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._initiate_emr_connect"
)
@patch("sagemaker_studio_analytics_extension.magics.sagemaker_analytics.IPython")
@patch(
    "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.ServiceFileLogger"
)
class TestMetricEmissionEndToEnd(unittest.TestCase):
    def test_metric_with_fault(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        exception_name = "custom_exception"
        mock_emr_connect.side_effect = CustomException(exception_name)

        sm = SagemakerAnalytics()
        with self.assertRaises(Exception) as e:
            sm.sm_analytics(
                f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None"
            )
        self.assertEqual(str(e.exception), exception_name)

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(
            actual_metric_dict,
            _create_emr_metric_dict(
                "MagicMock",
                expected_exception_name="CustomException",
                expected_fault=True,
            ),
        )
        # Assert we do not capture details of any custom exceptions
        assert actual_metric_dict[MetricDimension.ExceptionString.value] is None
        assert actual_metric_dict[MetricDimension.EventTimeStampMillis.value] > 0

    def test_metric_with_error(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        exception_message = "Cannot connect to livy service"
        mock_emr_connect.side_effect = LivyConnectionError(exception_message)

        sm = SagemakerAnalytics()
        with self.assertRaises(LivyConnectionError) as e:
            sm.sm_analytics(
                f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None"
            )
        self.assertEqual(str(e.exception), exception_message)

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        expected_metric_dict = _create_emr_metric_dict(
            expected_kernel_name="MagicMock",
            expected_error=True,
            expected_exception_name="LivyConnectionError",
            expected_exception_message=exception_message,
        )
        _match_dict(actual_metric_dict, expected_metric_dict)
        assert actual_metric_dict[MetricDimension.EventTimeStampMillis.value] > 0

    def test_success_metric(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        sm = SagemakerAnalytics()
        sm.sm_analytics(f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None")

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert actual_metric_dict[MetricDimension.OperationDurationMillis.value] > 0

    def test_ssl_cert_emission_when_input_is_true(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None  --verify-certificate TrUe"
        )

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert actual_metric_dict[MetricDimension.VerifyCertificate.value] == "True"

    def test_ssl_cert_emission_when_input_is_false(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None  --verify-certificate FalSE"
        )

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        print(actual_metric_dict)
        assert actual_metric_dict[MetricDimension.VerifyCertificate.value] == "False"

    def test_ssl_cert_emission_when_input_is_path_to_cert(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None  --verify-certificate Yo"
        )

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.VerifyCertificate.value] == "PathToCert"
        )

    def test_connection_protocol_emission_for_https(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        mock_context.return_value = MagicExecutionContext(connection_protocol="https")

        sm = SagemakerAnalytics()
        sm.sm_analytics(f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None")

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert actual_metric_dict[MetricDimension.ConnectionProtocol.value] == "https"

    def test_connection_protocol_emission_for_http(
        self,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        mock_context.return_value = MagicExecutionContext(connection_protocol="http")

        sm = SagemakerAnalytics()
        sm.sm_analytics(f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type None")

        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert actual_metric_dict[MetricDimension.ConnectionProtocol.value] == "http"

    @patch(
        "sagemaker_studio_analytics_extension.utils.arg_validators.emr_validator.EMRValidator.validate_emr_args"
    )
    def test_metric_auth_type_rbac(
        self,
        mock_validate_emr_args,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        # mock
        mock_emr_execution_role = "mock-execution-role"

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type {AUTH_TYPE_BASIC_ACCESS} --emr"
            f"-execution-role-arn {mock_emr_execution_role}"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_RBAC_FOR_LOGGING
        )

    @patch(
        "sagemaker_studio_analytics_extension.resource.emr.auth.ClusterAuthUtils.is_cluster_ldap"
    )
    @patch(
        "sagemaker_studio_analytics_extension.utils.arg_validators.emr_validator.EMRValidator.validate_emr_args"
    )
    def test_metric_auth_type_ldap(
        self,
        mock_validate_emr_args,
        mock_is_cluster_ldap,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        # ----------------------------
        # is_krb_cluster=True
        # ----------------------------

        # mock
        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=True)
        mock_EMRCluster.return_value = mock_emr_cluster

        mock_is_cluster_ldap.return_value = True

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type {AUTH_TYPE_BASIC_ACCESS}"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_LDAP_FOR_LOGGING
        )

        # ----------------------------
        # is_krb_cluster=False
        # ----------------------------

        # mock
        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=False)
        mock_EMRCluster.return_value = mock_emr_cluster

        mock_is_cluster_ldap.return_value = True

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type {AUTH_TYPE_BASIC_ACCESS}"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_LDAP_FOR_LOGGING
        )

    @patch(
        "sagemaker_studio_analytics_extension.resource.emr.auth.ClusterAuthUtils.is_cluster_ldap"
    )
    @patch(
        "sagemaker_studio_analytics_extension.utils.arg_validators.emr_validator.EMRValidator.validate_emr_args"
    )
    def test_metric_auth_type_http_basic(
        self,
        mock_validate_emr_args,
        mock_is_cluster_ldap,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        # ----------------------------
        # is_krb_cluster=True
        # ----------------------------

        # mock
        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=True)
        mock_EMRCluster.return_value = mock_emr_cluster

        mock_is_cluster_ldap.return_value = False

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type {AUTH_TYPE_BASIC_ACCESS}"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_HTTP_BASIC_FOR_LOGGING
        )

        # ----------------------------
        # is_krb_cluster=False
        # ----------------------------

        # mock
        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=False)
        mock_EMRCluster.return_value = mock_emr_cluster

        mock_is_cluster_ldap.return_value = False

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type {AUTH_TYPE_BASIC_ACCESS}"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_HTTP_BASIC_FOR_LOGGING
        )

    @patch(
        "sagemaker_studio_analytics_extension.utils.arg_validators.emr_validator.EMRValidator.validate_emr_args"
    )
    def test_metric_auth_type_kerberos(
        self,
        mock_validate_emr_args,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        # mock
        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=True)
        mock_EMRCluster.return_value = mock_emr_cluster

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type dummy-value"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_KERBEROS_FOR_LOGGING
        )

    @patch(
        "sagemaker_studio_analytics_extension.utils.arg_validators.emr_validator.EMRValidator.validate_emr_args"
    )
    def test_metric_auth_type_no_auth(
        self,
        mock_validate_emr_args,
        mock_logger,
        mock_kernel_name,
        mock_emr_connect,
        mock_get_boto3_session,
        mock_get_emr_client,
        mock_EMRCluster,
        mock_context,
    ):
        # mock
        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=False)
        mock_EMRCluster.return_value = mock_emr_cluster

        # test
        sm = SagemakerAnalytics()
        sm.sm_analytics(
            f"emr connect --cluster-id {DUMMY_CLUSTER_ID} --auth-type dummy-value"
        )

        # verify
        actual_service_metric = _get_func_arguments_from_mock(mock_logger, "log")
        actual_metric_dict = json.loads(actual_service_metric.serialize())
        _match_dict(actual_metric_dict, _create_emr_metric_dict("MagicMock", None))
        assert (
            actual_metric_dict[MetricDimension.AuthType.value]
            == AUTH_TYPE_NO_AUTH_FOR_LOGGING
        )


class TestMetricEmissions(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.resource.emr.auth.ClusterAuthUtils.is_cluster_ldap"
    )
    def test_auth_type_for_logging(self, mock_is_cluster_ldap):
        # -------------------------
        # --- RBAC ----
        # -------------------------
        # mock
        mock_emr_execution_role = "mock-execution-role"

        mock_args = MagicMock()
        mock_args.configure_mock(
            emr_execution_role_arn=mock_emr_execution_role,
            auth_type=AUTH_TYPE_BASIC_ACCESS,
        )

        mock_emr_cluster = MagicMock()

        # test
        auth_type_for_logging = ClusterAuthUtils.get_auth_type_for_logging(
            args=mock_args, cluster=mock_emr_cluster
        )

        # verify
        assert auth_type_for_logging == AUTH_TYPE_RBAC_FOR_LOGGING

        # -------------------------
        # --- LDAP ---
        # -------------------------
        # mock
        mock_args = MagicMock()
        mock_args.configure_mock(
            auth_type=AUTH_TYPE_BASIC_ACCESS, emr_execution_role_arn=None
        )

        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=True)

        mock_is_cluster_ldap.return_value = True

        # test
        auth_type_for_logging = ClusterAuthUtils.get_auth_type_for_logging(
            args=mock_args, cluster=mock_emr_cluster
        )

        # verify
        assert auth_type_for_logging == AUTH_TYPE_LDAP_FOR_LOGGING

        # -------------------------
        # --- HTTP Basic ---
        # -------------------------
        # mock
        mock_args = MagicMock()
        mock_args.configure_mock(
            auth_type=AUTH_TYPE_BASIC_ACCESS, emr_execution_role_arn=None
        )

        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=True)

        mock_is_cluster_ldap.return_value = False

        # test
        auth_type_for_logging = ClusterAuthUtils.get_auth_type_for_logging(
            args=mock_args, cluster=mock_emr_cluster
        )

        # verify
        assert auth_type_for_logging == AUTH_TYPE_HTTP_BASIC_FOR_LOGGING

        # -------------------------
        # --- Kerberos ---
        # -------------------------
        # mock
        mock_args = MagicMock()
        mock_args.configure_mock(auth_type="dummy-value", emr_execution_role_arn=None)

        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=True)

        # test
        auth_type_for_logging = ClusterAuthUtils.get_auth_type_for_logging(
            args=mock_args, cluster=mock_emr_cluster
        )

        # verify
        assert auth_type_for_logging == AUTH_TYPE_KERBEROS_FOR_LOGGING

        # -------------------------
        # --- no auth ---
        # -------------------------
        # mock
        mock_args = MagicMock()
        mock_args.configure_mock(auth_type="dummy-value", emr_execution_role_arn=None)

        mock_emr_cluster = MagicMock()
        mock_emr_cluster.configure_mock(is_krb_cluster=False)

        # test
        auth_type_for_logging = ClusterAuthUtils.get_auth_type_for_logging(
            args=mock_args, cluster=mock_emr_cluster
        )

        # verify
        assert auth_type_for_logging == AUTH_TYPE_NO_AUTH_FOR_LOGGING


def _get_func_arguments_from_mock(mock, func_name):
    """
    Returns arguments passed to func_name from a list of calls made to the mock.
    :param mock: mock
    :param func_name:  func_name
    :return:
    """
    for call in mock.mock_calls:
        name, args, kargs = call
        if func_name in name:
            return args[0]
    return None


def _match_dict(dict1, dict2):
    """
    Ensure values for keys which are present in both dict match
    """
    set1 = set(dict1)
    set2 = set(dict2)
    tc = unittest.TestCase()
    for key in set1.intersection(set2):
        if MetricDimension.LibraryVersion.value == key:
            """
            Analytics lib defaults to UNKNOWN in case of errors while identifying the current version.
            Ensure that the new versions published don't encounter errors resulting in UNKNOWN lib version.
            """
            tc.assertTrue(dict1[key] != "UNKNOWN")
            tc.assertTrue(dict2[key] != "UNKNOWN")
        else:
            tc.assertEqual(
                dict1[key],
                dict2[key],
                f"Actual `{dict1[key]}` != Expected `{dict2[key]}` for {key}",
            )


def _create_emr_metric_dict(
    expected_kernel_name=None,
    expected_fault=None,
    expected_error=None,
    expected_exception_name=None,
    expected_exception_message=None,
):
    return {
        MetricDimension.LibraryVersion.value: get_expected_library_version(),
        MetricDimension.Service.value: "emr",
        MetricDimension.Operation.value: "connect",
        MetricDimension.AccountId.value: DUMMY_ACCOUNT_ID,
        MetricDimension.Exception.value: expected_exception_name,
        MetricDimension.Fault.value: 1 if expected_fault else 0,
        MetricDimension.Success.value: 0 if (expected_fault or expected_error) else 1,
        MetricDimension.Error.value: 1 if expected_error else 0,
        MetricDimension.ClusterId.value: DUMMY_CLUSTER_ID,
        MetricDimension.KernelName.value: expected_kernel_name,
        MetricDimension.ExceptionString.value: expected_exception_message,
    }


def get_expected_library_version():
    with open(os.path.join(os.path.dirname(__file__), "../setup.py"), "r") as f:
        for line in f:
            if "VERSION" in line:
                return line.split("=")[1]


class CustomException(Exception):
    pass
