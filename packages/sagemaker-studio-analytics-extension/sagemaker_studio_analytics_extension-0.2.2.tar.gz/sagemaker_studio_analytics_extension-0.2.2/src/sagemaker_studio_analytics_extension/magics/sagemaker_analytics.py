# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from __future__ import print_function

import os
import ssl

import boto3
import contextlib
import io
import json
import logging
import subprocess
import sys
import base64
from time import sleep
from uuid import uuid4

import IPython
import argparse
import botocore
import requests
import traceback
from botocore.config import Config as BotocoreConfig
import filelock
import sparkmagic.utils.configuration as conf
from IPython import get_ipython
from IPython.core.display import display
from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from botocore.exceptions import ClientError, EndpointConnectionError

# The class MUST call this class decorator at creation time
# https://ipython.readthedocs.io/en/stable/config/custommagics.html
from ipywidgets import widgets
from requests_kerberos import REQUIRED
from sagemaker_studio_sparkmagic_lib.emr import EMRCluster
from sagemaker_studio_sparkmagic_lib.kerberos import write_krb_conf
from sparkmagic.livyclientlib.exceptions import HttpClientException, EXPECTED_EXCEPTIONS
from sagemaker_studio_analytics_extension.utils.constants import USE_DUALSTACK_ENDPOINT

from ..resource.emr.auth import ClusterSessionCredentialsProvider
from ..resource.emr.auth import ClusterAuthUtils
from ..resource.emr.emr_client import get_emr_client
from ..utils.arg_validators.emr_serverless_validator import EMRServerlessValidator
from ..utils.arg_validators.emr_validator import EMRValidator
from ..utils.common_utils import _run_preset_cell_magics
from ..utils.emr_serverless_magic_utils import EMRServerlessMagicUtils
from ..utils.exceptions import (
    LivyConnectionError,
    MissingParametersError,
    InvalidParameterError,
    InvalidConfigError,
)
from ..utils.boto_client_utils import get_boto3_session
from ..utils.magic_execution_context import MagicExecutionContext
from ..utils.constants import (
    LIBRARY_NAME,
    SERVICE,
    OPERATION,
    SAGEMAKER_ANALYTICS_LOG_BASE_DIRECTORY,
    VerifyCertificateArgument,
    SM_ANALYTICS_USAGE,
    EMR_CLUSTER_HELP,
    EMR_SERVERLESS_HELP,
)
from ..utils.emr_constants import (
    IPYTHON_KERNEL,
    MAGIC_KERNELS,
    LANGUAGES_SUPPORTED,
    AUTH_TYPE_SET,
    KRB_FILE_PATH,
    SPARK_SESSION_NAME_PREFIX,
    INSTANCE_COLLECTION_TYPE_GROUP,
    LIVY_DEFAULT_PORT,
    AUTH_TYPE_NONE,
    AUTH_TYPE_KERBEROS,
    AUTH_TYPE_BASIC_ACCESS,
    EMR_CONNECTION_LOG_FILE,
    PUBLIC_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE,
    SELF_SIGNED_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE,
)
from ..utils.logging_utils import ServiceFileLogger
from ..utils.resource_check import check_host_and_port, is_ssl_enabled, verify_ssl_cert
from ..utils.service_metrics import (
    records_service_metrics,
)

from ..utils.string_utils import is_blank, unquote_ends

from ..utils.kerberos_reset_util import handle_kerberos_reset_password

# This logger emits logs to sys.stdout, which is visible in customer's notebook in Studio
sys_out_logger = logging.getLogger(__name__)
sys_out_logger.setLevel(logging.INFO)
sys_out_logger.addHandler(logging.StreamHandler(sys.stdout))

sagemaker_analytics_service_logger = None


def _magic_kernel_connect_to_emr(
    context, emr_client, args, emr_cluster, username, password, kernel_name
):
    """
    Handles connectivity to EMR clusters from PySpark and SparkScala kernels
    """
    print("Initiating EMR connection..")
    ipy = get_ipython()
    _run_preset_cell_magics(ipy)

    endpoint_magic_line = _get_endpoint_magic_line(
        context, emr_client, args, emr_cluster, username, password, kernel_name
    )

    _handle_kerberos_endpoint_override(emr_cluster=emr_cluster)

    existing_all_errors_are_fatal_conf = _configure_ssl_verification_pre_session_start()
    livy_client_expected_exceptions = tuple(EXPECTED_EXCEPTIONS)

    session_started = False
    error_message = None

    try:
        # Pass the livy endpoint to connect to, through the internal cell magic without spark.conf
        change_endpoint_magic = ipy.find_line_magic("_do_not_call_change_endpoint")
        change_endpoint_magic(endpoint_magic_line)

        # Start spark session
        start_session_magic = ipy.find_cell_magic("_do_not_call_start_session")
        session_started = start_session_magic("")

        if not session_started:
            error_message = "Failed to start spark session."

    except livy_client_expected_exceptions as err:
        error_message = _handle_livy_client_expected_exceptions(
            err, args, existing_all_errors_are_fatal_conf
        )
    finally:
        conf.override(
            conf.all_errors_are_fatal.__name__, existing_all_errors_are_fatal_conf
        )

    _echo_response_to_iopub_web_socket(
        _build_response(
            cluster_id=args.cluster_id,
            error_message=error_message,
            success=session_started,
            service="emr",
            operation="connect",
        )
    )


