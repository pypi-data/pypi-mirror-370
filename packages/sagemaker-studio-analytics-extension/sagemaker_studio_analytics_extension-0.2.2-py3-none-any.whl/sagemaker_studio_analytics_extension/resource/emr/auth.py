# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from collections import namedtuple

from sagemaker_studio_analytics_extension.utils.constants import (
    AUTH_TYPE_RBAC_FOR_LOGGING,
    AUTH_TYPE_LDAP_FOR_LOGGING,
    AUTH_TYPE_HTTP_BASIC_FOR_LOGGING,
    AUTH_TYPE_KERBEROS_FOR_LOGGING,
    AUTH_TYPE_NO_AUTH_FOR_LOGGING,
)
from sagemaker_studio_analytics_extension.utils.emr_constants import (
    AUTH_TYPE_BASIC_ACCESS,
)

ClusterSessionCredentials = namedtuple("ClusterSessionCredentials", "username password")


class ClusterSessionCredentialsProvider:
    def get_cluster_session_credentials(
        self, emr_client, cluster_id, emr_execution_role_arn
    ):
        """
        This method is to retrieve the credentials by calling GetClusterSessionCredentials API.
        :param emr_client: EMR client used to communicate with EMR endpoint.
        :param emr_execution_role_arn: The role passed to EMR and used to set up job security context.
        :return: ClusterSessionCredentials
        """
        response = emr_client.get_cluster_session_credentials(
            ClusterId=cluster_id,
            ExecutionRoleArn=emr_execution_role_arn,
        )
        credentials = response["Credentials"]["UsernamePassword"]
        return ClusterSessionCredentials(
            credentials["Username"], credentials["Password"]
        )


class ClusterAuthUtils:
    @staticmethod
    def is_cluster_ldap(cluster):
        emr_configuration_list = cluster.__dict__.get("_cluster").get("Configurations")
        if emr_configuration_list is None or not emr_configuration_list:
            return False

        # For cluster configuration
        for configuration in emr_configuration_list:
            if (
                "Classification" in configuration
                and configuration["Classification"] == "livy-conf"
                and "Properties" in configuration
            ):
                livy_properties = configuration["Properties"]
                if "livy.server.auth.type" in livy_properties:
                    livy_server_auth_type = livy_properties["livy.server.auth.type"]
                    if livy_server_auth_type == "ldap":
                        return True
        return False

    @staticmethod
    def get_auth_type_for_logging(**kwargs):
        """
        Returns the value of auth type to be logged based on logic using cluster config and args

        :param kwargs:  kwargs for the func. Should contain 'args' and 'cluster'
        """

        if "args" not in kwargs:
            raise KeyError("Missing required kwarg. 'args' should be one of the kwargs")
        if "cluster" not in kwargs:
            raise KeyError(
                "Missing required kwarg. 'cluster' should be one of the kwargs"
            )

        args = kwargs["args"]
        emr_cluster = kwargs["cluster"]

        # For RBAC authentication
        if args.auth_type == AUTH_TYPE_BASIC_ACCESS and args.emr_execution_role_arn:
            return AUTH_TYPE_RBAC_FOR_LOGGING
        # For LDAP/HTTP-Basic authentication
        elif args.auth_type == AUTH_TYPE_BASIC_ACCESS:
            # For LDAP authentication
            if ClusterAuthUtils.is_cluster_ldap(emr_cluster):
                return AUTH_TYPE_LDAP_FOR_LOGGING
            # For HTTP-Basic authentication
            else:
                return AUTH_TYPE_HTTP_BASIC_FOR_LOGGING
        # For Kerberos authentication
        elif emr_cluster.is_krb_cluster:
            return AUTH_TYPE_KERBEROS_FOR_LOGGING
        # For no authentication
        else:
            return AUTH_TYPE_NO_AUTH_FOR_LOGGING
