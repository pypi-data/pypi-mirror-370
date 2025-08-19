# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from enum import Enum

from sagemaker_jupyterlab_extension_common.dual_stack_utils import is_dual_stack_enabled


LIBRARY_NAME = "sagemaker-analytics"
EXTENSION_NAME = "sagemaker_studio_analytics_extension"
USE_DUALSTACK_ENDPOINT = is_dual_stack_enabled()


class SERVICE(str, Enum):
    EMR = "emr"
    EMR_SERVERLESS = "emr-serverless"

    @staticmethod
    def list():
        return list(map(lambda s: s.value, SERVICE))


class OPERATION(str, Enum):
    CONNECT = "connect"
    EMRS_CONNECT = "emrs_connect"  # only for metrics
    HELP = "help"

    @staticmethod
    def list():
        return list(map(lambda s: s.value, OPERATION))


## Logging
SAGEMAKER_ANALYTICS_LOG_BASE_DIRECTORY = "/var/log/studio/sagemaker_analytics"

## Auth Types For Logging
AUTH_TYPE_LDAP_FOR_LOGGING = "ldap"
AUTH_TYPE_KERBEROS_FOR_LOGGING = "kerberos"
AUTH_TYPE_HTTP_BASIC_FOR_LOGGING = "http-basic"
AUTH_TYPE_RBAC_FOR_LOGGING = "rbac"
AUTH_TYPE_NO_AUTH_FOR_LOGGING = "no-auth"
AUTH_TYPE_SET_FOR_LOGGING = (
    AUTH_TYPE_LDAP_FOR_LOGGING,
    AUTH_TYPE_KERBEROS_FOR_LOGGING,
    AUTH_TYPE_HTTP_BASIC_FOR_LOGGING,
    AUTH_TYPE_RBAC_FOR_LOGGING,
    AUTH_TYPE_NO_AUTH_FOR_LOGGING,
)


class VerifyCertificateArgument:
    class VerifyCertificateArgumentType(str, Enum):
        """
        TRUE is same as verifying with public CA Cert
        """

        PUBLIC_CA_CERT = "True"
        IGNORE_CERT_VERIFICATION = "False"
        PATH_TO_CERT = "PathToCert"

        @staticmethod
        def list():
            return list(
                map(
                    lambda s: s.value,
                    VerifyCertificateArgument.VerifyCertificateArgumentType,
                )
            )

    def __init__(self, verify_certificate: str):
        self.value = None
        if verify_certificate.lower() == "true":
            self.type = self.VerifyCertificateArgumentType.PUBLIC_CA_CERT
            self.value = True
        elif verify_certificate.lower() == "false":
            self.type = self.VerifyCertificateArgumentType.IGNORE_CERT_VERIFICATION
            self.value = False
        else:
            self.type = self.VerifyCertificateArgumentType.PATH_TO_CERT
            self.value = verify_certificate


# Regex pattern for stack trace filters
email_regex = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
# credit to https://uibakery.io/regex-library/phone-number-python
phone_number_regex = (
    "\+?\d{1,4}?[-.\s]?\(?(\d{1,3}?)\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
)

password_regex = "(?i)password\s*[:=]\s*\S+"
api_key_regex = "(?i)apikey\s*[:= ]\s*\S+"
aws_secretkey_regex = "(?i)aws_secret_access_key\s*[:=]\s*\S+"

