import unittest

import boto3
from botocore.stub import Stubber
from sagemaker_studio_analytics_extension.magics import (
    _validate_cluster_auth_with_auth_type_provided,
)
from sagemaker_studio_analytics_extension.magics.sagemaker_analytics import (
    ClusterAuthUtils,
)
from sagemaker_studio_sparkmagic_lib.emr import EMRCluster
from unittest.mock import MagicMock

mock_args = MagicMock()

dummy_auth_type_kerberos = "Kerberos"
dummy_auth_type_basic = "Basic_Access"

emr = boto3.client("emr", region_name="us-west-2")


def dummy_describe_cluster_response_ldap():
    describe_cluster_response = {
        "Cluster": {
            "Id": "j-3DD9ZR01DAU14",
            "Name": "MyCluster",
            "MasterPublicDnsName": "ip-10-0-20-70.ec2.internal",
            "Configurations": [
                {
                    "Classification": "livy-conf",
                    "Properties": {
                        "livy.server.port": "8999",
                        "livy.server.session.timeout": "2h",
                        "livy.server.auth.type": "ldap",
                    },
                }
            ],
        }
    }
    return describe_cluster_response


def dummy_describe_cluster_response_none_auth():
    describe_cluster_response = {
        "Cluster": {
            "Id": "j-3DD9ZR01DAU14",
            "Name": "MyCluster",
            "MasterPublicDnsName": "ip-10-0-20-70.ec2.internal",
            "Configurations": [
                {
                    "Classification": "livy-conf",
                    "Properties": {
                        "livy.server.port": "8999",
                        "livy.server.session.timeout": "2h",
                    },
                }
            ],
        }
    }
    return describe_cluster_response


def dummy_list_instances_response():
    list_instances_response = {
        "Instances": [
            {
                "Id": "j-3DD9ZR01DAU14",
                "PublicDnsName": "ip-10-0-20-70.ec2.internal",
                "PrivateDnsName": "ip-10-0-20-70.ec2.internal",
            }
        ]
    }
    return list_instances_response


def dummy_list_instances_response_kerberos():
    list_instances_response = {
        "Instances": [
            {
                "Id": "j-3DD9ZR01DAU14",
                "Ec2InstanceId": "i-0736242069217a485",
                "PublicDnsName": "ec2-34-222-47-14.us-west-2.compute.amazonaws.com",
                "PublicIpAddress": "34.222.47.14",
                "PrivateDnsName": "ip-172-31-1-113.us-west-2.compute.internal",
                "PrivateIpAddress": "172.31.1.113",
            }
        ]
    }
    return list_instances_response


def dummy_describe_sec_conf_response():
    describe_sec_conf_response = {
        "Name": "kerb-security-config",
        "SecurityConfiguration": '{"EncryptionConfiguration": {"EnableInTransitEncryption": false, '
        '"EnableAtRestEncryption": false},"AuthenticationConfiguration": {'
        '"KerberosConfiguration": {"Provider": "ClusterDedicatedKdc", '
        '"ClusterDedicatedKdcConfiguration": {"TicketLifetimeInHours": 24 }}}}',
    }
    return describe_sec_conf_response


def dummy_describe_cluster_response_kerberos():
    describe_cluster_response = {
        "Cluster": {
            "Id": "j-3DD9ZR01DAU14",
            "Name": "Mycluster",
            "SecurityConfiguration": "kerb-security-config",
            "KerberosAttributes": {
                "Realm": "KTEST.COM",
                "KdcAdminPassword": "********",
            },
            "MasterPublicDnsName": "ec2-34-222-47-14.us-west-2.compute.amazonaws.com",
        }
    }
    return describe_cluster_response


class TestClusterAuthAgainstProvidedAuth(unittest.TestCase):
    def test_ldap_cluster_none_auth_provided_fail(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = dummy_describe_cluster_response_ldap()
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            mock_args.auth_type = "None"

            with self.assertRaises(Exception) as e:
                _validate_cluster_auth_with_auth_type_provided(mock_args, emr_cluster)
            self.assertEqual(
                str(e.exception),
                "Cluster auth type does not match provided auth None",
            )

    def test_ldap_cluster_kerberos_auth_provided_fail(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = dummy_describe_cluster_response_ldap()
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            mock_args.auth_type = "Kerberos"

            with self.assertRaises(Exception) as e:
                _validate_cluster_auth_with_auth_type_provided(mock_args, emr_cluster)
            self.assertEqual(
                str(e.exception),
                "Cluster auth type does not match provided auth Kerberos",
            )

    def test_no_auth_cluster_kerberos_auth_provided_fail(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = dummy_describe_cluster_response_none_auth()
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            mock_args.auth_type = "Kerberos"

            with self.assertRaises(Exception) as e:
                _validate_cluster_auth_with_auth_type_provided(mock_args, emr_cluster)
            self.assertEqual(
                str(e.exception),
                "Cluster auth type does not match provided auth Kerberos",
            )

    def test_kerberos_auth_cluster_none_auth_provided_fail(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = dummy_describe_cluster_response_kerberos()
            describe_sec_conf_response = dummy_describe_sec_conf_response()
            list_instances_response = dummy_list_instances_response_kerberos()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_stub.add_response(
                "describe_security_configuration", describe_sec_conf_response
            )
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            assert emr_cluster.is_krb_cluster
            assert not ClusterAuthUtils.is_cluster_ldap(emr_cluster)
            mock_args.auth_type = "None"

            with self.assertRaises(Exception) as e:
                _validate_cluster_auth_with_auth_type_provided(mock_args, emr_cluster)
            self.assertEqual(
                str(e.exception),
                "Cluster auth type does not match provided auth None",
            )
