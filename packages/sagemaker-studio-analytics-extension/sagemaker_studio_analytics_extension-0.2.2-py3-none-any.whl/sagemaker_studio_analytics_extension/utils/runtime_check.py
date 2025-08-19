# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import json
from importlib.util import find_spec


def main():
    """
    Entry method for Astra related runtime checking. The check is to provide meta info on the runtime kernel image for
    Studio UI for conditional logic e.g. enable the EMR connection function when the kernel image is Astra EMR function
    compatible.
    """
    # This naming space is contract for UI to filter in the relevant websocket messages.
    runtime = {
        "namespace": "sagemaker-analytics",
        "emr": {"compatible": check_emr_runtime()},
    }

    # The response will be printed into stdout and Studio gets the reponse through monitor the jupyter message channel.
    print(json.dumps(runtime), end="")


def check_emr_runtime():
    """
    Check required libraries for EMR connection function. The dependencies like pyhive, kinit(kerberos case) are
    not always required and will not be checked for compatibility determination. This enables the Bring Your Own
    image case to only install required packages.
    """
    # Check sparkmagic and dependencies.
    modules = ["sparkmagic", "sagemaker_studio_sparkmagic_lib"]
    return check_modules(modules)


def check_modules(modules):
    """
    Check if all modules are available in the python runtime. Return true only when all the modules can be found.
    """
    for module in modules:
        if not _check_module(module):
            return False
    return True


def _check_module(name):
    spec = find_spec(name)
    return spec is not None


if __name__ == "__main__":
    main()
