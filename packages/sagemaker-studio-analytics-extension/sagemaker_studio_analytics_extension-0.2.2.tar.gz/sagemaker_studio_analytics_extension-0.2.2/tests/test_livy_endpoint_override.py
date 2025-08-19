import unittest

import boto3
from botocore.stub import Stubber
from sagemaker_studio_analytics_extension.magics import _get_livy_port_override
from sagemaker_studio_sparkmagic_lib.emr import EMRCluster

emr = boto3.client("emr", region_name="us-west-2")


class TestLivyEndpointOverride(unittest.TestCase):
    def test_livy_endpoint_port_override(self):
        with Stubber(emr) as emr_stub:
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
                        },
                    ],
                }
            }
            list_instances_response = {
                "Instances": [
                    {
                        "Id": "j-3DD9ZR01DAU14",
                        "PublicDnsName": "ip-10-0-20-70.ec2.internal",
                        "PrivateDnsName": "ip-10-0-20-70.ec2.internal",
                    }
                ]
            }
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)

            emr_configuration_list = emr_cluster.__dict__.get("_cluster").get(
                "Configurations"
            )
            self.assertEqual(
                "8999",
                _get_livy_port_override(emr_configuration_list[0]),
            )

    def test_livy_endpoint_override_none(self):
        with Stubber(emr) as emr_stub:
            describe_cluster_response = {
                "Cluster": {
                    "Id": "j-3DD9ZR01DAU14",
                    "Name": "MyCluster",
                    "MasterPublicDnsName": "ip-10-0-20-70.ec2.internal",
                    "Configurations": [
                        {},
                        {
                            "Classification": "livy-conf",
                            "Properties": {
                                "livy.server.session.timeout": "2h",
                            },
                        },
                    ],
                }
            }
            list_instances_response = {
                "Instances": [
                    {
                        "Id": "j-3DD9ZR01DAU14",
                        "PublicDnsName": "ip-10-0-20-70.ec2.internal",
                        "PrivateDnsName": "ip-10-0-20-70.ec2.internal",
                    }
                ]
            }
            emr_stub.add_response("describe_cluster", describe_cluster_response)
            emr_stub.add_response("list_instances", list_instances_response)
            emr_cluster = EMRCluster(cluster_id="j-3DD9ZR01DAU14", emr=emr)

            emr_configuration_list = emr_cluster.__dict__.get("_cluster").get(
                "Configurations"
            )
            livy_endpoint_override = _get_livy_port_override(emr_configuration_list[0])

            self.assertIsNone(livy_endpoint_override)
