# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
from sparkmagic.utils.constants import LANG_SCALA, LANG_PYTHON

SPARK_SESSION_NAME_PREFIX = "sagemaker_studio_analytics_spark_session"
LANGUAGES_SUPPORTED = {LANG_SCALA, LANG_PYTHON}

## Kennel
IPYTHON_KERNEL = "IPythonKernel"
PYSPARK_KERNEL = "PySparkKernel"
SPARK_KERNEL = "SparkKernel"
MAGIC_KERNELS = {PYSPARK_KERNEL, SPARK_KERNEL}

## Auth type
AUTH_TYPE_NONE = "None"
AUTH_TYPE_KERBEROS = "Kerberos"
AUTH_TYPE_BASIC_ACCESS = "Basic_Access"
AUTH_TYPE_SET = {AUTH_TYPE_NONE, AUTH_TYPE_KERBEROS, AUTH_TYPE_BASIC_ACCESS}

## Kerberos
KRB_FILE_DIR = "/etc"
KRB_FILE_PATH = os.path.join(KRB_FILE_DIR, "krb5.conf")

## EMR
LIVY_DEFAULT_PORT = "8998"
INSTANCE_COLLECTION_TYPE_GROUP = "INSTANCE_GROUP"
EMR_CONNECTION_LOG_FILE = "emr_connection.log"

PUBLIC_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE = "  If Livy is configured with a certificate that is not public CA issued, then either pass --verify-certificate the path to a custom certificate file, or set --verify-certificate to False. Note that when set to False, library will ignore verifying the SSL connection."
SELF_SIGNED_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE = " Ensure that the certificate path provided in --verify-certificate points to the correct certificate. Alternatively, set --verify-certificate to False. Note that when set to False, library will ignore verifying the SSL connection. "