def _configure_ssl_verification_pre_session_start():
    existing_all_errors_are_fatal_conf = conf.all_errors_are_fatal()
    if not conf.ignore_ssl_errors():
        """
        Sparkmagic swallows certain errors, preventing us from knowing if we were not able to connect due to
        SSL cert verification error. Set all_errors_are_fatal flag to enable raising these errors.
        https://github.com/jupyter-incubator/sparkmagic/blob/b5246e8cd0bddf6c5df5761389e4a45fb3fc3032/sparkmagic/sparkmagic/livyclientlib/exceptions.py#L99
        """
        conf.override(conf.all_errors_are_fatal.__name__, True)
    return existing_all_errors_are_fatal_conf


def _handle_livy_client_expected_exceptions(
    err, args, existing_all_errors_are_fatal_conf
):
    error_message = str(err)
    if isinstance(err, HttpClientException):
        if (
            args.verify_certificate.type
            == VerifyCertificateArgument.VerifyCertificateArgumentType.PUBLIC_CA_CERT
        ):
            error_message = (
                error_message + PUBLIC_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE
            )
        elif (
            args.verify_certificate.type
            == VerifyCertificateArgument.VerifyCertificateArgumentType.PATH_TO_CERT
        ):
            error_message = (
                error_message + SELF_SIGNED_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE
            )

    if existing_all_errors_are_fatal_conf:
        # Re-raise the exception with appropriate class if requested.
        raise err.__class__(error_message)

    return error_message


def _get_endpoint_magic_line(
    context, emr_client, args, emr_cluster, username, password, kernel_name
):
    livy_port = _get_livy_port(
        args=args, emr_client=emr_client, emr_cluster=emr_cluster
    )

    livy_endpoint = _prepare_livy_endpoint(context, emr_cluster, int(livy_port), args)
    if kernel_name in MAGIC_KERNELS:
        return _get_magic_kernel_endpoint_magic_line(
            args=args,
            livy_endpoint=livy_endpoint,
            username=username,
            password=password,
        )

    return _get_ipython_kernel_endpoint_magic_line(
        args=args,
        livy_endpoint=livy_endpoint,
        username=username,
        password=password,
    )


def _prepare_livy_endpoint(context, emr_cluster, livy_port, args):
    # fast fail by check livy port availability. If fail, do not proceed to compose the endpoint.
    private_livy_host_name = emr_cluster.primary_node_private_dns_name()
    if check_host_and_port(private_livy_host_name, livy_port):
        livy_host_name = private_livy_host_name
    else:
        # Check public dns connectivity only if connection to private dns fails
        public_livy_host_name = emr_cluster.primary_node_public_dns_name()
        if is_blank(public_livy_host_name):
            raise LivyConnectionError(
                f"Cannot connect to livy service at {private_livy_host_name}:{livy_port}"
            )

        if check_host_and_port(public_livy_host_name, livy_port):
            # Fail if public dns is accessible but not configured to use SSL
            if not is_ssl_enabled(public_livy_host_name, livy_port):
                raise LivyConnectionError(
                    f"Livy is available at {public_livy_host_name}:{livy_port}, but not configured to use HTTPS. Please setup livy with HTTPS: https://docs.aws.amazon.com/emr/latest/ReleaseGuide/enabling-https.html"
                )
            livy_host_name = public_livy_host_name
        else:
            raise LivyConnectionError(
                f"Cannot connect to livy service at {private_livy_host_name}:{livy_port} or {public_livy_host_name}:{livy_port}"
            )

    protocol = "http"
    if is_ssl_enabled(livy_host_name, livy_port):
        protocol = "https"

        # Verify SSL Cert if asked. This will pre-emptively surface any SSLError.
        if (
            args.verify_certificate.type
            != VerifyCertificateArgument.VerifyCertificateArgumentType.IGNORE_CERT_VERIFICATION
        ):
            exc = verify_ssl_cert(livy_host_name, livy_port, args.verify_certificate)
            if exc is None:
                print("Certificate verification for HTTPS succeeded.")
            elif isinstance(exc, requests.exceptions.SSLError) or isinstance(
                exc, ssl.SSLError
            ):
                error_to_message_map = {
                    VerifyCertificateArgument.VerifyCertificateArgumentType.PATH_TO_CERT: SELF_SIGNED_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE,
                    VerifyCertificateArgument.VerifyCertificateArgumentType.PUBLIC_CA_CERT: PUBLIC_SSL_CERT_VERIFICATION_FAILURE_ERROR_MESSAGE,
                }

                print(
                    "Certificate verification for HTTPS request failed.{}. Error: [{}: {}] ".format(
                        error_to_message_map[args.verify_certificate.type],
                        exc.__class__.__name__,
                        exc,
                    )
                )

        _set_ssl_configs(args)

    context.connection_protocol = protocol
    livy_endpoint = "{0}://{1}:{2}".format(protocol, livy_host_name, livy_port)
    return livy_endpoint