EMR_CLUSTER_HELP = """
                Usage:
                %sm_analytics emr connect [--auth-type AUTH_TYPE] [--cluster-id CLUSTER_ID]
                    [--language LANGUAGE]
                    [--assumable-role-arn ASSUMABLE_ROLE_ARN]
                    [--emr-execution-role-arn EMR_EXECUTION_ROLE_ARN]
                    [--secret SECRET]
                    [--verify-certificate VERIFY_CERTIFICATE]
                    [--no-override-krb5-conf OPTIONAL]
                    
                --auth-type AUTH_TYPE
                        The authentication type to be used. Supported
                        authentication types are {'Basic_Access', 'Kerberos',
                        'None'}.
                --cluster-id CLUSTER_ID
                        The cluster id to connect to.
                --language LANGUAGE   
                        Language to use. The supported languages for IPython
                        kernel(s) are {'python', 'scala'}. This is a required
                        argument for IPython kernels, but not for magic
                        kernels such as PySpark or SparkScala.
                --assumable-role-arn ASSUMABLE_ROLE_ARN
                        The IAM role to assume when connecting to a cluster in
                        a different AWS account. This argument is not required
                        when connecting to a cluster in the same AWS account.
                --emr-execution-role-arn EMR_EXECUTION_ROLE_ARN
                        The IAM role passed to EMR to set up EMR job security
                        context. This argument is optional and used when IAM
                        Passthrough feature is enabled for EMR.
                --secret SECRET       
                    The AWS Secrets Manager SecretID.
                --verify-certificate VERIFY_CERTIFICATE
                        Determine if SSL certificate should be verified when
                        using HTTPS to connect to EMR. Supported values are
                        ['True', 'False', 'PathToCert']. If a path-to-cert-
                        file is provided, the certificate verification will be
                        done with the certificate in the provided file
                        path.Note that the default
                --no-override-krb5-conf OPTIONAL
                        This argument is used standalone (no input value needed) 
                        and only when connecting to Kerberos cluster. With this 
                        key SageMaker will not override existing krb5.conf file.
                        User should make sure there is krb5.conf file at 
                        /etc/krb5.conf. If this key this not present, Sagemaker
                        will generate and override the krb5.conf file by default. 

                Examples:
                # Connect Studio notebook using IPython Kernel to EMR cluster protected by Kerberos.
                %sm_analytics emr connect --cluster-id j-1JIIZS02SEVCS --auth-type Kerberos --language python
                
                # Connect Studio notebook using IPython Kernel to HTTP Basic Auth protected EMR cluster and create 
                the Scala based session.
                %sm_analytics emr connect --cluster-id j-1KHIOQZAQUF5P --auth-type Basic_Access  --language scala
                
                # Connect Studio notebook using IPython Kernel to EMR cluster directly without Livy authentication.
                %sm_analytics emr connect --cluster-id j-1KHIOQZAQUF5P --auth-type None  --language python
                
                # Connect Studio notebook using PySpark or Spark(scala) Kernel to HTTP Basic Auth protected EMR cluster.
                %sm_analytics emr connect --cluster-id j-1KHIOQZAQUF5P --auth-type Basic_Access
                """
EMR_SERVERLESS_HELP = """
                    Usage:
                    %sm_analytics emr-serverless connect [--application-id APPLICATION_ID]
                        [--language LANGUAGE]
                        [--assumable-role-arn ASSUMABLE_ROLE_ARN]
                        [--emr-execution-role-arn EMR_EXECUTION_ROLE_ARN]
                                        
                        --application-id APPLICATION_ID
                            The EMR Serverless Application to connect to. This argument 
                            is required.
                        --language LANGUAGE   
                            Language to use. The supported languages for IPython
                            kernel(s) are {'python', 'scala'}. This is a required
                            argument for IPython kernels, but not for magic
                            kernels such as PySpark or SparkScala.
                        --assumable-role-arn ASSUMABLE_ROLE_ARN
                            The IAM role to assume when connecting to an EMR Serverless 
                            Application in a different AWS account. This argument is not 
                            required when connecting to an EMR Serverless Application in 
                            the same AWS account.
                        --emr-execution-role-arn EMR_EXECUTION_ROLE_ARN
                            The IAM role passed to EMR Serverless to perform operations 
                            on behalf of the customer. This argument is required.      

                        Examples:
                        # Connect Studio notebook using IPython Kernel to EMR Serverless application and create Scala based session
                        %sm_analytics emr-serverless connect --application-id <APPLICATION_ID> 
                        --emr-execution-role-arn <EMR_EXECUTION_ROLE_ARN>
                        --language scala
                         
                        # Connect Studio notebook using PySpark or Spark(scala) Kernel to EMR Serverless application
                        %sm_analytics emr-serverless connect --application-id <APPLICATION_ID> 
                        --emr-execution-role-arn <EMR_EXECUTION_ROLE_ARN>
                        
                        # Connect Studio notebook using PySpark or Spark(scala) Kernel to EMR Serverless application 
                        in another account
                        %sm_analytics emr-serverless connect --application-id <APPLICATION_ID> 
                        --emr-execution-role-arn <EMR_EXECUTION_ROLE_ARN> --assumable-role-arn <ASSUMABLE_ROLE_ARN>

                    """
SM_ANALYTICS_USAGE = """
        Services currently supported: emr, emr-serverless
        Please look at usage of %sm_analytics by executing `%sm_analytics <SERVICE_NAME> help`
        Example:
        %sm_analytics emr help
        %sm_analytics emr-serverless help
        """
