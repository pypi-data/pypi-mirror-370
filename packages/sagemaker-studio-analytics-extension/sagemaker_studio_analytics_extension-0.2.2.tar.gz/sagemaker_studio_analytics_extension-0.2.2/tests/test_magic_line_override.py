import unittest
from unittest.mock import patch

import boto3
import pytest
import sparkmagic.utils.configuration as conf
from botocore.stub import Stubber
from sagemaker_studio_analytics_extension.magics import (
    _get_endpoint_magic_line,
)
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    IPYTHON_KERNEL,
    MAGIC_KERNELS,
)
from sagemaker_studio_sparkmagic_lib.emr import EMRCluster

from sagemaker_studio_analytics_extension.utils.string_utils import is_not_blank

from sagemaker_studio_analytics_extension.utils.exceptions import LivyConnectionError

from sagemaker_studio_analytics_extension.utils.magic_execution_context import (
    MagicExecutionContext,
)

from sagemaker_studio_analytics_extension.utils.constants import (
    VerifyCertificateArgument,
)

EMR_DUMMY_CLUSTER_ID = "j-3DD9ZR01DAU14"
EMR_PRIMARY_NODE_PRIVATE_DNS = "ip-10-0-20-70.ec2.internal"
EMR_PRIMARY_NODE_PUBLIC_DNS = "ec2-18-118-14-129.us-east-2.compute.amazonaws.com"

emr = boto3.client("emr", region_name="us-west-2")


class DummyArgsPython:
    auth_type = "None"
    cluster_id = EMR_DUMMY_CLUSTER_ID
    language = "python"
    verify_certificate = VerifyCertificateArgument("True")


class DummyArgsScala:
    auth_type = "None"
    cluster_id = EMR_DUMMY_CLUSTER_ID
    language = "scala"


def get_dummy_describe_cluster_response():
    describe_cluster_response = {
        "Cluster": {
            "Id": EMR_DUMMY_CLUSTER_ID,
            "Name": "MyCluster",
            "MasterPublicDnsName": EMR_PRIMARY_NODE_PRIVATE_DNS,
            "InstanceCollectionType": "INSTANCE_GROUP",
            "Configurations": [
                {
                    # Force the livy server port config to be second element in list to make sure we go through all
                    # configurations before establishing that the livy server port is not overridden
                },
                {
                    "Classification": "livy-conf",
                    "Properties": {
                        "livy.server.port": "8999",
                        "livy.server.session.timeout": "2h",
                    },
                },
            ],
        }
    }
    return describe_cluster_response


def get_dummy_public_cluster_describe_cluster_response():
    describe_cluster_response = {
        "Cluster": {
            "Id": EMR_DUMMY_CLUSTER_ID,
            "Name": "MyCluster",
            "MasterPublicDnsName": EMR_PRIMARY_NODE_PUBLIC_DNS,
            "InstanceCollectionType": "INSTANCE_GROUP",
            "Configurations": [
                {
                    # Force the livy server port config to be second element in list to make sure we go through all
                    # configurations before establishing that the livy server port is not overridden
                },
                {
                    "Classification": "livy-conf",
                    "Properties": {
                        "livy.server.port": "8999",
                        "livy.server.session.timeout": "2h",
                    },
                },
            ],
        }
    }
    return describe_cluster_response


def get_dummy_list_instances_response():
    list_instances_response = {
        "Instances": [
            {
                "Id": EMR_DUMMY_CLUSTER_ID,
                "PublicDnsName": EMR_PRIMARY_NODE_PUBLIC_DNS,
                "PrivateDnsName": EMR_PRIMARY_NODE_PRIVATE_DNS,
            }
        ]
    }
    return list_instances_response


def get_dummy_list_instances_response_with_no_public_dns():
    list_instances_response = {
        "Instances": [
            {
                "Id": EMR_DUMMY_CLUSTER_ID,
                "PublicDnsName": "",
                "PrivateDnsName": EMR_PRIMARY_NODE_PRIVATE_DNS,
            }
        ]
    }
    return list_instances_response


def get_list_instance_groups_response():
    list_instance_groups_response = {
        "InstanceGroups": [
            {
                "InstanceGroupType": "MASTER",
                "Configurations": [
                    {
                        # Force the livy server port config to be second element in list to make sure we go through
                        # all configurations before establishing that the livy server port is not overridden
                    },
                    {
                        "Classification": "livy-conf",
                        "Properties": {"livy.server.port": "8999"},
                    },
                ],
            },
            {
                "InstanceGroupType": "CORE",
                "Configurations": [
                    {
                        "Classification": "livy-conf",
                        "Properties": {"livy.server.port": "8999"},
                    }
                ],
            },
        ]
    }
    return list_instance_groups_response