def _get_livy_port(args, emr_client, emr_cluster):
    livy_port = LIVY_DEFAULT_PORT

    livy_port_from_cluster_configuration = _get_livy_port_from_cluster_configuration(
        emr_cluster=emr_cluster,
    )
    if livy_port_from_cluster_configuration:
        livy_port = livy_port_from_cluster_configuration
    # Given the logic cannot support EMR with INSTANCE_FLEET enabled. To avoid unexpected failure, check
    # InstanceCollectionType before calling logic to get livy port from instance group. This help unblock customer who
    # is using INSTANCE_FLEET but has no requirement to have custom livy port configured on instance fleet level.
    # Next step, we will add full support for livy port configured on instance fleet level.
    elif (
        _get_emr_instance_collection_type(emr_cluster) == INSTANCE_COLLECTION_TYPE_GROUP
    ):
        livy_port_from_instance_group = _get_livy_port_from_instance_group(
            emr_client=emr_client,
            args=args,
        )
        if livy_port_from_instance_group:
            livy_port = livy_port_from_instance_group
    return livy_port


def _get_emr_instance_collection_type(emr_cluster):
    """
    Get EMR instance collection type.
    The instance fleet configuration is available only in Amazon EMR versions 4.8.0 and later, excluding 5.0.x versions.
    The EMR version 5.9.0 starts to support livy which is a pre-condition to work with Studio. So we can safely assume
    the InstanceCollectionType is available.
    :param emr_cluster: EMR cluster
    :return: InstanceCollectionType with valid Values: INSTANCE_FLEET | INSTANCE_GROUP
    """
    return emr_cluster.__dict__.get("_cluster").get("InstanceCollectionType")


def _get_lock():
    """
    Handle cases when same studio user tries to connect to multiple kerberos clusters across notebooks.
    Because the krb5.conf location is same, this lock prevents async modifications to the file till one
    connection either succeeds or fails For same EMR cluster across notebooks, spark magic will hold off
    one initiating a session till the parallel session from another notebook is initiated or fails
    """
    lock = filelock.FileLock("{0}.lock".format(KRB_FILE_PATH))
    if lock.is_locked:
        sys_out_logger.debug("Lock is already acquired, waiting for 15s to check again")
        # Try to handle an unexpected kernel crash case
        sleep(15)
        # Check if lock is still locked
        if lock.is_locked:
            # Force release the lock as the kernel might have died silently
            sys_out_logger.debug(
                "Lock is still acquired after wait, trying to force release lock before attempting "
                "to acquire for processing"
            )
            lock.release(force=True)
    return lock


# IpythonWidgetBasedAuthProvider class must reside in this root file.
class IpythonWidgetBasedAuthProvider:
    """
    Class responsible for retrieving credentials needed to connect to EMR cluster.
    """

    def get_credentials_and_connect_to_cluster(
        self, context, emr_client, args, emr_cluster, kernel_name
    ):
        # If the Notebook is run in headless mode and a --secret parameter is not provided, we raise an exception to notify the same.
        if "SM_JOB_DEF_VERSION" in os.environ:
            raise MissingParametersError(
                "A --secret parameter needs to be added to run the Notebook in Headless mode"
            )
        else:
            username = widgets.Text(
                value="",
                placeholder="Username",
                description="Username:",
                disabled=False,
            )
            password = widgets.Password(
                value="",
                placeholder="Enter password",
                description="Password:",
                disabled=False,
            )
            display(username, password)
            button = widgets.Button(
                description="Connect",
                disabled=False,
                button_style="primary",
                tooltip="Connect to EMR",
                icon="",
            )
            output = widgets.Output()
            display(button, output)

            # Do not remove the unused param otherwise the button will become unresponsive
            def _on_button_clicked(b):
                with output:
                    _connect_to_cluster(
                        context=context,
                        emr_client=emr_client,
                        args=args,
                        emr_cluster=emr_cluster,
                        kernel_name=kernel_name,
                        username=username.value,
                        password=password.value,
                    )

            button.on_click(_on_button_clicked)


