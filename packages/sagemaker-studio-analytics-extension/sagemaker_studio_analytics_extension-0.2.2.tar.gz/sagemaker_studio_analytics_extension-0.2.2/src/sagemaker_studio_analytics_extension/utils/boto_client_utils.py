# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import os

import boto3
import botocore

from .client_factory import ClientFactory

CUSTOM_MODEL_DIRECTORY = "/opt/ml/aws-models"


def get_boto3_session(role_arn=None):
    """
    Create boto session which allow cross account cluster access by pass remote role_arn.
    The tags(as json object) are passed as session tags only when assumable role is specified.

    :param role_arn: IAM role arn to assume if not none.
    :return: boto3 session.
    """

    if not role_arn:
        session = boto3.session.Session()
    else:
        try:
            sts_client = ClientFactory.get_regional_sts_client()
            params = {"RoleArn": role_arn, "RoleSessionName": "SageMakerStudioUser"}
            assume_role_object = sts_client.assume_role(**params)
        except botocore.exceptions.ClientError as ce:
            raise ValueError(
                f"Unable to assume role(arn: {role_arn}). Ensure permissions are setup correctly"
                f' Error: {ce.response["Error"]}'
            ) from None
        session = boto3.Session(
            aws_access_key_id=assume_role_object["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assume_role_object["Credentials"]["SecretAccessKey"],
            aws_session_token=assume_role_object["Credentials"]["SessionToken"],
        )

    # Special handling for EMR GCSC API
    # DataScience and SparkMagic images will have the EMR custom SDK installed in this location
    # For the boto session loader, see https://stackoverflow.com/questions/63512015/boto3-load-custom-models
    if os.path.exists(CUSTOM_MODEL_DIRECTORY):
        session._loader.search_paths.extend([CUSTOM_MODEL_DIRECTORY])

    return session