def get_describe_cluster_response(instance_collection_type="INSTANCE_GROUP"):
    describe_cluster_response = {
        "Cluster": {
            "Id": EMR_DUMMY_CLUSTER_ID,
            "Name": "MyCluster",
            "MasterPublicDnsName": EMR_PRIMARY_NODE_PRIVATE_DNS,
            "InstanceCollectionType": instance_collection_type,
            "Configurations": [
                {
                    "Classification": "livy-conf",
                    "Properties": {
                        "livy.server.session.timeout": "2h",
                    },
                }
            ],
        }
    }
    return describe_cluster_response


def mock_check_host_and_port_for_public_cluster(host, _):
    """
    Fail host-port check for private or empty dns, succeed otherwise
    Private dns has `internal` in its name: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-naming.html
    :param host: host
    :param _: port. Not used.
    :return: True if host is not blank and is not internal dns.
    """
    return is_not_blank(host) and ("internal" not in host)


@pytest.fixture(scope="session", autouse=True)
def set_session_name():
    conf.override(conf.session_configs.__name__, {"name": "session_name"})


class TestMagicLineOverride(unittest.TestCase):
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_cluster_configuration_no_auth_magic_kernels(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        for kernel in MAGIC_KERNELS:
            with Stubber(emr) as emr_stub:
                describe_cluster_response = get_dummy_describe_cluster_response()
                list_instances_response = get_dummy_list_instances_response()
                emr_stub.add_response("describe_cluster", describe_cluster_response)
                emr_stub.add_response("list_instances", list_instances_response)
                emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

                # set mock to pass host and port fast fail check
                mock_check_host_and_port.return_value = True
                # set mock to return False indicating http protocol
                mock_is_ssl_enabled.return_value = False

                self.assertEqual(
                    _get_endpoint_magic_line(
                        context,
                        emr,
                        DummyArgsPython(),
                        emr_cluster,
                        None,
                        None,
                        kernel,
                    ),
                    f"-s http://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8999 -t None",
                )
                self.assertEqual(context.connection_protocol, "http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_cluster_configuration_no_auth_ipython_kernel(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        with Stubber(emr) as emr_stub:
            describe_cluster_response = get_dummy_describe_cluster_response()
            list_instances_response = get_dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

            # set mock to pass host and port fast fail check
            mock_check_host_and_port.return_value = True
            # set mock to return False indicating http protocol
            mock_is_ssl_enabled.return_value = False

            magic_line_override = _get_endpoint_magic_line(
                context,
                emr,
                DummyArgsPython(),
                emr_cluster,
                None,
                None,
                IPYTHON_KERNEL,
            )
            print(magic_line_override)
            self.assertTrue(magic_line_override.__contains__("add -s "))
            self.assertTrue(
                magic_line_override.__contains__(
                    f"-l python -t None -u http://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8999"
                )
            )
            self.assertEqual(context.connection_protocol, "http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._set_ssl_configs"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_public_ssl_cluster_no_auth_all_kernels_happy_case(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
        mock_set_ssl_configs,
    ):
        context = MagicExecutionContext()
        with Stubber(emr) as emr_stub:
            describe_cluster_response = (
                get_dummy_public_cluster_describe_cluster_response()
            )
            list_instances_response = get_dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

            # set mock to pass host and port check if using public dns, fail if using private dns
            mock_check_host_and_port.side_effect = (
                mock_check_host_and_port_for_public_cluster
            )
            mock_is_ssl_enabled.return_value = True
            mock_set_ssl_configs.return_value = None

            all_kernels = MAGIC_KERNELS.union({IPYTHON_KERNEL})

            for kernel in all_kernels:
                magic_line_override = _get_endpoint_magic_line(
                    context,
                    emr,
                    DummyArgsPython(),
                    emr_cluster,
                    None,
                    None,
                    kernel,
                )
                self.assertTrue(
                    magic_line_override.__contains__(
                        f"https://{EMR_PRIMARY_NODE_PUBLIC_DNS}:8999"
                    )
                )

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_public_cluster_configuration_no_ssl_all_kernels_fails(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        with Stubber(emr) as emr_stub:
            describe_cluster_response = (
                get_dummy_public_cluster_describe_cluster_response()
            )
            list_instances_response = get_dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

            # set mock to pass host and port check if using public dns, fail if using private dns
            mock_check_host_and_port.side_effect = (
                mock_check_host_and_port_for_public_cluster
            )
            mock_is_ssl_enabled.return_value = False

            all_kernels = MAGIC_KERNELS.union({IPYTHON_KERNEL})

            for kernel in all_kernels:
                with self.assertRaises(LivyConnectionError) as assert_raises_contex:
                    _get_endpoint_magic_line(
                        context,
                        emr,
                        DummyArgsPython(),
                        emr_cluster,
                        None,
                        None,
                        kernel,
                    )
                expected_error_message = f"Livy is available at {EMR_PRIMARY_NODE_PUBLIC_DNS}:8999, but not configured to use HTTPS. Please setup livy with HTTPS: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/enabling-https.html"
                assert expected_error_message in str(assert_raises_contex.exception)

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_cluster_configuration_no_auth_ipython_kernel_scala(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        with Stubber(emr) as emr_stub:
            describe_cluster_response = get_dummy_describe_cluster_response()
            list_instances_response = get_dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

            # set mock to pass host and port fast fail check
            mock_check_host_and_port.return_value = True
            # set mock to return False indicating http protocol
            mock_is_ssl_enabled.return_value = False

            magic_line_override = _get_endpoint_magic_line(
                context,
                emr,
                DummyArgsScala(),
                emr_cluster,
                None,
                None,
                "IPythonKernel",
            )
            self.assertTrue(magic_line_override.__contains__("add -s "))
            self.assertTrue(
                magic_line_override.__contains__(
                    f"-l scala -t None -u http://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8999"
                )
            )
            self.assertEqual(context.connection_protocol, "http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_instance_group_configuration_no_auth_ipython_kernel(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        describe_cluster_response = get_describe_cluster_response()
        list_instance_groups_response = get_list_instance_groups_response()
        list_instances_response = get_dummy_list_instances_response()

        with Stubber(emr) as emr_stub:
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_stub.add_response("list_instance_groups", list_instance_groups_response)
            emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

            # set mock to pass host and port fast fail check
            mock_check_host_and_port.return_value = True
            # set mock to return False indicating http protocol
            mock_is_ssl_enabled.return_value = False

            magic_line_override = _get_endpoint_magic_line(
                context,
                emr,
                DummyArgsPython(),
                emr_cluster,
                None,
                None,
                IPYTHON_KERNEL,
            )
            print(magic_line_override)
            self.assertTrue(magic_line_override.__contains__("add -s"))
            self.assertTrue(
                magic_line_override.__contains__(
                    f"-l python -t None -u http://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8999"
                )
            )
            self.assertEqual(context.connection_protocol, "http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_instance_group_configuration_no_auth_ipython_kernel_scala(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        describe_cluster_response = get_describe_cluster_response()
        list_instance_groups_response = get_list_instance_groups_response()
        list_instances_response = get_dummy_list_instances_response()

        with Stubber(emr) as emr_stub:
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_stub.add_response("list_instance_groups", list_instance_groups_response)
            emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

            # set mock to pass host and port fast fail check
            mock_check_host_and_port.return_value = True
            # set mock to return False indicating http protocol
            mock_is_ssl_enabled.return_value = False

            magic_line_override = _get_endpoint_magic_line(
                context,
                emr,
                DummyArgsScala(),
                emr_cluster,
                None,
                None,
                IPYTHON_KERNEL,
            )
            self.assertTrue(magic_line_override.__contains__("add -s"))
            self.assertTrue(
                magic_line_override.__contains__(
                    f"-l scala -t None -u http://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8999"
                )
            )
            self.assertEqual(context.connection_protocol, "http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_magic_line_override_from_instance_group_configuration_no_auth_magic_kernels(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        context = MagicExecutionContext()
        describe_cluster_response = get_describe_cluster_response()
        list_instance_groups_response = get_list_instance_groups_response()
        list_instances_response = get_dummy_list_instances_response()

        for kernel in MAGIC_KERNELS:
            with Stubber(emr) as emr_stub:
                emr_stub.add_response("describe_cluster", describe_cluster_response)
                emr_stub.add_response("list_instances", list_instances_response)
                emr_stub.add_response(
                    "list_instance_groups", list_instance_groups_response
                )
                emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

                # set mock to pass host and port fast fail check
                mock_check_host_and_port.return_value = True
                # set mock to return False indicating http protocol
                mock_is_ssl_enabled.return_value = False

                self.assertEqual(
                    _get_endpoint_magic_line(
                        context,
                        emr,
                        DummyArgsPython(),
                        emr_cluster,
                        None,
                        None,
                        kernel,
                    ),
                    f"-s http://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8999 -t None",
                )
                self.assertEqual(context.connection_protocol, "http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_fast_fail_due_to_host_and_port_check_for_magic_kernels(
        self,
        mock_check_host_and_port,
    ):
        context = MagicExecutionContext()
        for kernel in MAGIC_KERNELS:
            with Stubber(emr) as emr_stub:
                describe_cluster_response = get_dummy_describe_cluster_response()
                list_instances_response = get_dummy_list_instances_response()
                emr_stub.add_response("describe_cluster", describe_cluster_response)
                emr_stub.add_response("list_instances", list_instances_response)
                emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

                # set mock to fail host and port fast fail check
                mock_check_host_and_port.return_value = False
                with self.assertRaises(LivyConnectionError) as assert_raises_contex:
                    _get_endpoint_magic_line(
                        context,
                        emr,
                        DummyArgsPython(),
                        emr_cluster,
                        None,
                        None,
                        kernel,
                    )
                expected_error_message = (
                    f"Cannot connect to livy service "
                    f"at {EMR_PRIMARY_NODE_PRIVATE_DNS}:8999 or {EMR_PRIMARY_NODE_PUBLIC_DNS}:8999"
                )
                assert expected_error_message in str(assert_raises_contex.exception)

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_fast_fail_due_to_host_and_port_check_for_magic_kernels_cluster_with_no_public_dns(
        self,
        mock_check_host_and_port,
    ):
        context = MagicExecutionContext()
        for kernel in MAGIC_KERNELS:
            with Stubber(emr) as emr_stub:
                describe_cluster_response = get_dummy_describe_cluster_response()
                list_instances_response = (
                    get_dummy_list_instances_response_with_no_public_dns()
                )

                emr_stub.add_response("describe_cluster", describe_cluster_response)
                emr_stub.add_response("list_instances", list_instances_response)
                emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

                # set mock to fail host and port check
                mock_check_host_and_port.return_value = False
                with self.assertRaises(LivyConnectionError) as assert_raises_contex:
                    _get_endpoint_magic_line(
                        context,
                        emr,
                        DummyArgsPython(),
                        emr_cluster,
                        None,
                        None,
                        kernel,
                    )
                expected_error_message = f"Cannot connect to livy service at {EMR_PRIMARY_NODE_PRIVATE_DNS}:8999"
                assert expected_error_message in str(assert_raises_contex.exception)

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_no_failure_with_emr_using_instance_fleet(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
    ):
        # set mock to pass host and port fast fail check
        mock_check_host_and_port.return_value = True
        # set mock to return False indicating http protocol
        mock_is_ssl_enabled.return_value = False

        self._do_connecting_test(protocol="http")

    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics._set_ssl_configs"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.is_ssl_enabled"
    )
    @patch(
        "sagemaker_studio_analytics_extension.magics.sagemaker_analytics.check_host_and_port"
    )
    def test_livy_with_ssl_enabled(
        self,
        mock_check_host_and_port,
        mock_is_ssl_enabled,
        mock_set_ssl_configs,
    ):
        # set mock to pass host and port fast fail check
        mock_check_host_and_port.return_value = True
        # set mock to return True indicating https protocol
        mock_is_ssl_enabled.return_value = True
        mock_set_ssl_configs.return_value = None

        self._do_connecting_test(protocol="https")

    def _do_connecting_test(self, protocol):
        expected_livy_endpoint = f"{protocol}://{EMR_PRIMARY_NODE_PRIVATE_DNS}:8998"

        context = MagicExecutionContext()
        describe_cluster_response = get_describe_cluster_response("INSTANCE_FLEET")
        list_instances_response = get_dummy_list_instances_response()

        for kernel in MAGIC_KERNELS:
            with Stubber(emr) as emr_stub:
                emr_stub.add_response("describe_cluster", describe_cluster_response)
                emr_stub.add_response("list_instances", list_instances_response)
                emr_cluster = EMRCluster(cluster_id=EMR_DUMMY_CLUSTER_ID, emr=emr)

                self.assertEqual(
                    _get_endpoint_magic_line(
                        context,
                        emr,
                        DummyArgsPython(),
                        emr_cluster,
                        None,
                        None,
                        kernel,
                    ),
                    f"-s {expected_livy_endpoint} -t None",
                )
                self.assertEqual(context.connection_protocol, protocol)