def _connect_to_cluster(
    context, emr_client, args, emr_cluster, kernel_name, username, password
):
    # For LDAP/HTTP authentication
    if args.auth_type == AUTH_TYPE_BASIC_ACCESS:
        _initiate_connect_based_on_kernel(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=emr_cluster,
            username=username,
            password=password,
            kernel_name=kernel_name,
        )
    # For Kerberos authentication
    else:
        # At this point lock should be available to acquire if another process has not already taken it
        # Go ahead and try to use the "with" context directly
        with _get_lock().acquire(
            # Try for 15 seconds to acquire the lock, otherwise fail with lock acquire failure
            timeout=15
        ):
            completed_process = _generate_kerberos_token(
                emr_cluster=emr_cluster,
                username=username,
                password=password,
                override_krb5_conf=args.override_krb5_conf,
            )
            if completed_process.returncode == 0:
                _initiate_connect_based_on_kernel(
                    context=context,
                    emr_client=emr_client,
                    args=args,
                    emr_cluster=emr_cluster,
                    username=None,
                    password=None,
                    kernel_name=kernel_name,
                )
            else:
                # check the kerberos principal if resetting password is required in the first place
                if "Password expired.  You must change it now." in str(
                    completed_process.stdout
                ):
                    print(
                        "\033[93mNote: You can also manually run 'kinit <principal>' command on the SparkMagic image terminal.\n      Once authenticated, you may need to restart the kernel of your notebook.\x1b[0m"
                    )
                    handle_kerberos_reset_password(username=username, password=password)
                else:
                    # check the kerberos connectivity failure
                    _handle_kerberos_connectivity_failure(
                        args=args, completed_process=completed_process
                    )


