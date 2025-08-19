# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import Union

import requests
import socket
from ssl import get_server_certificate, SSLError

from sagemaker_studio_analytics_extension.utils.string_utils import *

from sagemaker_studio_analytics_extension.utils.constants import (
    VerifyCertificateArgument,
)


def check_host_and_port(host, port):
    """
    Check if the port is alive for designated host.
    :param host: host name
    :param port: port to check
    :return: True or False indicate if port is alive
    """

    if is_blank(host):
        print(f"[Error] Host must not be empty.")
        return False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # timeout as 5 seconds
        sock.settimeout(5)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                return True
            else:
                # when connect_ex return an error indicator instead of raising an exception for errors,
                # print the information and it will be displayed in cell output when used in notebook.
                print(
                    f"Host: {host} port: {port} is not connectible via socket with {result} returned."
                )
                return False
        except OSError as msg:
            # use print directly as for jupyter env the error message will displayed in cell output
            print(
                f"[Error] Failed to check host and port [{host}:{port}]. Error message: {msg}"
            )

            return False


def is_ssl_enabled(host, port):
    """
    Check if the host/port is SSL enabled.
    :param host: host name
    :param port: port to check
    :return: True or False indicate if SSL is enabled or not
    """
    try:
        cert = get_server_certificate((host, port))
        return cert is not None
    except SSLError:
        # only return false for SSL error, propagate other types of errors
        return False


def verify_ssl_cert(
    host, port, cert_arg: VerifyCertificateArgument
) -> Union[Exception, None]:
    """
    Attempts to connect to the https://host:port using provided cert to verify that cert is valid. This will check SSL
    certificate verification success, or fail with the following:

    If a PathToCert is provided, we expect to get the following exceptions:
    1. SSLError -- If we could not connect to the host:port via SSL
    2. OSError -- If the provided path is invalid

    :param host:
    :param port:
    :param cert_arg:    VerifyCertificateArgument | Value can be True (Use public cert) / False (Do not validate cert) / PathToCert (Path to local cert)
    :return:
    """

    try:
        requests.get("https://{}:{}".format(host, port), verify=cert_arg.value)
    except (SSLError, requests.exceptions.SSLError, OSError, Exception) as e:
        """
        Also catch generic "Exception" so that this code path doesn't fail execution. Most likely, the same Exception will
        also be raised when we try to actually connect to execute the connection to given host:port. Relegate failure to that code path.
        """
        return e

    return None
