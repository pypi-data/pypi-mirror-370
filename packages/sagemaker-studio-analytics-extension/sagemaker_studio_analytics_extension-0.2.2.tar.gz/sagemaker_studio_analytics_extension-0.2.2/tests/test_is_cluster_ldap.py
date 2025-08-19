import unittest

import boto3
from botocore.stub import Stubber
from sagemaker_studio_analytics_extension.magics import ClusterAuthUtils

from sagemaker_studio_sparkmagic_lib.emr import EMRCluster

emr = boto3.client("emr", region_name="us-west-2")


def dummy_describe_cluster_response():
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


def dummy_describe_cluster_response_no_configuration():
    describe_cluster_response = {
        "Cluster": {
            "Id": "j-3DD9ZR01DAU14",
            "Name": "MyCluster",
            "MasterPublicDnsName": "ip-10-0-20-70.ec2.internal",
        }
    }
    return describe_cluster_response


def dummy_describe_cluster_response_empty_configuration():
    describe_cluster_response = {
        "Cluster": {
            "Id": "j-3DD9ZR01DAU14",
            "Name": "MyCluster",
            "MasterPublicDnsName": "ip-10-0-20-70.ec2.internal",
            "Configurations": [],
        }
    }
    return describe_cluster_response


def dummy_describe_cluster_response_valid_ldap():
    describe_cluster_response = {
        "Cluster": {
            "Id": "j-3DD9ZR01DAU14",
            "Name": "MyCluster",
            "MasterPublicDnsName": "ip-10-0-20-70.ec2.internal",
            "Configurations": [
                {
                    "Classification": "livy-conf",
                    "Properties": {
                        "livy.server.auth.type": "ldap",
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


class TestArgsValidation(unittest.TestCase):
    def test_not_ldap_with_configuration(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = dummy_describe_cluster_response()
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            assert not ClusterAuthUtils.is_cluster_ldap(emr_cluster)

    def test_not_ldap_with_configuration_none(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = (
                dummy_describe_cluster_response_no_configuration()
            )
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            assert not ClusterAuthUtils.is_cluster_ldap(emr_cluster)

    def test_not_ldap_with_configuration_empty(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = (
                dummy_describe_cluster_response_empty_configuration()
            )
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            assert not ClusterAuthUtils.is_cluster_ldap(emr_cluster)

    def test_valid_ldap_with_configuration(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = dummy_describe_cluster_response_valid_ldap()
            list_instances_response = dummy_list_instances_response()
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)
            assert ClusterAuthUtils.is_cluster_ldap(emr_cluster)