def _generate_kerberos_token(emr_cluster, username, password, override_krb5_conf=True):
    if override_krb5_conf:
        write_krb_conf(emr_cluster, KRB_FILE_PATH)
    else:
        print(
            "Using user-provided krb5.conf file. Please make sure you have an existing krb5.conf file at /etc/krb5.conf!"
        )

    cmd = ["kinit", username.encode()]
    completed_process = subprocess.run(
        cmd,
        input=password.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed_process


def _handle_kerberos_connectivity_failure(args, completed_process):
    error_message = None
    if completed_process.stderr:
        error_message = str(completed_process.stderr, "UTF-8")

    _echo_response_to_iopub_web_socket(
        _build_response(
            cluster_id=args.cluster_id,
            error_message=error_message,
            success=False,
            service="emr",
            operation="connect",
        )
    )

    if error_message:
        raise InvalidParameterError(
            "Failed to generate kerberos token using provided credentials. \n{} \n{}".format(
                error_message, str(completed_process.stdout, "UTF-8")
            )
        )


def _get_magic_kernel_endpoint_magic_line(args, livy_endpoint, username, password):
    if args.auth_type == AUTH_TYPE_BASIC_ACCESS:
        return "-s {0} -t {1} -u {2} -p {3}".format(
            livy_endpoint, args.auth_type, username, password
        )
    else:
        return "-s {0} -t {1}".format(livy_endpoint, args.auth_type)


def _get_ipython_kernel_endpoint_magic_line(args, livy_endpoint, username, password):
    # Choice of uuid generator based on: https://docs.python.org/3/library/uuid.html
    # Maintain same session name for sparkmagic session and livy session
    session_name = conf.session_configs()["name"]

    if args.auth_type == AUTH_TYPE_BASIC_ACCESS:
        return "add -s {0} -l {1} -t {2} -u {3} -a {4} -p {5}".format(
            session_name,
            args.language,
            args.auth_type,
            livy_endpoint,
            username,
            password,
        )
    else:
        return "add -s {0} -l {1} -t {2} -u {3}".format(
            session_name, args.language, args.auth_type, livy_endpoint
        )


def _get_livy_port_from_instance_group(emr_client, args):
    """
    Check if livy port is overridden as an EMR instance group override This case will happen when the describe
    cluster response does not have livy port as cluster conf but in individual instance group configuration
    """
    emr_instance_group_list = _list_instance_groups(emr_client, args.cluster_id)
    for instance_group in emr_instance_group_list:
        # TODO: Test with multi-name-node configuration to see if livy server port is set to all master nodes or not
        if instance_group["InstanceGroupType"] == "MASTER":
            instance_group_configuration_list = instance_group.get("Configurations")
            for configuration in instance_group_configuration_list:
                livy_port_override = _get_livy_port_override(configuration)
                if livy_port_override:
                    return livy_port_override


def _get_livy_port_override(configuration):
    if (
        "Classification" in configuration
        and configuration["Classification"] == "livy-conf"
        and "Properties" in configuration
    ):
        """
        There are two cases when livy port is overridden post start and on-create
        In both cases the livy port appears in different places in the describe-cluster response
        It can either be in cluster config or instance group config
        """
        livy_properties = configuration["Properties"]
        if "livy.server.port" in livy_properties:
            livy_overridden_port = livy_properties["livy.server.port"]
            return livy_overridden_port


def _ipython_kernel_connect_to_emr(
    context, emr_client, args, emr_cluster, username, password, kernel_name
):
    print("Initiating EMR connection..")

    ipy = get_ipython()
    # Depth should be 2 if run_line_magic is being called from within a magic
    ipy.run_line_magic("load_ext", "sparkmagic.magics", 2)
    endpoint_magic_line = _get_endpoint_magic_line(
        context, emr_client, args, emr_cluster, username, password, kernel_name
    )

    _handle_kerberos_endpoint_override(emr_cluster=emr_cluster)

    ipy.run_line_magic("spark", "cleanup")

    existing_all_errors_are_fatal_conf = _configure_ssl_verification_pre_session_start()
    livy_client_expected_exceptions = tuple(EXPECTED_EXCEPTIONS)
    error_message = None

    try:
        ipy.run_line_magic("spark", endpoint_magic_line)
    except livy_client_expected_exceptions as err:
        error_message = _handle_livy_client_expected_exceptions(
            err, args, existing_all_errors_are_fatal_conf
        )
    finally:
        conf.override(
            conf.all_errors_are_fatal.__name__, existing_all_errors_are_fatal_conf
        )

    session_started = False
    if error_message is None:
        # Check if session is created. Return true if sagemaker session name prefix is in '%spark info' response.
        # Sagemaker session name prefix is under control and can be used as stable contract.
        spark_info_output = io.StringIO()
        with contextlib.redirect_stdout(spark_info_output):
            ipy.run_line_magic("spark", "info")

        session_started = SPARK_SESSION_NAME_PREFIX in spark_info_output.getvalue()

        if not session_started:
            error_message = "Failed to start spark session."

    _echo_response_to_iopub_web_socket(
        _build_response(
            cluster_id=args.cluster_id,
            error_message=error_message,
            success=session_started,
            service="emr",
            operation="connect",
        )
    )


# External KDC use cases require the kerberos endpoint to be overridden
def _handle_kerberos_endpoint_override(emr_cluster):
    if emr_cluster.krb_hostname_override():
        # Kerberos endpoint is overridden
        overridden_kerberos_auth_config = {
            "mutual_authentication": REQUIRED,
            "hostname_override": emr_cluster.krb_hostname_override(),
        }

        # Override kerberos auth config with new KDC endpoint
        conf.override(
            conf.kerberos_auth_configuration.__name__, overridden_kerberos_auth_config
        )


def _set_ssl_configs(args):
    """
    Determines how to verify ssl certificate validation. If verify_certificate is set to:
    True => Certificate validation is performed with a public cert.
    False => Certificate validation is not performed
    Path-to-cert-file => Certificate validation is performed using the provided cert file.
    :param args:
    :return:
    """
    if (
        args.verify_certificate.type
        == VerifyCertificateArgument.VerifyCertificateArgumentType.PUBLIC_CA_CERT
    ):
        conf.override(conf.ignore_ssl_errors.__name__, False)
        conf.override(conf.custom_certfiles_path.__name__, None)
    elif (
        args.verify_certificate.type
        == VerifyCertificateArgument.VerifyCertificateArgumentType.IGNORE_CERT_VERIFICATION
    ):
        print(
            'WARN: Skipping SSL certificate verification because verify_certificate option is set to "False". '
            "We recommended that you enable SSL certificate verification. "
            "Please run the command %sm_analytics? for details about enabling SSL certificate verification."
        )
        conf.override(conf.ignore_ssl_errors.__name__, True)
        conf.override(conf.custom_certfiles_path.__name__, None)
    elif (
        args.verify_certificate.type
        == VerifyCertificateArgument.VerifyCertificateArgumentType.PATH_TO_CERT
    ):
        cert_file_path = args.verify_certificate.value
        if os.path.isfile(cert_file_path):
            conf.override(conf.ignore_ssl_errors.__name__, False)
            conf.override(conf.custom_certfiles_path.__name__, cert_file_path)
        else:
            raise InvalidParameterError(
                "{} path does not point to a file. Please provide a valid path. Refer to %sm_analytics? for all supported options. ".format(
                    cert_file_path
                )
            )


def _get_livy_port_from_cluster_configuration(emr_cluster):
    emr_configuration_list = emr_cluster.__dict__.get("_cluster").get("Configurations")
    # For cluster configuration
    for configuration in emr_configuration_list:
        livy_port_override = _get_livy_port_override(configuration)
        if livy_port_override:
            return livy_port_override


def _initiate_emr_connect(
    context, args, cluster, emr_client, boto_session, kernel_name
):
    _validate_cluster_auth_with_auth_type_provided(args=args, emr_cluster=cluster)

    # Please update get_auth_type_for_logging() in ../emr/auth.py when updating below branches

    # If emr execution role is passed, the EMR IAM passthrough should be used and the token API is invoked
    # to get user and password which are later used for basic auth.
    #
    # For RBAC authentication
    if args.auth_type == AUTH_TYPE_BASIC_ACCESS and args.emr_execution_role_arn:
        # Create a boto session config to append "sagemaker-analytics" to user-agent
        emr_boto_config = BotocoreConfig(
            user_agent_extra="sagemaker-analytics",
            use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT,
        )

        # Before EMR IAM Passthrough is GA, use emr-iam-passthrough-gcsc as service.
        emr_gcsc_client = boto_session.client("emr", config=emr_boto_config)

        credentials = (
            ClusterSessionCredentialsProvider().get_cluster_session_credentials(
                emr_gcsc_client, args.cluster_id, args.emr_execution_role_arn
            )
        )
        # wait for 3s for EMR token propagation
        sleep(3)

        _initiate_connect_based_on_kernel(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=cluster,
            username=credentials.username,
            password=credentials.password,
            kernel_name=kernel_name,
        )
    # For HTTP-Basic/LDAP/Kerberos authentication
    elif (
        cluster.is_krb_cluster or args.auth_type == AUTH_TYPE_BASIC_ACCESS
    ) and args.secret is None:
        auth_provider = IpythonWidgetBasedAuthProvider()
        auth_provider.get_credentials_and_connect_to_cluster(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=cluster,
            kernel_name=kernel_name,
        )
    elif (
        cluster.is_krb_cluster or args.auth_type == AUTH_TYPE_BASIC_ACCESS
    ) and args.secret is not None:
        response = _get_secret(args.secret)
        _connect_to_cluster(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=cluster,
            username=response["username"],
            password=response["password"],
            kernel_name=kernel_name,
        )
    # For no authentication
    else:
        _initiate_connect_based_on_kernel(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=cluster,
            username=None,
            password=None,
            kernel_name=kernel_name,
        )


def _set_session_name_config():
    # Define livy session name. session_configs are passed to livy api.
    session_name = f"{SPARK_SESSION_NAME_PREFIX}_{uuid4().hex}"
    session_configs = conf.session_configs()
    session_configs["name"] = session_name
    conf.override(conf.session_configs.__name__, session_configs)


def _initiate_connect_based_on_kernel(
    context, emr_client, args, emr_cluster, username, password, kernel_name
):
    _set_session_name_config()

    # EMR clusters after version 6.6 take ~90s for livy connection to establish.
    # If customer did not specify default timeout, increase timeout to 120s to enable connections.
    # TODO: Remove after Livy sessions on EMR can be established in under 60s.
    existing_session_startup_timeout = conf.livy_session_startup_timeout_seconds()
    if existing_session_startup_timeout == 60:
        conf.override(conf.livy_session_startup_timeout_seconds.__name__, 120)

    _set_logging_config()

    if kernel_name in MAGIC_KERNELS:
        _magic_kernel_connect_to_emr(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=emr_cluster,
            username=username,
            password=password,
            kernel_name=kernel_name,
        )

    elif kernel_name == IPYTHON_KERNEL:
        _ipython_kernel_connect_to_emr(
            context=context,
            emr_client=emr_client,
            args=args,
            emr_cluster=emr_cluster,
            username=username,
            password=password,
            kernel_name=kernel_name,
        )


def _set_logging_config() -> None:
    """
    Sets `disable_existing_loggers` key on the dictconfig config used by sparkmagic to create loggers. By default,
    loading a logger via `logging.config.dictConfig` disables all existing loggers, including our loggers. python
    doc: https://docs.python.org/3/library/logging.config.html sparkmagic ref:
    https://github.com/jupyter-incubator/sparkmagic/blob/master/hdijupyterutils/hdijupyterutils/log.py#L13

    :return: None
    """
    logging_config = conf.logging_config()
    logging_config["disable_existing_loggers"] = False
    conf.override(conf.logging_config.__name__, logging_config)


def _validate_cluster_auth_with_auth_type_provided(args, emr_cluster):
    is_cluster_kerberos_authenticated = emr_cluster.is_krb_cluster
    is_cluster_ldap_authenticated = ClusterAuthUtils.is_cluster_ldap(emr_cluster)
    is_cluster_no_auth = (
        not is_cluster_ldap_authenticated and not is_cluster_kerberos_authenticated
    )
    auth_type = args.auth_type

    if (
        (auth_type == AUTH_TYPE_NONE and is_cluster_kerberos_authenticated)
        or (auth_type == AUTH_TYPE_NONE and is_cluster_ldap_authenticated)
        or (auth_type == AUTH_TYPE_KERBEROS and is_cluster_ldap_authenticated)
        or (auth_type == AUTH_TYPE_KERBEROS and is_cluster_no_auth)
    ):
        raise InvalidParameterError(
            "Cluster auth type does not match provided auth {}".format(auth_type)
        )

    if (not args.override_krb5_conf) and (auth_type != AUTH_TYPE_KERBEROS):
        raise InvalidParameterError(
            "--no-override-krb5-conf key is only for Kerberos cluster"
        )


def _check_required_args(args, usage):
    if args is None or args.command is None or len(args.command) != 2:
        raise MissingParametersError(
            "Please provide service name and operation to perform. {}".format(usage)
        )


@magics_class
class SagemakerAnalytics(Magics):
    @line_magic
    @magic_arguments()
    @argument(
        "command",
        type=str,
        default=[""],
        nargs="*",
        help="Command to execute. The command consists of a service name followed by a ' ' followed by an operation. "
        "Supported services are {0} and supported operations are {1}. For example a valid command is '{2}'.".format(
            SERVICE.list(), ["connect", "help"], "emr connect"
        ),
    )
    @argument(
        "--auth-type",
        type=str,
        default=None,
        help="The authentication type to be used. Supported authentication types are {0}.".format(
            AUTH_TYPE_SET
        ),
    )
    @argument(
        "--application-id",
        type=str,
        default=None,
        help="The EMR Serverless Application to connect to",
    )
    @argument(
        "--cluster-id",
        type=str,
        default=None,
        help="The cluster id to connect to.",
    )
    @argument(
        "--language",
        type=str,
        default=None,
        help="Language to use. The supported languages for IPython kernel(s) are {0}. This is a required "
        "argument for IPython kernels, but not for magic kernels such as PySpark or SparkScala.".format(
            LANGUAGES_SUPPORTED
        ),
    )
    @argument(
        "--assumable-role-arn",
        type=str,
        default=None,
        help="The IAM role to assume when connecting to a cluster in a different AWS account. This argument is not "
        "required when connecting to a cluster in the same AWS account.",
    )
    @argument(
        "--emr-execution-role-arn",
        type=str,
        default=None,
        help="The IAM role passed to EMR to set up EMR job security context. This argument is optional and "
        "used when IAM Passthrough feature is enabled for EMR.",
    )
    @argument(
        "--secret",
        type=str,
        default=None,
        help="The AWS Secrets Manager SecretID.",
    )
    @argument(
        "--verify-certificate",
        type=str,
        default="False",
        help="Determine if SSL certificate should be verified when using HTTPS to connect to EMR. Supported values are {0}. "
        "If a PathToCert is provided, the certificate verification will be done using the certificate in the provided file path. "
        "For public CA issued certificates, enable the certificate validation by setting the parameter as true. "
        "Alternatively, you can disable the certificate validation by setting the parameter as false.".format(
            VerifyCertificateArgument.VerifyCertificateArgumentType.list()
        ),
    )
    @argument(
        "--override-krb5-conf",
        type=bool,
        default=True,
        action=argparse.BooleanOptionalAction,
        help="This input only works when the cluster is a Kerberos cluster. Supported values are [True, False]."
        "If you want to set it as True, simply add --override-krb5-conf to the end of command with no input value."
        "If you want to set it as False, simply add --no-override-krb5-conf to the end of command with no input value."
        "Default value is True. If set to False, SageMaker will not generate and use krb5.conf file provided by user."
        "User should make sure there is existing krb5.conf file at /etc/krb5.conf",
    )
    def sm_analytics(self, line):
        """
        This is a notebook extension provided by AWS SageMaker Studio Team to integrate with analytics resources.
        Currently, it supports connecting SageMaker Studio Notebook to EMR clusters and EMR Serverless Applications
        through the SparkMagic library.

        Services currently supported: emr, emr-serverless
        Please look at usage of %sm_analytics by executing `%sm_analytics <SERVICE_NAME> help`
        Example:
        %sm_analytics emr help
        %sm_analytics emr-serverless help
        """
        usage = SM_ANALYTICS_USAGE
        user_input = line
        args = parse_argstring(self.sm_analytics, user_input)

        _check_required_args(args, usage)

        service = args.command[0].lower()
        operation = args.command[1].lower()

        """
        Magic argument parser, unlike python's argparse, doesn't remove quotation marks. Please sanitize input as needed.
        https://github.com/ipython/ipython/issues/2001
        """
        args.verify_certificate = unquote_ends(args.verify_certificate)

        args.verify_certificate = VerifyCertificateArgument(args.verify_certificate)

        global sagemaker_analytics_service_logger
        try:
            kernel_name = type(IPython.Application.instance().kernel).__name__
        except Exception as e:
            _echo_response_to_iopub_web_socket(
                _build_response(
                    cluster_id=args.cluster_id,
                    error_message=str(e),
                    success=False,
                    service=service,
                    operation=operation,
                )
            )
            raise e

        # emr
        if service == SERVICE.EMR:
            if operation == OPERATION.CONNECT:
                sagemaker_analytics_service_logger = ServiceFileLogger(
                    EMR_CONNECTION_LOG_FILE,
                    SAGEMAKER_ANALYTICS_LOG_BASE_DIRECTORY,
                    sys_out_logger,
                )

                EMRValidator.validate_emr_args(
                    args=args, usage=usage, kernel_name=kernel_name
                )
                # Only create boto session if absolutely needed
                boto_session = get_boto3_session(args.assumable_role_arn)
                emr_client = get_emr_client(boto_session)

                # Even if assumable role arn is None, we can pass it to the EMRCluster constructor and will be handled
                # by get_boto3_session method call gracefully. So no need to do a explicit None check here.
                cluster = EMRCluster(
                    cluster_id=args.cluster_id,
                    role_arn=args.assumable_role_arn,
                    emr=emr_client,
                )

                context = MagicExecutionContext()

                _connect_to_emr(
                    context=context,
                    service=service,
                    operation=operation,
                    args=args,
                    cluster=cluster,
                    emr_client=emr_client,
                    boto_session=boto_session,
                    kernel_name=kernel_name,
                    service_logger=sagemaker_analytics_service_logger,
                )
            elif operation == OPERATION.HELP:
                print(EMR_CLUSTER_HELP)

            else:
                raise InvalidParameterError(
                    "Operation '{}' not found. {}".format(operation, usage)
                )
        # emr serverless
        elif service == SERVICE.EMR_SERVERLESS:
            if operation == OPERATION.CONNECT:
                sagemaker_analytics_service_logger = ServiceFileLogger(
                    EMR_CONNECTION_LOG_FILE,
                    SAGEMAKER_ANALYTICS_LOG_BASE_DIRECTORY,
                    sys_out_logger,
                )
                context = MagicExecutionContext()
                EMRServerlessValidator.validate_args_for_emr_serverless(
                    args, usage, kernel_name
                )
                _set_session_name_config()
                _set_logging_config()
                emr_serverless_magic_utils = EMRServerlessMagicUtils(
                    args, kernel_name, conf.session_configs()["name"]
                )
                emr_serverless_magic_utils.connect_to_emr_serverless_application(
                    kernel_name=kernel_name,
                    args=args,
                    service=service,
                    operation=operation,
                    session_name=conf.session_configs()["name"],
                    service_logger=sagemaker_analytics_service_logger,
                    context=context,
                )
            elif operation == OPERATION.HELP:
                print(EMR_SERVERLESS_HELP)
            else:
                raise InvalidParameterError(
                    "Operation '{}' not found. {}".format(operation, usage)
                )

        else:
            raise InvalidParameterError(
                "Service '{}' not found. {}".format(service, usage)
            )


@records_service_metrics
def _connect_to_emr(
    context,
    service,
    operation,
    args,
    cluster,
    emr_client,
    boto_session,
    kernel_name,
    service_logger,
):
    try:
        _initiate_emr_connect(
            context=context,
            args=args,
            cluster=cluster,
            emr_client=emr_client,
            boto_session=boto_session,
            kernel_name=kernel_name,
        )
    except Exception as e:
        error_msg = str(e)
        if isinstance(e, EndpointConnectionError):
            error_msg = "{}. Please check your network settings or contact support for assistance.".format(
                str(e)
            )
        _echo_response_to_iopub_web_socket(
            _build_response(
                cluster_id=args.cluster_id,
                error_message=error_msg,
                success=False,
                service=service,
                operation=operation,
            )
        )
        raise e


# In order to actually use these magics, you must register them with a
# running IPython.
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    auto-loaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(SagemakerAnalytics)


def _list_instance_groups(emr_client, cluster_id):
    try:
        emr_instance_group_list = []
        paginator = emr_client.get_paginator("list_instance_groups")
        operation_parameters = {"ClusterId": cluster_id}
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            emr_instance_group_list.extend(page["InstanceGroups"])
    except botocore.exceptions.EndpointConnectionError as e:
        sys_out_logger.error("{} {}".format(str(e), traceback.format_exc()))
        # TODO: exact error message to be updated after PM sign off.
        raise ConnectionError(
            "{}. Please check your network settings or contact support for assistance.".format(
                str(e)
            )
        )
    except botocore.exceptions.ClientError as ce:
        sys_out_logger.error(
            "Failed to list instance groups for EMR cluster({0}). {1}".format(
                cluster_id, ce.response
            )
        )
        raise InvalidConfigError(
            "Unable to list instance groups for EMR cluster(Id: {0}) using ListInstanceGroups API. Error: {1}".format(
                cluster_id, ce.response["Error"]
            )
        ) from None
    return emr_instance_group_list


def _echo_response_to_iopub_web_socket(response):
    print(json.dumps(response))


def _build_response(cluster_id, error_message, success, service, operation):
    return {
        "namespace": LIBRARY_NAME,
        "cluster_id": cluster_id,
        "error_message": error_message,
        "success": success,
        "service": service,
        "operation": operation,
    }


def _get_secret(secret_id):
    # Create a Secrets Manager client
    session = get_boto3_session()
    cfg = botocore.client.Config(
        use_dualstack_endpoint=USE_DUALSTACK_ENDPOINT,
    )
    client = session.client(
        service_name="secretsmanager",
        region_name=session.region_name,
        config=cfg,
    )
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_id)
    except botocore.exceptions.EndpointConnectionError as e:
        sys_out_logger.error("{} {}".format(str(e), traceback.format_exc()))
        # TODO: exact error message to be updated after PM sign off.
        raise ConnectionError(
            "{}. Please check your network settings or contact support for assistance.".format(
                str(e)
            )
        )
    except ClientError as e:
        sys_out_logger.error(
            "Error while fetching secrets from secret manager : {}".format(e)
        )
        raise e
    else:
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])
    return json.loads(secret)
